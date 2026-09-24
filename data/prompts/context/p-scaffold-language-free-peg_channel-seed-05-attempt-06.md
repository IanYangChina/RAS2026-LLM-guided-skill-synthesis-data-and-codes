## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.3054 | 0.07 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0667 | 0.62 | ❌ rejected |
| 4 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | -0.3500 | 0.13 | ❌ rejected |
| 3 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.0923 | 0.25 | ❌ rejected |
| 2 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 10 | -0.0961 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.07 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=-0.305) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.305
- **task_score** (E): 0.069
- **fitness_score**: 0.035  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_peg | 0.00 | 1.00 | 0.1201 |
| descend_to_peg | 0.00 | 1.00 | 0.0293 |
| make_contact | 1.00 | 1.00 | 0.0001 |
| push_through_channel | 0.00 | 1.00 | 0.0004 |
| retract_from_channel | 0.67 | 1.00 | 0.0981 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_peg | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.531, 0.098, 0.275) | (0.512, 0.095, 0.040)→(0.505, 0.093, 0.033) | 0.175→0.174 | 1.00 / 2.333 | 454.502 | 1283.017 |
| descend_to_peg | approach | 0.00 / step_budget | (0.531, 0.098, 0.275)→(0.516, 0.098, 0.254) | (0.505, 0.093, 0.033)→(0.506, 0.084, 0.034) | 0.174→0.164 | 1.00 / 2.667 | 306.164 | 583.524 |
| make_contact | contact | 1.00 / force_exceeded | (0.516, 0.098, 0.254)→(0.516, 0.098, 0.254) | (0.506, 0.084, 0.034)→(0.506, 0.084, 0.034) | 0.164→0.164 | 1.00 / 2.667 | 1380.001 | 226.861 |
| push_through_channel | push | 0.00 / guard_failure | (0.517, 0.098, 0.254)→(0.517, 0.097, 0.254) | (0.506, 0.084, 0.034)→(0.506, 0.084, 0.034) | 0.164→0.164 | 1.00 / 2.333 | 233.511 | 402.891 |
| retract_from_channel | retract | 0.67 / step_budget | (0.517, 0.097, 0.254)→(0.516, 0.097, 0.352) | (0.506, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.164 | 1.00 / 1.000 | 0.548 | 287.459 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.206
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.206
- phase_score: 0.010
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_peg_score: 0.036
- phase_breakdown.contact_peg_score: 0.008

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.088
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.206
- **Median Q (composite search score)**: -0.332
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98333,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.height_offset":0.05039,"align_to_peg.speed":0.11723,"descend_to_peg.pre_contact_height":0.01543,"make_contact.force_threshold":7.80906,"make_contact.probe_distance":0.03455,"push_through_channel.push_distance":0.18975,"push_through_channel.speed":0.03783,"retract_from_channel.retract_height":0.11816,"retract_from_channel.speed":0.06247},"optimized_scores":{"best_composite_score":-0.33208,"best_fitness_score":0.00792,"best_task_score":9e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":682.0,"contact_point_centroid":[0.54784,0.0878,0.0597],"force_p95":552.95582,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1369.49297,"mean_force":440.71755,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.58858,0.19614,0.22458]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":946.0,"contact_point_centroid":[0.55497,0.04598,0.05992],"force_p95":392.4724,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":515.17077,"mean_force":318.36147,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.56403,0.11042,0.26297]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.55499,0.04375,0.05999],"force_p95":360.69937,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":378.21707,"mean_force":162.46377,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.56319,0.10785,0.24522]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.55497,0.04436,0.05998],"force_p95":342.66811,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.79084,"mean_force":341.82255,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.56284,0.10903,0.24463]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55499,0.04437,0.05999],"force_p95":171.04177,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.04177,"mean_force":171.04177,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.56278,0.10919,0.24465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50549,0.10518,0.0094],"force_p95":0.69702,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.18331,"mean_force":0.59517,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.58245,0.19372,0.22239]},{"body_a":"peg","body_b":"link6","contact_count":38.0,"contact_point_centroid":[0.52164,0.10569,0.05646],"force_p95":5.16807,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.79309,"mean_force":0.90357,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.43719,0.25636,0.13667]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.50157,0.19412,0.28326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50585,0.10461,0.00939],"force_p95":0.56329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58967,"mean_force":0.54616,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.56246,0.10839,0.29471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50584,0.10464,0.00939],"force_p95":0.55996,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56287,"mean_force":0.54644,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.56398,0.11041,0.26285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49045,0.10935,0.00938],"force_p95":0.56069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5618,"mean_force":0.55163,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.56284,0.10903,0.24463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51731,0.11777,0.00939],"force_p95":0.5423,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54282,"mean_force":0.53758,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.56276,0.10917,0.24469]}],"total_contact_groups":12},"final_pose_error":0.01643,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50585,0.10461,0.0338],"final_tcp_position":[0.56292,0.10842,0.34647],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1369.49297,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.10467,0.0338],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":382.01283,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1597.0,"raw_peak_contact_force":1369.49297,"subtask_id":"reach_peg","tcp_end":[0.57133,0.10916,0.27114],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24624,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.10467,0.0338],"object_pos_start":[0.50585,0.10467,0.0338],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18486,"object_z_max":0.0338,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1946.0,"raw_peak_contact_force":515.17077,"subtask_id":"contact_peg","tcp_end":[0.56275,0.10915,0.24472],"tcp_start":[0.57133,0.10916,0.27114],"tcp_to_object_dist_end":0.21851,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.5058,0.10468,0.0338],"object_pos_start":[0.50585,0.10467,0.0338],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18487,"object_z_max":0.0338,"peak_contact_force":171.04177,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":171.04177,"subtask_id":"contact_peg","tcp_end":[0.56277,0.10917,0.24461],"tcp_start":[0.56275,0.10915,0.24472],"tcp_to_object_dist_end":0.21842,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50578,0.10466,0.0338],"object_pos_start":[0.5058,0.10468,0.0338],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18487,"object_z_max":0.0338,"peak_contact_force":342.79084,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":342.79084,"subtask_id":"push_to_goal","tcp_end":[0.56311,0.10853,0.24474],"tcp_start":[0.56293,0.10885,0.24466],"tcp_to_object_dist_end":0.21863,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.10461,0.0338],"object_pos_start":[0.50579,0.10461,0.0338],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18481,"object_z_max":0.03383,"peak_contact_force":0.53425,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1008.0,"raw_peak_contact_force":378.21707,"tcp_end":[0.56292,0.10842,0.34647],"tcp_start":[0.56311,0.10853,0.24474],"tcp_to_object_dist_end":0.31785,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11404,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.height_offset":0.13538,"align_to_peg.speed":0.12407,"descend_to_peg.pre_contact_height":0.02172,"make_contact.force_threshold":3.04099,"make_contact.probe_distance":0.03236,"push_through_channel.push_distance":0.15416,"push_through_channel.speed":0.03424,"retract_from_channel.retract_height":0.16361,"retract_from_channel.speed":0.05625},"optimized_scores":{"best_composite_score":-0.25177,"best_fitness_score":0.08823,"best_task_score":0.20594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":603.0,"contact_point_centroid":[0.52507,0.08907,0.05983],"force_p95":664.22325,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1041.83924,"mean_force":600.35313,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.50504,0.14771,0.26403]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":23.0,"contact_point_centroid":[0.47434,0.11331,0.05871],"force_p95":626.15369,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":787.26878,"mean_force":403.97873,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.4269,0.2275,0.17587]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.52505,0.07087,0.0599],"force_p95":657.97984,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":676.88932,"mean_force":599.00215,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.43992,0.07299,0.27316]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.52503,0.06983,0.05992],"force_p95":509.98904,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.1333,"mean_force":471.15221,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.43166,0.0672,0.27021]},{"body_a":"peg","body_b":"link6","contact_count":407.0,"contact_point_centroid":[0.50309,0.08008,0.05811],"force_p95":79.5748,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":248.62828,"mean_force":49.94907,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.48853,0.12284,0.26903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.50298,0.07335,0.00935],"force_p95":69.02537,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":217.9758,"mean_force":29.16571,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.49918,0.15286,0.25488]},{"body_a":"peg","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.50145,0.0646,0.05645],"force_p95":102.55803,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.32448,"mean_force":61.08825,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.43997,0.07298,0.27318]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":593.0,"contact_point_centroid":[0.475,0.09472,0.06],"force_p95":117.14523,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.84029,"mean_force":63.73328,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.43549,0.07288,0.27164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50583,0.05662,0.0088],"force_p95":99.17873,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.95604,"mean_force":60.0848,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.43997,0.07298,0.27318]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52505,0.06968,0.05988],"force_p95":144.12361,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.12361,"mean_force":144.12361,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.43167,0.06737,0.27012]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":301.0,"contact_point_centroid":[0.52525,0.06783,0.04809],"force_p95":18.46121,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.82816,"mean_force":8.42754,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.49743,0.09957,0.28469]},{"body_a":"peg","body_b":"link6","contact_count":25.0,"contact_point_centroid":[0.5046,0.05191,0.05992],"force_p95":86.24867,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.22486,"mean_force":11.1982,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.43125,0.06554,0.27116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5061,0.03425,0.00941],"force_p95":0.56378,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.18466,"mean_force":0.81546,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.43109,0.07035,0.31766]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":992.0,"contact_point_centroid":[0.52548,0.04846,0.02938],"force_p95":20.88744,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.40295,"mean_force":9.87254,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.43979,0.07301,0.27312]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.47499,0.09608,0.06],"force_p95":62.92716,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.92716,"mean_force":62.92716,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.43167,0.06737,0.27012]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52514,0.03548,0.02793],"force_p95":23.83278,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.61055,"mean_force":6.13557,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.43117,0.06623,0.27171]}],"total_contact_groups":23},"final_pose_error":0.05916,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50629,0.03451,0.03386],"final_tcp_position":[0.43142,0.0662,0.3749],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3919.07037,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":711.0,"n_steps_budget":930.0,"object_pos_end":[0.50693,0.06351,0.03223],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":598.641,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2040.0,"raw_peak_contact_force":1041.83924,"subtask_id":"reach_peg","tcp_end":[0.46316,0.06965,0.28082],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25249,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50762,0.03605,0.03423],"object_pos_start":[0.50693,0.06351,0.03223],"object_to_goal_dist_end":0.11645,"object_to_goal_dist_start":0.14389,"object_z_max":0.03422,"peak_contact_force":664.47778,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4582.0,"raw_peak_contact_force":676.88932,"subtask_id":"contact_peg","tcp_end":[0.43167,0.06737,0.27012],"tcp_start":[0.46316,0.06965,0.28082],"tcp_to_object_dist_end":0.24979,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50761,0.03604,0.03423],"object_pos_start":[0.50762,0.03605,0.03423],"object_to_goal_dist_end":0.11643,"object_to_goal_dist_start":0.11645,"object_z_max":0.03423,"peak_contact_force":3919.07037,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":144.12361,"subtask_id":"contact_peg","tcp_end":[0.43169,0.0674,0.27014],"tcp_start":[0.43167,0.06737,0.27012],"tcp_to_object_dist_end":0.2498,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50761,0.03603,0.03424],"object_pos_start":[0.50761,0.03604,0.03423],"object_to_goal_dist_end":0.11642,"object_to_goal_dist_start":0.11643,"object_z_max":0.03425,"peak_contact_force":10.68889,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":514.1333,"subtask_id":"push_to_goal","tcp_end":[0.43156,0.06649,0.27044],"tcp_start":[0.43163,0.06695,0.2703],"tcp_to_object_dist_end":0.25,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,0.03451,0.03386],"object_pos_start":[0.50759,0.03603,0.03426],"object_to_goal_dist_end":0.11485,"object_to_goal_dist_start":0.11642,"object_z_max":0.03531,"peak_contact_force":0.54323,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1036.0,"raw_peak_contact_force":117.22486,"tcp_end":[0.43142,0.0662,0.3749],"tcp_start":[0.43156,0.06649,0.27044],"tcp_to_object_dist_end":0.35059,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15315,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_peg.height_offset":0.05266,"align_to_peg.speed":0.09842,"descend_to_peg.pre_contact_height":0.02953,"make_contact.force_threshold":8.13569,"make_contact.probe_distance":0.0477,"push_through_channel.push_distance":0.17572,"push_through_channel.speed":0.04536,"retract_from_channel.retract_height":0.10078,"retract_from_channel.speed":0.09882},"optimized_scores":{"best_composite_score":-0.33239,"best_fitness_score":0.00761,"best_task_score":0.00055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":759.0,"contact_point_centroid":[0.54786,0.08854,0.05973],"force_p95":533.83865,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1437.71938,"mean_force":422.69746,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.5872,0.19989,0.22262]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":942.0,"contact_point_centroid":[0.55498,0.05687,0.05993],"force_p95":426.12261,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":558.51333,"mean_force":341.49703,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.55295,0.11799,0.26461]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.55496,0.05232,0.05996],"force_p95":359.38631,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":366.93432,"mean_force":287.73873,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.55536,0.11683,0.24739]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.55498,0.05225,0.05998],"force_p95":349.64114,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.41753,"mean_force":207.65358,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.55492,0.11757,0.24705]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.55494,0.0523,0.05994],"force_p95":351.44421,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.74873,"mean_force":349.1686,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.55496,0.11744,0.24708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":914.0,"contact_point_centroid":[0.50386,0.11189,0.00936],"force_p95":0.6223,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55852,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.58084,0.19794,0.22077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50365,0.11167,0.00942],"force_p95":0.59511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63246,"mean_force":0.54328,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.55294,0.11798,0.26447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50366,0.11162,0.00942],"force_p95":0.59005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63001,"mean_force":0.54317,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.55463,0.11689,0.28986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50775,0.12,0.00943],"force_p95":0.55831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55931,"mean_force":0.55033,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.55496,0.11744,0.24708]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.50137,0.19827,0.29674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51048,0.1016,0.00944],"force_p95":0.54009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54074,"mean_force":0.52791,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.55494,0.11758,0.24707]},{"body_a":"peg","body_b":"link6","contact_count":31.0,"contact_point_centroid":[0.51857,0.11275,0.05565],"force_p95":0.45814,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4699,"mean_force":0.1459,"phase_index":0.0,"phase_name":"align_to_peg","phase_type":"approach","tcp_position_centroid":[0.42524,0.25114,0.12212]}],"total_contact_groups":12},"final_pose_error":0.01277,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5037,0.11168,0.03392],"final_tcp_position":[0.55496,0.11691,0.3353],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1437.71938,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.03376],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":382.8532,"phase_name":"align_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1720.0,"raw_peak_contact_force":1437.71938,"subtask_id":"reach_peg","tcp_end":[0.55794,0.1165,0.2736],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24594,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11174,0.03388],"object_pos_start":[0.50371,0.11177,0.03376],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19191,"object_z_max":0.03397,"peak_contact_force":254.01393,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1942.0,"raw_peak_contact_force":558.51333,"subtask_id":"contact_peg","tcp_end":[0.55493,0.11758,0.24705],"tcp_start":[0.55794,0.1165,0.2736],"tcp_to_object_dist_end":0.21932,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50372,0.11175,0.03388],"object_pos_start":[0.50373,0.11174,0.03388],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19187,"object_z_max":0.03388,"peak_contact_force":49.88964,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":365.41753,"subtask_id":"contact_peg","tcp_end":[0.55489,0.11756,0.24704],"tcp_start":[0.55493,0.11758,0.24705],"tcp_to_object_dist_end":0.21929,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11176,0.03388],"object_pos_start":[0.50372,0.11175,0.03388],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19188,"object_z_max":0.03388,"peak_contact_force":347.05353,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":351.74873,"subtask_id":"push_to_goal","tcp_end":[0.55523,0.11702,0.24728],"tcp_start":[0.55505,0.11729,0.24715],"tcp_to_object_dist_end":0.21959,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.5037,0.11168,0.03392],"object_pos_start":[0.50371,0.11176,0.03388],"object_to_goal_dist_end":0.19182,"object_to_goal_dist_start":0.1919,"object_z_max":0.03398,"peak_contact_force":0.56783,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":576.0,"raw_peak_contact_force":366.93432,"tcp_end":[0.55496,0.11691,0.3353],"tcp_start":[0.55523,0.11702,0.24728],"tcp_to_object_dist_end":0.30575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```