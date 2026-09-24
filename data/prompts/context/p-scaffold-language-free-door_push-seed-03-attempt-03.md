## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2059 | 0.28 | ❌ rejected |
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | -0.2463 | 0.03 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.1148 | 0.32 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.1148 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- Frozen realised-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`
- Frozen initial hinge angle: -0.145 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: -0.1446
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=0.206) — your mutation base

```yaml
skill: door_push
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
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
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.206
- **task_score** (E): 0.283
- **fitness_score**: 0.283  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.33 | 1.00 | 0.2339 |
| contact_door | 1.00 | 1.00 | 0.0001 |
| push_door_open | 1.00 | 0.67 | 0.0463 |
| retract | 0.33 | 1.00 | 0.1710 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.054, 0.179, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 283.301 | 1986.432 |
| contact_door | contact | 1.00 / force_exceeded | (0.054, 0.179, 0.393)→(0.054, 0.179, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 64.274 | 82.597 |
| push_door_open | push | 1.00 / time_limit | (0.054, 0.179, 0.393)→(0.072, 0.200, 0.429) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 0.000 | 169.839 |
| retract | retract | 0.33 / step_budget | (0.072, 0.200, 0.429)→(0.064, 0.356, 0.421) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 130.910 | 472.394 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.572
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.572
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.572
- **Median Q (composite search score)**: 0.199
- **K-run variance**: 0.0545
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.338


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bba62da7f52483738d4dc6e46310e5298b0e0489aa689b981e86db9abdda203f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `789e053c0bcbffe7b16f252cc6b64c92268fc5193521b308e129f45c08e7a265`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.82979,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.09691,"contact_door.force_threshold":16.5343,"contact_door.speed":0.03448,"push_door_open.push_distance":0.2422,"push_door_open.push_speed":0.0456,"push_door_open.push_timeout":4.56111,"retract.speed":0.26526},"optimized_scores":{"best_composite_score":0.19911,"best_fitness_score":0.27578,"best_task_score":0.27578},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":636.0,"contact_point_centroid":[0.10299,0.24685,0.6056],"force_p95":538.00171,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1501.12079,"mean_force":320.53204,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05909,0.29476,0.4391]},{"body_a":"door_panel","body_b":"link4","contact_count":713.0,"contact_point_centroid":[0.10015,0.21565,0.62281],"force_p95":380.69406,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":555.5199,"mean_force":315.71634,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05522,0.26001,0.44477]},{"body_a":"door_panel","body_b":"link7","contact_count":299.0,"contact_point_centroid":[0.10091,0.22213,0.41496],"force_p95":350.64911,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":365.29776,"mean_force":310.54406,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05258,0.23522,0.43084]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.10003,0.18067,0.61212],"force_p95":137.40272,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.40272,"mean_force":137.40272,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.05187,0.21458,0.4269]},{"body_a":"door_panel","body_b":"link4","contact_count":2.0,"contact_point_centroid":[0.09998,0.18067,0.61212],"force_p95":73.13778,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.54783,"mean_force":51.44736,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.05176,0.21453,0.42688]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.10009,0.20041,0.41199],"force_p95":41.46917,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.86128,"mean_force":25.61008,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.05177,0.21458,0.4269]},{"body_a":"world","body_b":"door_panel","contact_count":1004.0,"contact_point_centroid":[0.30017,0.21048,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05746,0.27735,0.43536]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.10013,0.20043,0.41199],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.05187,0.21458,0.4269]},{"body_a":"world","body_b":"door_panel","contact_count":1104.0,"contact_point_centroid":[0.3,0.19003,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.06579,0.22857,0.44562]},{"body_a":"world","body_b":"door_panel","contact_count":300.0,"contact_point_centroid":[0.3,0.19003,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.09052,0.31083,0.41494]}],"total_contact_groups":10},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09768,0.3833,0.36064],"hinge_angle":-0.00013,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1501.12079,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":349.64128,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2652.0,"raw_peak_contact_force":1501.12079,"subtask_id":"approach_handle","tcp_end":[0.05187,0.21458,0.4269],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4806,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":137.40272,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":137.40272,"subtask_id":"contact_door","tcp_end":[0.05176,0.21455,0.42689],"tcp_start":[0.05187,0.21458,0.4269],"tcp_to_object_dist_end":0.48056,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1116.0,"raw_peak_contact_force":75.54783,"subtask_id":"push_door","tcp_end":[0.08398,0.24412,0.46522],"tcp_start":[0.05176,0.21455,0.42689],"tcp_to_object_dist_end":0.53205,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":300.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09768,0.3833,0.36064],"tcp_start":[0.08398,0.24412,0.46522],"tcp_to_object_dist_end":0.53527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5a9939150766bec2b15bab1845f15dc59243da82175f4d23a01f9499c42cbd2f`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.13675,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.17074,"contact_door.force_threshold":17.20894,"contact_door.speed":0.03001,"push_door_open.push_distance":0.19935,"push_door_open.push_speed":0.03471,"push_door_open.push_timeout":7.3817,"retract.speed":0.10201},"optimized_scores":{"best_composite_score":0.49531,"best_fitness_score":0.57197,"best_task_score":0.57197},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":907.0,"contact_point_centroid":[0.11303,0.10416,0.6431],"force_p95":756.75791,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2192.32823,"mean_force":537.53393,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.06678,0.22071,0.42817]},{"body_a":"door_panel","body_b":"link4","contact_count":931.0,"contact_point_centroid":[0.13666,0.033,0.65143],"force_p95":391.41878,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":538.42687,"mean_force":329.75929,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08726,0.23818,0.42956]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.13045,0.04714,0.63435],"force_p95":33.22443,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.22443,"mean_force":33.22443,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.08823,0.11061,0.39346]},{"body_a":"door_panel","body_b":"link4","contact_count":3.0,"contact_point_centroid":[0.13064,0.04662,0.63445],"force_p95":18.11002,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.87172,"mean_force":10.04214,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.08843,0.11041,0.39342]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30793,0.14684,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.06809,0.23207,0.42362]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.319,0.11434,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.08823,0.11061,0.39346]},{"body_a":"world","body_b":"door_panel","contact_count":936.0,"contact_point_centroid":[0.31869,0.115,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09367,0.11671,0.4065]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.32224,0.10792,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08766,0.2338,0.4295]}],"total_contact_groups":8},"final_pose_error":0.14332,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07913,0.30718,0.45719],"hinge_angle":0.45437,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2192.32823,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":157.40196,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1883.0,"raw_peak_contact_force":2192.32823,"subtask_id":"approach_handle","tcp_end":[0.08823,0.11061,0.39346],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":33.22443,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":33.22443,"subtask_id":"contact_door","tcp_end":[0.08837,0.11047,0.39344],"tcp_start":[0.08823,0.11061,0.39346],"tcp_to_object_dist_end":0.4181,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":939.0,"raw_peak_contact_force":18.87172,"subtask_id":"push_door","tcp_end":[0.09945,0.124,0.41947],"tcp_start":[0.08837,0.11047,0.39344],"tcp_to_object_dist_end":0.44858,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":391.31708,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1819.0,"raw_peak_contact_force":538.42687,"tcp_end":[0.07913,0.30718,0.45719],"tcp_start":[0.09945,0.124,0.41947],"tcp_to_object_dist_end":0.55646,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `2f40317e91cda9d20f75f9f44171fa9a28a4706ede195f831595653d78bddc9d`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.96875,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.10966,"contact_door.force_threshold":14.73587,"contact_door.speed":0.01362,"push_door_open.push_distance":0.22721,"push_door_open.push_speed":0.05399,"push_door_open.push_timeout":7.11011,"retract.speed":0.23347},"optimized_scores":{"best_composite_score":-0.07667,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":943.0,"contact_point_centroid":[0.10088,0.21567,0.60561],"force_p95":764.35952,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2265.84832,"mean_force":536.18916,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.02761,0.28036,0.37911]},{"body_a":"door_panel","body_b":"link4","contact_count":513.0,"contact_point_centroid":[0.1033,0.25181,0.60511],"force_p95":809.75937,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":878.75372,"mean_force":676.20193,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.01969,0.30635,0.41684]},{"body_a":"door_panel","body_b":"link4","contact_count":403.0,"contact_point_centroid":[0.09984,0.21523,0.5957],"force_p95":378.22893,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":415.09822,"mean_force":277.5887,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.0327,0.22698,0.39205]},{"body_a":"door_panel","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.10222,0.24133,0.3496],"force_p95":270.04797,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":283.9505,"mean_force":212.32353,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.02133,0.21945,0.35715]},{"body_a":"door_panel","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.10155,0.23517,0.35839],"force_p95":67.39432,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.27974,"mean_force":19.80095,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.02516,0.21471,0.36616]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.10167,0.23617,0.35164],"force_p95":75.3053,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.16308,"mean_force":58.5853,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.021,0.21178,0.35898]},{"body_a":"door_panel","body_b":"link4","contact_count":2.0,"contact_point_centroid":[0.09992,0.21632,0.59053],"force_p95":33.20824,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.82517,"mean_force":27.65591,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.021,0.21178,0.35898]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.30042,0.20552,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.03173,0.28984,0.37901]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.29992,0.20814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.02099,0.2118,0.35898]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.29989,0.20739,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.03002,0.2211,0.37977]},{"body_a":"world","body_b":"door_panel","contact_count":456.0,"contact_point_centroid":[0.30171,0.22729,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.01899,0.31402,0.41883]}],"total_contact_groups":11},"final_pose_error":0.12911,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.01503,0.37603,0.4442],"hinge_angle":-0.21692,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2265.84832,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":342.86076,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2012.0,"raw_peak_contact_force":2265.84832,"subtask_id":"approach_handle","tcp_end":[0.02101,0.21177,0.35899],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41733,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.19349,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":8.0,"raw_peak_contact_force":77.16308,"subtask_id":"contact_door","tcp_end":[0.02099,0.21181,0.35896],"tcp_start":[0.02101,0.21177,0.35899],"tcp_to_object_dist_end":0.41732,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1520.0,"raw_peak_contact_force":415.09822,"subtask_id":"push_door","tcp_end":[0.03135,0.23259,0.40269],"tcp_start":[0.02099,0.21181,0.35896],"tcp_to_object_dist_end":0.46609,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.41421,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":969.0,"raw_peak_contact_force":878.75372,"tcp_end":[0.01503,0.37603,0.4442],"tcp_start":[0.03135,0.23259,0.40269],"tcp_to_object_dist_end":0.58218,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```