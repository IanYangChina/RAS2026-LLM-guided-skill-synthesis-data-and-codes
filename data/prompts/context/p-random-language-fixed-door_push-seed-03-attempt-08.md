## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_exceeded | time_limit | 5 | 0.6961 | 0.28 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_exceeded | time_limit | 5 | 1.7500 | 1.00 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_exceeded | time_limit | 5 | 1.7500 | 1.00 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_exceeded | time_limit | 5 | 1.7500 | 1.00 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_exceeded | time_limit | 5 | 1.7500 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.696) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: hinge_progress
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.696
- **task_score** (E): 0.279
- **fitness_score**: 0.279  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.1778 |
| push_door | 1.00 | 1.00 | 0.1427 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / force_exceeded | (0.100, 0.399, 0.350)→(0.100, 0.222, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 18.605 | 25.799 |
| push_door | push | 1.00 / time_limit | (0.100, 0.222, 0.348)→(0.048, 0.141, 0.435) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 4.000 | 189.269 | 1301.396 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.485
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.485
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.485
- **Median Q (composite search score)**: 0.954
- **K-run variance**: 0.3300
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.270


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":15.0,"average_failure_rate":0.21429,"average_mean_iterations":46.98571,"average_solve_count":70.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.09407,"approach_handle.force_threshold":16.54482,"push_door.max_time":6.87559,"push_door.push_distance":0.17418,"push_door.push_speed":0.10124},"optimized_scores":{"best_composite_score":1.23465,"best_fitness_score":0.48465,"best_task_score":0.48465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":83.0,"contact_point_centroid":[-0.1049,0.03577,0.37408],"force_p95":488.65783,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":668.12202,"mean_force":257.86862,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[-0.0196,0.1941,0.49962]},{"body_a":"door_panel","body_b":"link6","contact_count":37.0,"contact_point_centroid":[0.10158,0.1657,0.45223],"force_p95":70.37881,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.32403,"mean_force":30.15406,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10126,0.24386,0.3507]},{"body_a":"door_panel","body_b":"link6","contact_count":384.0,"contact_point_centroid":[0.10056,0.21017,0.45671],"force_p95":15.20926,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.41866,"mean_force":7.78141,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09952,0.28961,0.34786]},{"body_a":"world","body_b":"door_panel","contact_count":972.0,"contact_point_centroid":[0.29999,0.20173,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09954,0.32144,0.34779]},{"body_a":"world","body_b":"door_panel","contact_count":500.0,"contact_point_centroid":[0.30228,0.1683,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.06645,0.22495,0.42856]}],"total_contact_groups":5},"final_pose_error":0.24305,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.05519,0.17658,0.50884],"hinge_angle":0.10932,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":668.12202,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.08728,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":20.41866,"tcp_end":[0.0996,0.25457,0.34804],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44255,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":402.21894,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":620.0,"raw_peak_contact_force":668.12202,"tcp_end":[-0.05519,0.17658,0.50884],"tcp_start":[0.0996,0.25457,0.34804],"tcp_to_object_dist_end":0.54143,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.15789,"average_mean_iterations":39.59649,"average_solve_count":57.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.16685,"approach_handle.force_threshold":24.70949,"push_door.max_time":3.40108,"push_door.push_distance":0.17193,"push_door.push_speed":0.12544},"optimized_scores":{"best_composite_score":-0.10001,"best_fitness_score":0.14999,"best_task_score":0.14999},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":54.0,"contact_point_centroid":[0.11683,0.10917,0.5374],"force_p95":1560.97397,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1748.00576,"mean_force":547.90077,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12484,0.15038,0.35515]},{"body_a":"door_panel","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.10918,0.126,0.33946],"force_p95":1198.37642,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1412.05665,"mean_force":359.16424,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12291,0.15133,0.35478]},{"body_a":"link1","body_b":"link5","contact_count":66.0,"contact_point_centroid":[0.01385,0.06943,0.37169],"force_p95":1013.37137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1176.43386,"mean_force":497.75544,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12579,0.15017,0.3551]},{"body_a":"link1","body_b":"link7","contact_count":94.0,"contact_point_centroid":[0.05846,0.11207,0.33973],"force_p95":313.74761,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":555.78912,"mean_force":200.49137,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10269,0.13638,0.36673]},{"body_a":"door_panel","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.16519,0.14064,0.37241],"force_p95":27.50739,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.36368,"mean_force":15.23634,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09994,0.19794,0.34853]},{"body_a":"world","body_b":"door_panel","contact_count":808.0,"contact_point_centroid":[0.30388,0.15955,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09972,0.30271,0.34814]},{"body_a":"world","body_b":"door_panel","contact_count":500.0,"contact_point_centroid":[0.30667,0.14794,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09039,0.1581,0.40769]}],"total_contact_groups":7},"final_pose_error":0.12102,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09766,0.13054,0.39062],"hinge_angle":0.23325,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1748.00576,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":803.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.11345,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":870.0,"raw_peak_contact_force":34.36368,"tcp_end":[0.09995,0.189,0.34862],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":544.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":164.7569,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":776.0,"raw_peak_contact_force":1748.00576,"tcp_end":[0.09766,0.13054,0.39062],"tcp_start":[0.09995,0.189,0.34862],"tcp_to_object_dist_end":0.42327,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.18462,"average_mean_iterations":45.16923,"average_solve_count":65.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.16448,"approach_handle.force_threshold":17.73509,"push_door.max_time":7.60947,"push_door.push_distance":0.22163,"push_door.push_speed":0.1164},"optimized_scores":{"best_composite_score":0.95357,"best_fitness_score":0.20357,"best_task_score":0.20357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":32.0,"contact_point_centroid":[0.12634,0.11179,0.52138],"force_p95":1142.53119,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1488.05966,"mean_force":478.68998,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12224,0.15213,0.33422]},{"body_a":"door_panel","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.10675,0.12798,0.32843],"force_p95":716.77494,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1069.08959,"mean_force":214.72796,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12249,0.15041,0.33636]},{"body_a":"link1","body_b":"link5","contact_count":63.0,"contact_point_centroid":[0.01478,0.06911,0.37218],"force_p95":868.45577,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1001.90192,"mean_force":513.57363,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12435,0.15092,0.33147]},{"body_a":"link1","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.05481,0.1101,0.34896],"force_p95":363.78559,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":783.79467,"mean_force":194.12494,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09718,0.13323,0.37636]},{"body_a":"door_panel","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.10324,0.1497,0.45333],"force_p95":51.64293,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.92736,"mean_force":22.68406,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09968,0.21764,0.34921]},{"body_a":"door_panel","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.10257,0.15639,0.45347],"force_p95":10.7641,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.61359,"mean_force":8.89863,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09986,0.22421,0.34834]},{"body_a":"world","body_b":"door_panel","contact_count":780.0,"contact_point_centroid":[0.30215,0.16909,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09969,0.31136,0.34808]},{"body_a":"world","body_b":"door_panel","contact_count":784.0,"contact_point_centroid":[0.30458,0.15686,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.08459,0.17427,0.40575]}],"total_contact_groups":8},"final_pose_error":0.12867,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1003,0.11519,0.40431],"hinge_angle":0.21314,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1488.05966,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":684.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.61359,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":806.0,"raw_peak_contact_force":22.61359,"tcp_end":[0.09985,0.22096,0.34837],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42445,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.83205,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1132.0,"raw_peak_contact_force":1488.05966,"tcp_end":[0.1003,0.11519,0.40431],"tcp_start":[0.09985,0.22096,0.34837],"tcp_to_object_dist_end":0.4322,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```