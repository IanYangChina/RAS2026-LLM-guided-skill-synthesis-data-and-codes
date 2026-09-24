## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1754 | 0.43 | ✅ accepted |
| 12 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1527 | 0.31 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1048 | 0.00 | ❌ rejected |
| 10 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1121 | 0.31 | ❌ rejected |
| 9 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1157 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.175) — your mutation base

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

- **Composite score**: 0.175
- **task_score** (E): 0.435
- **fitness_score**: 0.385  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.33 | 1.00 | 0.1407 |
| align_2 | 1.00 | 1.00 | 0.0064 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.560 | 2.857 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 1.667 | 34.709 | 43.847 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.118, 0.043)→(0.495, -0.022, 0.038) | (0.497, 0.084, 0.033)→(0.503, -0.032, 0.023) | 0.164→0.060 | 1.00 / 3.000 | 45.788 | 212.227 |
| align_2 | align | 1.00 / step_budget | (0.495, -0.022, 0.038)→(0.499, -0.018, 0.038) | (0.503, -0.032, 0.023)→(0.492, -0.030, 0.027) | 0.060→0.057 | 1.00 / 4.333 | 193.854 | 283.178 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.814
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.606
- phase_score: 0.465
- phase_breakdown.approach_score: 0.035
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.763

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.521
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.606
- **Median Q (composite search score)**: 0.222
- **K-run variance**: 0.0180
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54464,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0032,"align_2.lateral_offset_x":-0.00194,"push_1.push_distance":0.061},"optimized_scores":{"best_composite_score":-0.00706,"best_fitness_score":0.20294,"best_task_score":0.40718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50334,0.10145,0.00764],"force_p95":196.83231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":199.31229,"mean_force":120.38666,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50392,0.12797,0.04706]},{"body_a":"attachment","body_b":"peg","contact_count":455.0,"contact_point_centroid":[0.50718,0.11659,0.04715],"force_p95":196.10294,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.78585,"mean_force":122.08125,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50366,0.12525,0.04656]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52502,0.10579,0.05999],"force_p95":108.38134,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.76795,"mean_force":77.4404,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.507,0.10577,0.04826]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":106.0,"contact_point_centroid":[0.542,0.07538,0.05996],"force_p95":101.63531,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.58588,"mean_force":94.0122,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49708,0.07577,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":173.0,"contact_point_centroid":[0.47339,0.07184,0.03842],"force_p95":81.26404,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.76409,"mean_force":31.76806,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50322,0.09572,0.04341]},{"body_a":"peg","body_b":"world","contact_count":113.0,"contact_point_centroid":[0.50203,0.12559,-0.0002],"force_p95":22.71069,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":15.53693,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5006,0.15358,0.04501]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54228,0.07604,0.05997],"force_p95":42.52014,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.81845,"mean_force":39.03781,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49738,0.07638,0.03668]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.49391,0.042,0.00942],"force_p95":0.80504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15523,"mean_force":0.57256,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49707,0.07576,0.03669]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.4749,0.04579,0.01067],"force_p95":0.40257,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4046,"mean_force":0.38397,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49735,0.07596,0.03666]}],"total_contact_groups":13},"final_pose_error":0.01083,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49383,0.04361,0.03386],"final_tcp_position":[0.49686,0.07618,0.03674],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":199.31229,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":488.0,"n_steps_budget":600.0,"object_pos_end":[0.49292,0.04621,0.03564],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.12648,"object_to_goal_dist_start":0.20832,"object_z_max":0.03709,"peak_contact_force":42.81845,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1195.0,"raw_peak_contact_force":199.31229,"tcp_end":[0.49736,0.07607,0.03666],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":107.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.04361,0.03386],"object_pos_start":[0.49292,0.04621,0.03564],"object_to_goal_dist_end":0.12392,"object_to_goal_dist_start":0.12648,"object_z_max":0.03564,"peak_contact_force":94.11421,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":212.0,"raw_peak_contact_force":120.58588,"tcp_end":[0.49686,0.07618,0.03674],"tcp_start":[0.49736,0.07607,0.03666],"tcp_to_object_dist_end":0.03284,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00071,"align_2.lateral_offset_x":-0.00592,"push_1.push_distance":0.19997},"optimized_scores":{"best_composite_score":0.31139,"best_fitness_score":0.52139,"best_task_score":0.60588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":318.0,"contact_point_centroid":[0.52508,-0.06268,0.05996],"force_p95":323.55733,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":379.7272,"mean_force":222.28035,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50051,-0.06246,0.03756]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":382.0,"contact_point_centroid":[0.54526,-0.05937,0.05995],"force_p95":315.47756,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.66121,"mean_force":238.7833,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50015,-0.06283,0.03741]},{"body_a":"channel_base_body","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.53816,-0.1,0.06498],"force_p95":227.48874,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.18315,"mean_force":133.50473,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49544,-0.06684,0.03732]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":315.0,"contact_point_centroid":[0.53454,-0.01244,0.05999],"force_p95":165.36573,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.65332,"mean_force":102.64884,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48919,-0.00815,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":458.0,"contact_point_centroid":[0.50261,-0.06573,0.03676],"force_p95":122.66687,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.07161,"mean_force":69.40444,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49943,-0.06349,0.0374]},{"body_a":"attachment","body_b":"peg","contact_count":913.0,"contact_point_centroid":[0.49769,0.00585,0.03562],"force_p95":120.2496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.03588,"mean_force":71.17429,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4893,0.01103,0.03808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.49687,-0.06426,0.00644],"force_p95":118.0725,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.51059,"mean_force":62.86615,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49942,-0.0635,0.03739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":967.0,"contact_point_centroid":[0.50842,-0.00627,0.00907],"force_p95":91.1657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.66779,"mean_force":43.34881,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4893,0.01531,0.03819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":841.0,"contact_point_centroid":[0.52623,-0.00833,0.02642],"force_p95":97.05078,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.75041,"mean_force":58.7094,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.00499,0.03807]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5358,-0.1,0.065],"force_p95":94.92408,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.14724,"mean_force":70.72029,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49291,-0.06777,0.03779]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52535,-0.06459,0.0169],"force_p95":68.94461,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.60775,"mean_force":43.24192,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49469,-0.06757,0.03753]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":284.0,"contact_point_centroid":[0.4745,-0.07872,0.0234],"force_p95":34.7998,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.94828,"mean_force":26.61132,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50042,-0.0624,0.03769]},{"body_a":"peg","body_b":"link7","contact_count":366.0,"contact_point_centroid":[0.52013,0.01032,0.06772],"force_p95":25.29839,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.18281,"mean_force":12.85975,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48929,0.0351,0.03792]},{"body_a":"peg","body_b":"world","contact_count":51.0,"contact_point_centroid":[0.50976,-0.06367,-0.0006],"force_p95":14.55856,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.615,"mean_force":1.68785,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49175,-0.06285,0.03779]},{"body_a":"peg","body_b":"world","contact_count":133.0,"contact_point_centroid":[0.50572,-0.06531,-0.001],"force_p95":8.56946,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.64499,"mean_force":1.39515,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49674,-0.06594,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]}],"total_contact_groups":18},"final_pose_error":0.04023,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49184,-0.06638,0.02409],"final_tcp_position":[0.5001,-0.06195,0.0388],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":379.7272,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50864,-0.06953,0.01655],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.0271,"object_to_goal_dist_start":0.14379,"object_z_max":0.03993,"peak_contact_force":94.54524,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3456.0,"raw_peak_contact_force":225.65332,"tcp_end":[0.49319,-0.06853,0.03792],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02639,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.49184,-0.06638,0.02409],"object_pos_start":[0.50864,-0.06953,0.01655],"object_to_goal_dist_end":0.02248,"object_to_goal_dist_start":0.0271,"object_z_max":0.02408,"peak_contact_force":266.00073,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2162.0,"raw_peak_contact_force":379.7272,"tcp_end":[0.5001,-0.06195,0.0388],"tcp_start":[0.49319,-0.06853,0.03792],"tcp_to_object_dist_end":0.01745,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00857,"align_2.lateral_offset_x":-0.00405,"push_1.push_distance":0.19984},"optimized_scores":{"best_composite_score":0.22201,"best_fitness_score":0.43201,"best_task_score":0.29125},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":337.0,"contact_point_centroid":[0.52507,-0.06797,0.05997],"force_p95":326.32584,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.22207,"mean_force":224.62433,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50081,-0.06782,0.03736]},{"body_a":"channel_base_body","body_b":"link7","contact_count":437.0,"contact_point_centroid":[0.54308,-0.10001,0.06495],"force_p95":283.30463,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.28504,"mean_force":224.83747,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50035,-0.06851,0.03737]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":302.0,"contact_point_centroid":[0.53424,-0.00609,0.05999],"force_p95":163.97697,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.71485,"mean_force":96.11785,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48888,-0.0015,0.03816]},{"body_a":"attachment","body_b":"peg","contact_count":880.0,"contact_point_centroid":[0.49789,-0.00118,0.03504],"force_p95":117.2037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.26471,"mean_force":70.04523,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48938,0.00347,0.03812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.5075,-0.01005,0.00878],"force_p95":93.60623,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.65908,"mean_force":42.32112,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48929,0.0103,0.03822]},{"body_a":"attachment","body_b":"peg","contact_count":414.0,"contact_point_centroid":[0.50094,-0.0727,0.03733],"force_p95":69.90618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.20241,"mean_force":35.39856,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50019,-0.06872,0.03741]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":834.0,"contact_point_centroid":[0.52608,-0.00805,0.02363],"force_p95":96.70835,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.70686,"mean_force":54.95553,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48934,0.0019,0.03809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":461.0,"contact_point_centroid":[0.49426,-0.0723,0.00641],"force_p95":72.02376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.20036,"mean_force":34.53506,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50023,-0.06869,0.03739]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54583,-0.06393,0.06],"force_p95":67.7207,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.15494,"mean_force":63.80549,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50036,-0.06724,0.03821]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52502,-0.04631,0.01591],"force_p95":44.34449,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.23418,"mean_force":27.77524,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49641,-0.0738,0.03817]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":356.0,"contact_point_centroid":[0.47418,-0.06851,0.02231],"force_p95":40.99117,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.01696,"mean_force":23.72971,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5008,-0.06788,0.03734]},{"body_a":"peg","body_b":"world","contact_count":122.0,"contact_point_centroid":[0.50846,-0.06561,-0.00057],"force_p95":3.71971,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.94728,"mean_force":0.83982,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49268,-0.06307,0.0381]},{"body_a":"peg","body_b":"link7","contact_count":210.0,"contact_point_centroid":[0.51723,0.00791,0.069],"force_p95":13.70194,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.86218,"mean_force":7.92904,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48888,0.0345,0.03797]},{"body_a":"peg","body_b":"world","contact_count":91.0,"contact_point_centroid":[0.50512,-0.07203,-0.00113],"force_p95":5.18469,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.68318,"mean_force":0.6747,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49799,-0.07178,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49933,0.1979,0.29752]}],"total_contact_groups":17},"final_pose_error":0.04228,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49161,-0.06618,0.02266],"final_tcp_position":[0.50035,-0.06722,0.03829],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":349.22207,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,-0.0715,0.01662],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02581,"object_to_goal_dist_start":0.13914,"object_z_max":0.0401,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3314.0,"raw_peak_contact_force":211.71485,"tcp_end":[0.49525,-0.07472,0.03858],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02505,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":461.0,"n_steps_budget":600.0,"object_pos_end":[0.49161,-0.06618,0.02266],"object_pos_start":[0.50685,-0.0715,0.01662],"object_to_goal_dist_end":0.02371,"object_to_goal_dist_start":0.02581,"object_z_max":0.02351,"peak_contact_force":221.44761,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2134.0,"raw_peak_contact_force":349.22207,"tcp_end":[0.50035,-0.06722,0.03829],"tcp_start":[0.49525,-0.07472,0.03858],"tcp_to_object_dist_end":0.01794,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```