## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1661 | 0.41 | ✅ accepted |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.2378 | 0.24 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1208 | 0.32 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.166
- **task_score** (E): 0.407
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| rotate_1 | 1.00 | 0.1730 |
| align_1 | 1.00 | 0.1462 |
| push_1 | 0.33 | 0.1364 |
| align_2 | 1.00 | 0.0072 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.118, 0.043)→(0.496, -0.018, 0.038) | (0.497, 0.084, 0.033)→(0.502, -0.027, 0.023) | 0.164→0.064 |
| align_2 | align | 1.00 / step_budget | (0.496, -0.018, 0.038)→(0.499, -0.013, 0.038) | (0.502, -0.027, 0.023)→(0.492, -0.025, 0.027) | 0.064→0.061 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.806
- alignment_error: None
- terminal_score: 0.611
- phase_score: 0.470
- phase_breakdown.push_score: 0.772
- phase_breakdown.approach_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.526
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.611
- **Median Q (composite search score)**: 0.219
- **K-run variance**: 0.0222
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.311


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54464,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00721,"align_2.lateral_offset_x":0.00526,"push_1.push_distance":0.04951},"optimized_scores":{"best_composite_score":-0.03698,"best_fitness_score":0.17302,"best_task_score":0.32303},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50317,0.10473,0.00745],"force_p95":196.16166,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":198.13205,"mean_force":123.64126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50399,0.13114,0.04717]},{"body_a":"attachment","body_b":"peg","contact_count":465.0,"contact_point_centroid":[0.50782,0.12172,0.04764],"force_p95":195.67749,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.61331,"mean_force":129.13585,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50396,0.13039,0.04706]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52501,0.10673,0.05999],"force_p95":106.64266,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.25316,"mean_force":67.29335,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50659,0.10672,0.0474]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54137,0.08936,0.05987],"force_p95":107.79992,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.98801,"mean_force":98.81185,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49652,0.08905,0.03639]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":147.0,"contact_point_centroid":[0.47326,0.07968,0.03966],"force_p95":78.4364,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.42869,"mean_force":35.83989,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50456,0.10246,0.0448]},{"body_a":"peg","body_b":"world","contact_count":132.0,"contact_point_centroid":[0.50204,0.12553,-0.00017],"force_p95":22.11936,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.19386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50059,0.15374,0.04502]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.49882,0.05409,0.00968],"force_p95":0.91206,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09407,"mean_force":0.52593,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49691,0.08881,0.03662]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":70.0,"contact_point_centroid":[0.4748,0.05604,0.02299],"force_p95":0.54948,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56612,"mean_force":0.29588,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49698,0.08876,0.03663]}],"total_contact_groups":12},"final_pose_error":0.01061,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49294,0.05596,0.03465],"final_tcp_position":[0.49638,0.08923,0.03661],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":488.0,"n_steps_budget":600.0,"object_pos_end":[0.49174,0.05864,0.03505],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.13898,"object_to_goal_dist_start":0.20832,"object_z_max":0.0356,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49905,0.08832,0.03826],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03073,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.49294,0.05596,0.03465],"object_pos_start":[0.49174,0.05864,0.03505],"object_to_goal_dist_end":0.13625,"object_to_goal_dist_start":0.13898,"object_z_max":0.03518,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49638,0.08923,0.03661],"tcp_start":[0.49905,0.08832,0.03826],"tcp_to_object_dist_end":0.0335,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00122,"align_2.lateral_offset_x":0.00409,"push_1.push_distance":0.19908},"optimized_scores":{"best_composite_score":0.31634,"best_fitness_score":0.52634,"best_task_score":0.61067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":328.0,"contact_point_centroid":[0.52507,-0.06263,0.05997],"force_p95":292.63645,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":369.94619,"mean_force":220.23316,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50058,-0.06243,0.03727]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":379.0,"contact_point_centroid":[0.54527,-0.05918,0.05994],"force_p95":302.20487,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.28575,"mean_force":228.73814,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50029,-0.06267,0.03716]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":295.0,"contact_point_centroid":[0.53455,-0.00733,0.05999],"force_p95":164.12129,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.55097,"mean_force":100.19991,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48919,-0.00274,0.03817]},{"body_a":"channel_base_body","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.53867,-0.1,0.06498],"force_p95":182.45022,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.9882,"mean_force":121.90178,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49604,-0.06654,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":913.0,"contact_point_centroid":[0.49795,0.00658,0.03577],"force_p95":117.76888,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.11899,"mean_force":70.22571,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48944,0.01174,0.03808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49653,-0.06239,0.00622],"force_p95":117.40262,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.70021,"mean_force":61.72075,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49985,-0.06314,0.03714]},{"body_a":"attachment","body_b":"peg","contact_count":447.0,"contact_point_centroid":[0.50271,-0.06408,0.03651],"force_p95":118.69089,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.72289,"mean_force":64.27511,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49985,-0.06314,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.50834,-0.00552,0.00896],"force_p95":90.4984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.23786,"mean_force":43.62135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48942,0.01646,0.03818]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":859.0,"contact_point_centroid":[0.52613,-0.00469,0.02685],"force_p95":97.56431,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.59576,"mean_force":56.14536,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4895,0.00718,0.03806]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":289.0,"contact_point_centroid":[0.47441,-0.07974,0.02288],"force_p95":38.73983,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.11662,"mean_force":27.09123,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50049,-0.06237,0.03738]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":28.0,"contact_point_centroid":[0.52501,-0.06178,0.01542],"force_p95":36.75225,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.58895,"mean_force":29.73421,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49645,-0.06633,0.03717]},{"body_a":"peg","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.5201,0.01204,0.06771],"force_p95":23.2841,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.37529,"mean_force":12.54787,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48921,0.03675,0.03792]},{"body_a":"peg","body_b":"world","contact_count":91.0,"contact_point_centroid":[0.50896,-0.06356,-0.00065],"force_p95":14.97131,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.76075,"mean_force":1.4975,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49234,-0.0589,0.038]},{"body_a":"peg","body_b":"world","contact_count":120.0,"contact_point_centroid":[0.50568,-0.06311,-0.00136],"force_p95":6.86417,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.54996,"mean_force":2.03182,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49786,-0.06508,0.03683]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49942,0.19831,0.29814]}],"total_contact_groups":17},"final_pose_error":0.0406,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49147,-0.06504,0.02325],"final_tcp_position":[0.50021,-0.06194,0.03836],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50706,-0.06821,0.01684],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02693,"object_to_goal_dist_start":0.14379,"object_z_max":0.03985,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49453,-0.06837,0.03835],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.0249,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.49147,-0.06504,0.02325],"object_pos_start":[0.50706,-0.06821,0.01684],"object_to_goal_dist_end":0.02402,"object_to_goal_dist_start":0.02693,"object_z_max":0.02377,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50021,-0.06194,0.03836],"tcp_start":[0.49453,-0.06837,0.03835],"tcp_to_object_dist_end":0.01772,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00576,"align_2.lateral_offset_x":0.00994,"push_1.push_distance":0.19997},"optimized_scores":{"best_composite_score":0.21898,"best_fitness_score":0.42898,"best_task_score":0.28818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":365.0,"contact_point_centroid":[0.52506,-0.06722,0.05997],"force_p95":261.17018,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.85142,"mean_force":207.78826,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50075,-0.06706,0.03723]},{"body_a":"channel_base_body","body_b":"link7","contact_count":438.0,"contact_point_centroid":[0.54309,-0.10001,0.06495],"force_p95":268.2448,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.53352,"mean_force":188.07705,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50036,-0.06776,0.03728]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":323.0,"contact_point_centroid":[0.53418,-0.00746,0.05999],"force_p95":157.33829,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.88213,"mean_force":97.15175,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48882,-0.00293,0.03818]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":102.0,"contact_point_centroid":[0.54573,-0.06329,0.05998],"force_p95":144.66528,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.15647,"mean_force":103.48254,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50041,-0.06659,0.03788]},{"body_a":"attachment","body_b":"peg","contact_count":880.0,"contact_point_centroid":[0.49774,-0.00094,0.03492],"force_p95":117.84447,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.5077,"mean_force":70.01271,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48926,0.00362,0.03812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50752,-0.0095,0.00885],"force_p95":91.96857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.5192,"mean_force":41.26897,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48918,0.01059,0.03822]},{"body_a":"attachment","body_b":"peg","contact_count":434.0,"contact_point_centroid":[0.5022,-0.07398,0.03677],"force_p95":100.96672,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.57947,"mean_force":53.02977,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50016,-0.06809,0.0373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":833.0,"contact_point_centroid":[0.5261,-0.00986,0.02379],"force_p95":96.57926,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.57375,"mean_force":55.6361,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48927,0.00072,0.0381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.49554,-0.07588,0.00624],"force_p95":93.62744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.62384,"mean_force":50.04984,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50019,-0.06802,0.03731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52508,-0.0463,0.0163],"force_p95":43.67494,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.94986,"mean_force":29.17401,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49613,-0.07391,0.03826]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":326.0,"contact_point_centroid":[0.47427,-0.05837,0.02235],"force_p95":41.55117,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.53474,"mean_force":23.58726,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50069,-0.06699,0.0373]},{"body_a":"peg","body_b":"world","contact_count":101.0,"contact_point_centroid":[0.50836,-0.06691,-0.00067],"force_p95":5.03579,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.52758,"mean_force":0.74707,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49269,-0.06459,0.03803]},{"body_a":"peg","body_b":"link7","contact_count":182.0,"contact_point_centroid":[0.51663,0.01013,0.06925],"force_p95":9.17483,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.40419,"mean_force":6.31107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48882,0.03718,0.03797]},{"body_a":"peg","body_b":"world","contact_count":110.0,"contact_point_centroid":[0.50537,-0.07443,-0.00101],"force_p95":5.94853,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.92535,"mean_force":0.90119,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49843,-0.07118,0.03752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49933,0.1979,0.29752]}],"total_contact_groups":17},"final_pose_error":0.04147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49163,-0.065,0.02302],"final_tcp_position":[0.5003,-0.06647,0.03823],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,-0.07138,0.01713],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02539,"object_to_goal_dist_start":0.13914,"object_z_max":0.04015,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.495,-0.07454,0.03856],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.0247,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.49163,-0.065,0.02302],"object_pos_start":[0.50687,-0.07138,0.01713],"object_to_goal_dist_end":0.02416,"object_to_goal_dist_start":0.02539,"object_z_max":0.02351,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.5003,-0.06647,0.03823],"tcp_start":[0.495,-0.07454,0.03856],"tcp_to_object_dist_end":0.01757,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```