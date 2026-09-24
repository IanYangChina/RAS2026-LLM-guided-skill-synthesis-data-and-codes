## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1703 | 0.00 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.170) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.170
- **task_score** (E): 0.000
- **fitness_score**: 0.110  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_peg | 1.00 | 0.1772 |
| descend_behind | 1.00 | 0.0887 |
| push_through_channel | 0.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.131, 0.141) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 |
| descend_behind | align | 1.00 / step_budget | (0.493, 0.131, 0.141)→(0.496, 0.117, 0.056) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |
| push_through_channel | push | 0.00 / guard_failure | (0.496, 0.117, 0.056)→(0.495, 0.117, 0.056) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- terminal_score: 0.001
- phase_score: 0.208
- phase_breakdown.pre_push_score: 0.692
- phase_breakdown.final_push_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.125
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.174
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.333


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02985,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_y_offset":0.0516,"approach_peg.approach_z_offset":0.07866,"descend_behind.descend_y_offset":0.04605,"push_through_channel.push_speed":0.04743,"push_through_channel.push_tolerance":0.01634},"optimized_scores":{"best_composite_score":-0.15504,"best_fitness_score":0.12496,"best_task_score":0.00075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.49096,0.17379,-0.00058],"force_p95":386.96062,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":432.34425,"mean_force":305.69903,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48923,0.11285,0.05432]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49135,0.17378,-0.00025],"force_p95":140.10583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.69388,"mean_force":99.89336,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.489,0.11436,0.05662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.49552,0.06376,0.00936],"force_p95":0.62624,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56952,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48446,0.1719,0.20858]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50382,0.21519,0.29262]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.49499,0.06419,0.0094],"force_p95":0.55001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55112,"mean_force":0.54577,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48511,0.11723,0.08908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49375,0.04641,0.0094],"force_p95":0.54293,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54312,"mean_force":0.54182,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.489,0.11436,0.05662]}],"total_contact_groups":6},"final_pose_error":0.03976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4952,0.06369,0.03395],"final_tcp_position":[0.4889,0.11425,0.05687],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.49527,0.06381,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14402,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.48125,0.12455,0.13607],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11967,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":237.0,"n_steps_budget":660.0,"object_pos_end":[0.49502,0.06367,0.03395],"object_pos_start":[0.49527,0.06381,0.03392],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14402,"object_z_max":0.03395,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48906,0.1144,0.05648],"tcp_start":[0.48125,0.12455,0.13607],"tcp_to_object_dist_end":0.05583,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.49508,0.06366,0.03395],"object_pos_start":[0.49502,0.06367,0.03395],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14388,"object_z_max":0.03395,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.4889,0.11425,0.05687],"tcp_start":[0.48893,0.11431,0.05676],"tcp_to_object_dist_end":0.05588,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02899,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_y_offset":0.04511,"approach_peg.approach_z_offset":0.12439,"descend_behind.descend_y_offset":0.04686,"push_through_channel.push_speed":0.03701,"push_through_channel.push_tolerance":0.02678},"optimized_scores":{"best_composite_score":-0.1744,"best_fitness_score":0.1056,"best_task_score":0.00019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.48989,0.16813,-0.00064],"force_p95":388.86164,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":433.08319,"mean_force":306.01025,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48812,0.10723,0.05425]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49026,0.16814,-0.00028],"force_p95":134.04275,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.23504,"mean_force":100.96135,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48789,0.1088,0.05663]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47492,0.12,0.05996],"force_p95":125.54665,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.86519,"mean_force":108.75138,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48584,0.10707,0.06472]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.49459,0.05884,0.00933],"force_p95":0.63279,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59478,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.47826,0.16987,0.22629]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50179,0.22019,0.28674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.49418,0.05919,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.5462,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.47887,0.11076,0.11029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47711,0.05733,0.00939],"force_p95":0.54912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54918,"mean_force":0.54818,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48789,0.1088,0.05663]}],"total_contact_groups":7},"final_pose_error":0.03547,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49403,0.05885,0.03389],"final_tcp_position":[0.48778,0.10869,0.0569],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05898,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.46992,0.11675,0.17891],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15802,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":347.0,"n_steps_budget":930.0,"object_pos_end":[0.49399,0.059,0.03389],"object_pos_start":[0.49422,0.05898,0.03385],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.13924,"object_z_max":0.03389,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48796,0.10884,0.05647],"tcp_start":[0.46992,0.11675,0.17891],"tcp_to_object_dist_end":0.05505,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":630.0,"object_pos_end":[0.49398,0.05895,0.03389],"object_pos_start":[0.49399,0.059,0.03389],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.13926,"object_z_max":0.03389,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.48778,0.10869,0.0569],"tcp_start":[0.48782,0.10875,0.05678],"tcp_to_object_dist_end":0.05517,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98529,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_y_offset":0.06547,"approach_peg.approach_z_offset":0.05025,"descend_behind.descend_y_offset":0.03565,"push_through_channel.push_speed":0.04308,"push_through_channel.push_tolerance":0.03255},"optimized_scores":{"best_composite_score":-0.18145,"best_fitness_score":0.09855,"best_task_score":9e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.51209,0.18802,-0.00043],"force_p95":276.18768,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.222,"mean_force":264.34699,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.51017,0.12649,0.05398]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.51238,0.18797,-9e-05],"force_p95":100.41372,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.2721,"mean_force":76.03557,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50974,0.12696,0.05521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":392.0,"contact_point_centroid":[0.50564,0.08091,0.00935],"force_p95":0.56157,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58569,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50713,0.18263,0.1966]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50333,0.22172,0.28679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":195.0,"contact_point_centroid":[0.50582,0.08077,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.51697,0.13526,0.07303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5166,0.0872,0.00938],"force_p95":0.54967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54692,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50974,0.12696,0.05521]}],"total_contact_groups":6},"final_pose_error":0.05031,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.08086,0.03378],"final_tcp_position":[0.5098,0.12695,0.0552],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.52904,0.151,0.10832],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10492,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50971,0.12696,0.0552],"tcp_start":[0.52904,0.151,0.10832],"tcp_to_object_dist_end":0.05094,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":750.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.5098,0.12695,0.0552],"tcp_start":[0.50977,0.12696,0.05521],"tcp_to_object_dist_end":0.05094,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```