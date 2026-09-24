## Search State

- **Seed**: 1
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.147) — your mutation base

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

- **Composite score**: 0.147
- **task_score** (E): 0.302
- **fitness_score**: 0.357  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.00 | 1.00 | 0.1689 |
| align_2 | 1.00 | 1.00 | 0.0403 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 34.709 | 43.847 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 3.333 | 38.060 | 211.025 |
| push_1 | push | 0.00 / step_budget | (0.494, 0.118, 0.043)→(0.495, -0.051, 0.038) | (0.497, 0.084, 0.033)→(0.503, -0.023, 0.023) | 0.164→0.069 | 1.00 / 4.000 | 231.134 | 292.803 |
| align_2 | align | 1.00 / step_budget | (0.495, -0.051, 0.038)→(0.500, -0.013, 0.038) | (0.503, -0.023, 0.023)→(0.494, -0.004, 0.028) | 0.069→0.083 | 1.00 / 1.000 | 0.560 | 2.857 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.834
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.611
- phase_score: 0.452
- phase_breakdown.push_score: 0.742
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.515
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.611
- **Median Q (composite search score)**: 0.224
- **K-run variance**: 0.0287
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.516


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00091,"align_2.lateral_offset_x":-0.00942,"push_1.push_distance":0.19929},"optimized_scores":{"best_composite_score":-0.08761,"best_fitness_score":0.12239,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":611.0,"contact_point_centroid":[0.54318,0.03591,0.05998],"force_p95":182.265,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":219.41726,"mean_force":144.45861,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49832,0.03837,0.03679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49868,0.08839,0.00786],"force_p95":186.46086,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.6923,"mean_force":87.59517,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50299,0.08092,0.04539]},{"body_a":"attachment","body_b":"peg","contact_count":696.0,"contact_point_centroid":[0.50841,0.10517,0.04969],"force_p95":188.77355,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.28072,"mean_force":134.40865,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50522,0.10878,0.04847]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":153.0,"contact_point_centroid":[0.52501,0.0754,0.06],"force_p95":136.71504,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.67269,"mean_force":72.9696,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5071,0.07538,0.04898]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":522.0,"contact_point_centroid":[0.47373,0.07887,0.02933],"force_p95":72.87167,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.19994,"mean_force":35.08905,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50409,0.05986,0.04552]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.54173,0.00052,0.06],"force_p95":61.88313,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.85439,"mean_force":45.4532,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49683,0.00475,0.03713]},{"body_a":"peg","body_b":"world","contact_count":124.0,"contact_point_centroid":[0.50193,0.12556,-0.00018],"force_p95":20.10999,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":13.79072,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50031,0.15484,0.04489]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.49727,0.07862,0.03733],"force_p95":14.71844,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.00746,"mean_force":2.77703,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49887,0.06693,0.03661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":684.0,"contact_point_centroid":[0.49395,0.08719,0.00947],"force_p95":1.54646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.70626,"mean_force":0.91126,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4983,0.03685,0.03681]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":288.0,"contact_point_centroid":[0.47487,0.08125,0.04604],"force_p95":0.56142,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.42339,"mean_force":0.36134,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49832,0.03706,0.03684]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]}],"total_contact_groups":14},"final_pose_error":0.02316,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49839,0.12489,0.03481],"final_tcp_position":[0.49931,0.09284,0.0363],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":219.41726,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":103.03901,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":0.5489,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2564.0,"raw_peak_contact_force":193.6923,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.493,0.07499,0.03379],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.15527,"object_to_goal_dist_start":0.20832,"object_z_max":0.03456,"peak_contact_force":174.93139,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1684.0,"raw_peak_contact_force":219.41726,"tcp_end":[0.49702,-0.01001,0.03707],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.08516,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.49839,0.12489,0.03481],"object_pos_start":[0.493,0.07499,0.03379],"object_to_goal_dist_end":0.20496,"object_to_goal_dist_start":0.15527,"object_z_max":0.03702,"peak_contact_force":0.58045,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49931,0.09284,0.0363],"tcp_start":[0.49702,-0.01001,0.03707],"tcp_to_object_dist_end":0.03209,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00393,"align_2.lateral_offset_x":0.00303,"push_1.push_distance":0.19223},"optimized_scores":{"best_composite_score":0.30548,"best_fitness_score":0.51548,"best_task_score":0.61086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":323.0,"contact_point_centroid":[0.52507,-0.06389,0.05996],"force_p95":291.43116,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":364.00415,"mean_force":214.71779,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50045,-0.06364,0.03776]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":372.0,"contact_point_centroid":[0.54524,-0.06046,0.05994],"force_p95":305.20566,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.39318,"mean_force":227.71539,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5,-0.06384,0.03765]},{"body_a":"channel_base_body","body_b":"link7","contact_count":103.0,"contact_point_centroid":[0.53882,-0.10001,0.06496],"force_p95":248.73572,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.57498,"mean_force":136.93538,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49604,-0.06595,0.03725]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":330.0,"contact_point_centroid":[0.53475,-0.01245,0.05999],"force_p95":167.23567,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.77307,"mean_force":102.44474,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48942,-0.00787,0.03817]},{"body_a":"attachment","body_b":"peg","contact_count":455.0,"contact_point_centroid":[0.50289,-0.06855,0.03676],"force_p95":137.38413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.19138,"mean_force":71.32658,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49927,-0.06427,0.0376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49729,-0.0672,0.00653],"force_p95":137.08183,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.08747,"mean_force":64.46593,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49927,-0.06427,0.0376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.50848,-0.0061,0.00926],"force_p95":92.77714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.14064,"mean_force":42.82424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48938,0.01694,0.03818]},{"body_a":"attachment","body_b":"peg","contact_count":912.0,"contact_point_centroid":[0.49788,0.00695,0.03644],"force_p95":121.97237,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.40122,"mean_force":71.29307,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48939,0.01254,0.03808]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":859.0,"contact_point_centroid":[0.52618,-0.00571,0.0285],"force_p95":97.11075,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.07185,"mean_force":57.97484,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48946,0.00779,0.03806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":76.0,"contact_point_centroid":[0.52551,-0.05716,0.01692],"force_p95":76.77479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.00851,"mean_force":46.56959,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49458,-0.06665,0.03756]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":265.0,"contact_point_centroid":[0.4746,-0.07763,0.02375],"force_p95":29.4693,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.79146,"mean_force":25.01284,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50031,-0.06355,0.03797]},{"body_a":"peg","body_b":"link7","contact_count":367.0,"contact_point_centroid":[0.52025,0.00989,0.0677],"force_p95":24.49123,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.56346,"mean_force":12.23222,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48942,0.03462,0.0379]},{"body_a":"peg","body_b":"world","contact_count":33.0,"contact_point_centroid":[0.51004,-0.06385,-0.00059],"force_p95":21.32285,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.71304,"mean_force":2.72465,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49139,-0.06186,0.03807]},{"body_a":"peg","body_b":"world","contact_count":137.0,"contact_point_centroid":[0.5062,-0.068,-0.00088],"force_p95":11.251,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.02468,"mean_force":2.41855,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49654,-0.06576,0.0372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.51823,-0.10004,0.01328],"force_p95":9.02639,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.03384,"mean_force":7.60587,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49933,-0.06464,0.03659]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]}],"total_contact_groups":18},"final_pose_error":0.03861,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49215,-0.06952,0.02471],"final_tcp_position":[0.50004,-0.06311,0.0391],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":364.00415,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54085,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":113.63031,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3477.0,"raw_peak_contact_force":232.77307,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50934,-0.0733,0.0164],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02625,"object_to_goal_dist_start":0.14379,"object_z_max":0.03989,"peak_contact_force":264.93804,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2193.0,"raw_peak_contact_force":364.00415,"tcp_end":[0.49256,-0.06721,0.03788],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02793,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49215,-0.06952,0.02471],"object_pos_start":[0.50934,-0.0733,0.0164],"object_to_goal_dist_end":0.02013,"object_to_goal_dist_start":0.02625,"object_z_max":0.02471,"peak_contact_force":0.55002,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.50004,-0.06311,0.0391],"tcp_start":[0.49256,-0.06721,0.03788],"tcp_to_object_dist_end":0.01762,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00746,"align_2.lateral_offset_x":0.00482,"push_1.push_distance":0.19561},"optimized_scores":{"best_composite_score":0.22373,"best_fitness_score":0.43373,"best_task_score":0.29657},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":438.0,"contact_point_centroid":[0.54311,-0.10001,0.06494],"force_p95":284.56685,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.98613,"mean_force":228.48834,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50041,-0.0686,0.03732]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":349.0,"contact_point_centroid":[0.52505,-0.06816,0.05998],"force_p95":249.17402,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.93257,"mean_force":206.15978,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5008,-0.06801,0.0373]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":316.0,"contact_point_centroid":[0.53434,-0.00666,0.05999],"force_p95":158.81991,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.60826,"mean_force":95.27629,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48899,-0.00211,0.03815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50751,-0.00975,0.00887],"force_p95":93.00063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.29078,"mean_force":42.03056,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48929,0.01048,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":880.0,"contact_point_centroid":[0.49783,-0.00106,0.03501],"force_p95":120.86771,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.02961,"mean_force":71.72816,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48938,0.00364,0.0381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.4946,-0.07218,0.00639],"force_p95":79.27048,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.84177,"mean_force":37.7237,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50024,-0.06884,0.03736]},{"body_a":"attachment","body_b":"peg","contact_count":422.0,"contact_point_centroid":[0.50112,-0.07242,0.03733],"force_p95":78.21925,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.61493,"mean_force":39.73436,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50018,-0.06888,0.0374]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":840.0,"contact_point_centroid":[0.52609,-0.01141,0.02373],"force_p95":96.2038,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.6024,"mean_force":56.1794,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48945,-2e-05,0.03808]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53736,-0.1,0.06499],"force_p95":104.5604,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":104.88631,"mean_force":70.98717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49455,-0.07389,0.03842]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":349.0,"contact_point_centroid":[0.4741,-0.06945,0.02251],"force_p95":42.22518,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.02423,"mean_force":26.49757,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5008,-0.06801,0.0373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52504,-0.04693,0.01653],"force_p95":43.28141,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.82869,"mean_force":28.86643,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49604,-0.07432,0.0383]},{"body_a":"peg","body_b":"world","contact_count":105.0,"contact_point_centroid":[0.50853,-0.06461,-0.00035],"force_p95":9.48322,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.39097,"mean_force":1.40722,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49261,-0.06461,0.03804]},{"body_a":"peg","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.51682,0.00965,0.06918],"force_p95":9.61931,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.29195,"mean_force":6.59042,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48889,0.03656,0.03796]},{"body_a":"peg","body_b":"world","contact_count":106.0,"contact_point_centroid":[0.5055,-0.07168,-0.00104],"force_p95":5.79297,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35934,"mean_force":0.85942,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49834,-0.07157,0.03759]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49933,0.1979,0.29752]}],"total_contact_groups":17},"final_pose_error":0.04155,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49136,-0.06688,0.0231],"final_tcp_position":[0.50038,-0.06738,0.03826],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":294.98613,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54579,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3301.0,"raw_peak_contact_force":206.60826,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.072,0.01747],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.0249,"object_to_goal_dist_start":0.13914,"object_z_max":0.04017,"peak_contact_force":253.53371,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2145.0,"raw_peak_contact_force":294.98613,"tcp_end":[0.49498,-0.07488,0.03861],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02447,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.49136,-0.06688,0.0231],"object_pos_start":[0.50695,-0.072,0.01747],"object_to_goal_dist_end":0.02307,"object_to_goal_dist_start":0.0249,"object_z_max":0.02374,"peak_contact_force":0.54973,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.50038,-0.06738,0.03826],"tcp_start":[0.49498,-0.07488,0.03861],"tcp_to_object_dist_end":0.01765,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```