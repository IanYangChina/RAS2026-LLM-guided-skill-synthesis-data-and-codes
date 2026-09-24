## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1662 | 0.18 | ✅ accepted |
| 1 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1703 | 0.00 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.166) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  weight: 0.3
- id: final_push
  weight: 0.7
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.12
    - 0.08
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.08
      - 0.16
      default: 0.12
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.06
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_push
- id: descend_behind
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.0
  parameters:
    descend_y_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: pre_push
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.02
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: final_push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.12, 0.08]
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_behind** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0]
  - parameter_bindings:
    - descend_y_offset: status=consumed; consumers=target.offset.y (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.166
- **task_score** (E): 0.183
- **fitness_score**: 0.396  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_peg | 1.00 | 0.1526 |
| descend_behind | 1.00 | 0.1638 |
| push_through_channel | 1.00 | 0.1274 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.197, 0.150) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 |
| descend_behind | align | 1.00 / step_budget | (0.492, 0.197, 0.150)→(0.495, 0.079, 0.039) | (0.498, 0.068, 0.034)→(0.503, 0.049, 0.038) | 0.148→0.129 |
| push_through_channel | push | 1.00 / time_limit | (0.495, 0.079, 0.039)→(0.495, -0.047, 0.051) | (0.503, 0.049, 0.038)→(0.501, -0.034, 0.024) | 0.129→0.049 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.714
- alignment_error: None
- terminal_score: 0.331
- phase_score: 0.588
- phase_breakdown.pre_push_score: 0.748
- phase_breakdown.final_push_score: 0.519

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.485
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.331
- **Median Q (composite search score)**: 0.175
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90654,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_y_offset":0.12821,"approach_peg.approach_z_offset":0.0894,"descend_behind.descend_y_offset":0.00134,"push_through_channel.push_speed":0.0763},"optimized_scores":{"best_composite_score":0.25491,"best_fitness_score":0.48491,"best_task_score":0.33051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.53578,0.07403,0.05971],"force_p95":286.39206,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.83147,"mean_force":207.7697,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.4905,0.07424,0.03691]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":162.0,"contact_point_centroid":[0.53586,0.06496,0.05997],"force_p95":79.56655,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.19768,"mean_force":61.75946,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49056,0.06561,0.03749]},{"body_a":"attachment","body_b":"peg","contact_count":731.0,"contact_point_centroid":[0.49931,0.01149,0.04142],"force_p95":54.20948,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.99985,"mean_force":24.83358,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49075,0.01906,0.04178]},{"body_a":"peg","body_b":"channel_base_body","contact_count":905.0,"contact_point_centroid":[0.50673,-0.01259,0.00948],"force_p95":43.66879,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.38639,"mean_force":15.82708,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49129,0.01153,0.04291]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":570.0,"contact_point_centroid":[0.52547,-0.0136,0.02912],"force_p95":37.34613,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.22777,"mean_force":19.58926,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49092,0.00631,0.04308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.49594,0.06039,0.00944],"force_p95":9.49539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.36782,"mean_force":1.48231,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48351,0.13309,0.08653]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.49294,0.07381,0.04723],"force_p95":24.68485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.0698,"mean_force":11.96618,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48894,0.0852,0.0461]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49554,0.06378,0.00936],"force_p95":0.59683,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5642,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48877,0.19523,0.21556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49926,0.19944,0.29682]}],"total_contact_groups":9},"final_pose_error":0.03238,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50134,-0.05041,0.0241],"final_tcp_position":[0.49419,-0.04956,0.05063],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49525,0.06399,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14419,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.4796,0.19162,0.13917],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16616,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.50461,0.04354,0.03689],"object_pos_start":[0.49525,0.06399,0.03394],"object_to_goal_dist_end":0.12367,"object_to_goal_dist_start":0.14419,"object_z_max":0.03776,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.4909,0.07396,0.03681],"tcp_start":[0.4796,0.19162,0.13917],"tcp_to_object_dist_end":0.03336,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50134,-0.05041,0.0241],"object_pos_start":[0.50461,0.04354,0.03689],"object_to_goal_dist_end":0.03362,"object_to_goal_dist_start":0.12367,"object_z_max":0.04042,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49419,-0.04956,0.05063],"tcp_start":[0.4909,0.07396,0.03681],"tcp_to_object_dist_end":0.02749,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90826,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_y_offset":0.14152,"approach_peg.approach_z_offset":0.09787,"descend_behind.descend_y_offset":0.00105,"push_through_channel.push_speed":0.07761},"optimized_scores":{"best_composite_score":0.17466,"best_fitness_score":0.40466,"best_task_score":0.12297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53446,0.06886,0.05971],"force_p95":312.79101,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.91253,"mean_force":233.75585,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.4891,0.06928,0.03708]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47496,0.09607,0.05992],"force_p95":251.64276,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.77607,"mean_force":141.2484,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.4846,0.09095,0.05518]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":141.0,"contact_point_centroid":[0.53469,0.06157,0.05996],"force_p95":82.29501,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.77269,"mean_force":63.54527,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48932,0.06234,0.03761]},{"body_a":"attachment","body_b":"peg","contact_count":775.0,"contact_point_centroid":[0.4983,0.01314,0.04033],"force_p95":63.84234,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.17253,"mean_force":28.57113,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48965,0.01958,0.04153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50616,-0.01182,0.00936],"force_p95":46.97538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.38825,"mean_force":17.67298,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4904,0.0077,0.04311]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":611.0,"contact_point_centroid":[0.52548,-0.01212,0.02607],"force_p95":46.30078,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.85824,"mean_force":23.34503,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49001,0.00311,0.04326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.49472,0.05555,0.00944],"force_p95":11.49213,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.91938,"mean_force":1.5661,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.4766,0.13335,0.08999]},{"body_a":"attachment","body_b":"peg","contact_count":66.0,"contact_point_centroid":[0.49287,0.06568,0.04769],"force_p95":21.50828,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.76619,"mean_force":10.03813,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.48762,0.0771,0.04369]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.49444,0.05886,0.00934],"force_p95":0.59375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58008,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48221,0.19913,0.21945]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49875,0.19951,0.29572]}],"total_contact_groups":10},"final_pose_error":0.02546,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50516,-0.04508,0.02413],"final_tcp_position":[0.49436,-0.05664,0.05158],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.49424,0.05898,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.46696,0.19924,0.14756],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1826,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.50193,0.04108,0.03565],"object_pos_start":[0.49424,0.05898,0.03386],"object_to_goal_dist_end":0.12117,"object_to_goal_dist_start":0.13923,"object_z_max":0.03756,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.48956,0.06903,0.03704],"tcp_start":[0.46696,0.19924,0.14756],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50516,-0.04508,0.02413],"object_pos_start":[0.50193,0.04108,0.03565],"object_to_goal_dist_end":0.0387,"object_to_goal_dist_start":0.12117,"object_z_max":0.04044,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49436,-0.05664,0.05158],"tcp_start":[0.48956,0.06903,0.03704],"tcp_to_object_dist_end":0.03168,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90385,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_y_offset":0.1198,"approach_peg.approach_z_offset":0.11718,"descend_behind.descend_y_offset":0.00191,"push_through_channel.push_speed":0.07985},"optimized_scores":{"best_composite_score":0.06889,"best_fitness_score":0.29889,"best_task_score":0.09701},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":53.0,"contact_point_centroid":[0.52512,0.09501,0.05995],"force_p95":350.31271,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":377.79519,"mean_force":284.15859,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.50449,0.09489,0.04296]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52505,0.09478,0.05998],"force_p95":65.41739,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.08133,"mean_force":33.7227,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50397,0.09465,0.04256]},{"body_a":"peg","body_b":"channel_base_body","contact_count":556.0,"contact_point_centroid":[0.5055,0.07686,0.00947],"force_p95":4.30778,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.07659,"mean_force":1.94587,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.51491,0.14298,0.09714]},{"body_a":"attachment","body_b":"peg","contact_count":66.0,"contact_point_centroid":[0.50684,0.0866,0.0462],"force_p95":54.67101,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.79198,"mean_force":12.00089,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"align","tcp_position_centroid":[0.50524,0.09819,0.04667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49792,0.01577,0.00904],"force_p95":24.85487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.243,"mean_force":9.63548,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4993,0.03031,0.04507]},{"body_a":"attachment","body_b":"peg","contact_count":548.0,"contact_point_centroid":[0.50386,0.04951,0.04153],"force_p95":25.03052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.01262,"mean_force":17.04426,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50055,0.06047,0.04274]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47499,-0.02774,0.02832],"force_p95":11.01007,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.225,"mean_force":7.13937,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49977,0.02241,0.04636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.50562,0.08084,0.00935],"force_p95":0.56103,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5838,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51442,0.19931,0.22784]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50037,0.1996,0.29567]}],"total_contact_groups":9},"final_pose_error":0.04502,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49584,-0.00665,0.02419],"final_tcp_position":[0.49694,-0.03606,0.05072],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":441.0,"n_steps_budget":930.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_push","tcp_end":[0.52925,0.19953,0.16463],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17816,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.50314,0.06312,0.04059],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.14315,"object_to_goal_dist_start":0.16112,"object_z_max":0.04065,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"pre_push","tcp_end":[0.50404,0.09469,0.04263],"tcp_start":[0.52925,0.19953,0.16463],"tcp_to_object_dist_end":0.03165,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49584,-0.00665,0.02419],"object_pos_start":[0.50314,0.06312,0.04059],"object_to_goal_dist_end":0.07514,"object_to_goal_dist_start":0.14315,"object_z_max":0.04059,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"final_push","tcp_end":[0.49694,-0.03606,0.05072],"tcp_start":[0.50404,0.09469,0.04263],"tcp_to_object_dist_end":0.03962,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```