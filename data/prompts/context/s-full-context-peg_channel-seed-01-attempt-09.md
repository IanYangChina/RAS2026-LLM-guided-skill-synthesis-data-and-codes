## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1157 | 0.31 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 6 | 0.1640 | 0.31 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.0921 | 0.15 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | -0.0376 | 0.00 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1208 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.116) — your mutation base

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

- **Composite score**: 0.116
- **task_score** (E): 0.309
- **fitness_score**: 0.326  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.33 | 1.00 | 0.1358 |
| align_2 | 1.00 | 1.00 | 0.0098 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.560 | 2.857 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 1.667 | 34.709 | 43.847 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.118, 0.043)→(0.496, -0.018, 0.040) | (0.497, 0.084, 0.033)→(0.501, -0.028, 0.023) | 0.164→0.064 | 1.00 / 3.000 | 46.228 | 220.030 |
| align_2 | align | 1.00 / step_budget | (0.496, -0.018, 0.040)→(0.495, -0.012, 0.039) | (0.501, -0.028, 0.023)→(0.498, -0.030, 0.026) | 0.064→0.059 | 1.00 / 4.000 | 202.012 | 259.298 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.783
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.296
- phase_score: 0.513
- phase_breakdown.approach_score: 0.035
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.843

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.426
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.346
- **Median Q (composite search score)**: 0.157
- **K-run variance**: 0.0106
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_distance
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63393,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00066,"align_2.lateral_offset_x":-0.00164,"push_1.push_distance":0.05683},"optimized_scores":{"best_composite_score":-0.02558,"best_fitness_score":0.18442,"best_task_score":0.3456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.50271,0.10093,0.00731],"force_p95":196.1787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":198.79099,"mean_force":128.40724,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50472,0.12519,0.04776]},{"body_a":"attachment","body_b":"peg","contact_count":513.0,"contact_point_centroid":[0.50815,0.1154,0.04858],"force_p95":195.67257,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.47817,"mean_force":137.83472,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50471,0.12408,0.04763]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.52501,0.09918,0.06],"force_p95":128.50538,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.42039,"mean_force":83.59047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50676,0.09916,0.0479]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":177.0,"contact_point_centroid":[0.47271,0.08071,0.03731],"force_p95":108.37358,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.99699,"mean_force":62.93809,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50644,0.09799,0.04733]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":76.0,"contact_point_centroid":[0.53779,0.09138,0.05993],"force_p95":90.86756,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.92881,"mean_force":83.6064,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49278,0.0909,0.03682]},{"body_a":"peg","body_b":"world","contact_count":124.0,"contact_point_centroid":[0.50206,0.12559,-0.00018],"force_p95":22.04971,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.80059,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50063,0.15349,0.04507]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":115.0,"contact_point_centroid":[0.49767,0.05073,0.00967],"force_p95":1.13872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42563,"mean_force":0.60318,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49452,0.08957,0.03746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":70.0,"contact_point_centroid":[0.47426,0.05329,0.03226],"force_p95":0.87363,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85833,"mean_force":0.27505,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49744,0.08744,0.03862]}],"total_contact_groups":12},"final_pose_error":0.01013,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49304,0.05208,0.0338],"final_tcp_position":[0.49151,0.09196,0.03695],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":198.79099,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48628,0.06056,0.0358],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.14129,"object_to_goal_dist_start":0.20832,"object_z_max":0.03678,"peak_contact_force":0.63881,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1407.0,"raw_peak_contact_force":198.79099,"tcp_end":[0.50338,0.08461,0.04234],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":127.0,"n_steps_budget":600.0,"object_pos_end":[0.49304,0.05208,0.0338],"object_pos_start":[0.48628,0.06056,0.0358],"object_to_goal_dist_end":0.13241,"object_to_goal_dist_start":0.14129,"object_z_max":0.03606,"peak_contact_force":88.3866,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":261.0,"raw_peak_contact_force":90.92881,"tcp_end":[0.49151,0.09196,0.03695],"tcp_start":[0.50338,0.08461,0.04234],"tcp_to_object_dist_end":0.04003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0066,"align_2.lateral_offset_x":0.00818,"push_1.push_distance":0.19009},"optimized_scores":{"best_composite_score":0.15654,"best_fitness_score":0.36654,"best_task_score":0.28422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":443.0,"contact_point_centroid":[0.53791,-0.06093,0.05998],"force_p95":326.20569,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":370.28235,"mean_force":184.03133,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49158,-0.064,0.04007]},{"body_a":"channel_base_body","body_b":"link7","contact_count":260.0,"contact_point_centroid":[0.53501,-0.10001,0.06496],"force_p95":193.63963,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.99686,"mean_force":161.34246,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49108,-0.06465,0.03929]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":354.0,"contact_point_centroid":[0.53467,-0.01372,0.05999],"force_p95":172.14131,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.33238,"mean_force":104.87989,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48932,-0.00938,0.03821]},{"body_a":"attachment","body_b":"peg","contact_count":455.0,"contact_point_centroid":[0.5015,-0.06425,0.03507],"force_p95":127.78502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.58002,"mean_force":98.58299,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49156,-0.06402,0.04004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50905,-0.06294,0.00588],"force_p95":136.50134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.88269,"mean_force":96.73765,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49156,-0.06402,0.04004]},{"body_a":"attachment","body_b":"peg","contact_count":914.0,"contact_point_centroid":[0.49761,0.00729,0.03591],"force_p95":122.80888,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.75131,"mean_force":73.21327,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.01269,0.03811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.50852,-0.00525,0.00934],"force_p95":90.61468,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.82032,"mean_force":42.35383,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.01731,0.03821]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":862.0,"contact_point_centroid":[0.52624,-0.00563,0.02782],"force_p95":97.30466,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.79953,"mean_force":59.66058,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48933,0.0083,0.03809]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":455.0,"contact_point_centroid":[0.52605,-0.06641,0.01996],"force_p95":71.82481,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.20761,"mean_force":51.84577,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49156,-0.06402,0.04004]},{"body_a":"peg","body_b":"world","contact_count":9.0,"contact_point_centroid":[0.51103,-0.06984,-0.00051],"force_p95":27.10314,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.82184,"mean_force":7.98038,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49094,-0.0624,0.03797]},{"body_a":"peg","body_b":"link7","contact_count":371.0,"contact_point_centroid":[0.52023,0.01219,0.06768],"force_p95":24.88184,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.44615,"mean_force":12.8188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48932,0.03688,0.0379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":189.0,"contact_point_centroid":[0.51025,-0.10008,0.00739],"force_p95":14.6094,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.6758,"mean_force":8.24272,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4917,-0.06378,0.04049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49942,0.19831,0.29814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":447.0,"contact_point_centroid":[0.49494,0.06368,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54515,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49304,0.08732,0.11116]},{"body_a":"peg","body_b":"world","contact_count":25.0,"contact_point_centroid":[0.51017,-0.0604,-0.00023],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49106,-0.06483,0.03794]}],"total_contact_groups":16},"final_pose_error":0.04245,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5082,-0.07463,0.02068],"final_tcp_position":[0.493,-0.06237,0.04184],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":370.28235,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51092,-0.07285,0.01718],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02629,"object_to_goal_dist_start":0.14379,"object_z_max":0.03995,"peak_contact_force":74.64701,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3486.0,"raw_peak_contact_force":253.33238,"tcp_end":[0.49127,-0.06381,0.03783],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02991,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.5082,-0.07463,0.02068],"object_pos_start":[0.51092,-0.07285,0.01718],"object_to_goal_dist_end":0.02166,"object_to_goal_dist_start":0.02629,"object_z_max":0.0214,"peak_contact_force":324.15907,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2282.0,"raw_peak_contact_force":370.28235,"tcp_end":[0.493,-0.06237,0.04184],"tcp_start":[0.49127,-0.06381,0.03783],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00646,"align_2.lateral_offset_x":0.00259,"push_1.push_distance":0.2},"optimized_scores":{"best_composite_score":0.21617,"best_fitness_score":0.42617,"best_task_score":0.29635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":356.0,"contact_point_centroid":[0.52505,-0.06652,0.05998],"force_p95":293.87276,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.68254,"mean_force":193.73103,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50067,-0.06636,0.03714]},{"body_a":"channel_base_body","body_b":"link7","contact_count":436.0,"contact_point_centroid":[0.54289,-0.10001,0.06495],"force_p95":256.61802,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.73544,"mean_force":179.60366,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50015,-0.06704,0.03719]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":215.0,"contact_point_centroid":[0.54563,-0.06283,0.05997],"force_p95":206.2677,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.69119,"mean_force":124.9029,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50049,-0.06614,0.0375]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":332.0,"contact_point_centroid":[0.53423,-0.00823,0.05999],"force_p95":156.20457,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.9654,"mean_force":96.87929,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48887,-0.00395,0.03817]},{"body_a":"attachment","body_b":"peg","contact_count":419.0,"contact_point_centroid":[0.50139,-0.0709,0.03699],"force_p95":92.90453,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.70452,"mean_force":42.92304,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49988,-0.06735,0.03726]},{"body_a":"attachment","body_b":"peg","contact_count":879.0,"contact_point_centroid":[0.49765,-0.00078,0.03494],"force_p95":119.1133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.97766,"mean_force":71.65797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48918,0.0038,0.03811]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50759,-0.00922,0.0089],"force_p95":93.60655,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.30978,"mean_force":41.04468,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48911,0.01069,0.0382]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":840.0,"contact_point_centroid":[0.52615,-0.01148,0.02377],"force_p95":96.38941,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.15489,"mean_force":57.26921,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48924,0.00022,0.03809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.49511,-0.06885,0.00626],"force_p95":80.09332,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.13492,"mean_force":38.89727,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49996,-0.06728,0.03722]},{"body_a":"channel_base_body","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.53641,-0.1,0.06499],"force_p95":89.52536,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.72508,"mean_force":54.58631,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49357,-0.07093,0.03811]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52503,-0.0626,0.01717],"force_p95":51.54334,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.22538,"mean_force":32.32245,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49565,-0.07277,0.03814]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":337.0,"contact_point_centroid":[0.47411,-0.07366,0.02227],"force_p95":41.94733,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.87143,"mean_force":26.34884,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50065,-0.06633,0.03717]},{"body_a":"peg","body_b":"world","contact_count":94.0,"contact_point_centroid":[0.50913,-0.06517,-0.00042],"force_p95":12.65007,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.35381,"mean_force":1.3638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49219,-0.06464,0.03791]},{"body_a":"peg","body_b":"link7","contact_count":170.0,"contact_point_centroid":[0.51645,0.00992,0.06934],"force_p95":6.99546,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.2589,"mean_force":5.86843,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48882,0.03715,0.03797]},{"body_a":"peg","body_b":"world","contact_count":117.0,"contact_point_centroid":[0.50595,-0.06976,-0.00093],"force_p95":7.14407,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.18092,"mean_force":1.10184,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49792,-0.07003,0.03743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]}],"total_contact_groups":18},"final_pose_error":0.04148,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49128,-0.06632,0.02318],"final_tcp_position":[0.50026,-0.06588,0.03825],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":316.68254,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50729,-0.07073,0.01738],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02551,"object_to_goal_dist_start":0.13914,"object_z_max":0.04015,"peak_contact_force":63.39954,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3296.0,"raw_peak_contact_force":207.9654,"tcp_end":[0.49439,-0.07375,0.03846],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.0249,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.49128,-0.06632,0.02318],"object_pos_start":[0.50729,-0.07073,0.01738],"object_to_goal_dist_end":0.02336,"object_to_goal_dist_start":0.02551,"object_z_max":0.02383,"peak_contact_force":193.4913,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2382.0,"raw_peak_contact_force":316.68254,"tcp_end":[0.50026,-0.06588,0.03825],"tcp_start":[0.49439,-0.07375,0.03846],"tcp_to_object_dist_end":0.01755,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```