## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.6400 | 0.97 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.3222 | 0.98 | ✅ accepted |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.4145 | 0.96 | ✅ accepted |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.1935 | 0.17 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.1571 | 0.46 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.97). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`
- Frozen initial hinge angle: 0.013 rad
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
  frozen_initial_hinge_angle_rad: 0.0133
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80

## Current Skill (Q=0.640) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: door_push_progress
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.04
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.3
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_height:
      type: scalar
      range:
      - 0.3
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.35
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    guard_force_threshold:
      type: scalar
      range:
      - 10.0
      - 28.0
      default: 22.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 12.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 22.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: door_push_progress
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.05
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.04, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.35, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - guard_force_threshold: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=22.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.640
- **task_score** (E): 0.967
- **fitness_score**: 0.967  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2350 |
| contact_1 | 1.00 | 1.00 | 0.0065 |
| push_1 | 1.00 | 1.00 | 0.1144 |
| retract_1 | 1.00 | 0.33 | 0.1091 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.177, 0.425) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 9.565 | 31.386 |
| contact_1 | contact | 1.00 / force_exceeded | (0.100, 0.177, 0.425)→(0.100, 0.176, 0.419) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 21.646 | 3.826 |
| push_1 | push | 1.00 / time_limit | (0.100, 0.176, 0.419)→(0.099, 0.062, 0.405) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 4.876 | 23.761 |
| retract_1 | retract | 1.00 / step_budget | (0.099, 0.062, 0.405)→(0.099, 0.110, 0.503) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 2.958 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.673
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.331


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60c29f30561fee2ce06b067ae52309dfc2791a8d10a0f8247d4f057dc1f7bbf4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `34da519aca1008b6dc2cb922623d951e3d277879157a381e988a54565a8fccc4`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03292,"average_solve_count":243.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.43449,"approach_1.arc_height":0.07805,"approach_1.speed":0.03608,"contact_1.contact_force":5.98103,"contact_1.contact_lateral_offset":-0.0302,"contact_1.speed":0.01042,"push_1.guard_force_threshold":27.94134,"push_1.max_time":12.16264,"push_1.push_depth":0.42331,"push_1.push_speed":0.02652,"retract_1.retract_height":0.12729,"retract_1.speed":0.04577},"optimized_scores":{"best_composite_score":0.67333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":72.0,"contact_point_centroid":[0.165,0.13906,0.48079],"force_p95":26.81151,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.1946,"mean_force":20.12173,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0998,0.19653,0.45685]},{"body_a":"door_panel","body_b":"link7","contact_count":786.0,"contact_point_centroid":[0.1655,0.05473,0.44563],"force_p95":17.19546,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.7043,"mean_force":12.99362,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09948,0.11178,0.41999]},{"body_a":"door_panel","body_b":"link6","contact_count":109.0,"contact_point_centroid":[0.10121,0.17282,0.57522],"force_p95":21.84787,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.25581,"mean_force":11.69271,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09995,0.2436,0.46903]},{"body_a":"world","body_b":"door_panel","contact_count":728.0,"contact_point_centroid":[0.30116,0.18017,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10001,0.30631,0.43697]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16498,0.11881,0.4697],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09978,0.17633,0.44579]},{"body_a":"world","body_b":"door_panel","contact_count":136.0,"contact_point_centroid":[0.30819,0.14247,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09965,0.17557,0.44057]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.32179,0.11074,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09948,0.10839,0.41931]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16651,-0.01146,0.43365],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09956,0.0452,0.40643]},{"body_a":"world","body_b":"door_panel","contact_count":664.0,"contact_point_centroid":[0.33533,0.08605,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09932,0.07824,0.46362]}],"total_contact_groups":9},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09927,0.09469,0.52386],"hinge_angle":0.54569,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.1946,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.41121,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":909.0,"raw_peak_contact_force":27.1946,"tcp_end":[0.09978,0.17633,0.44579],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.4462,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":137.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09959,0.17499,0.43438],"tcp_start":[0.09978,0.17633,0.44579],"tcp_to_object_dist_end":0.47878,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1710.0,"raw_peak_contact_force":25.7043,"subtask_id":"door_push_progress","tcp_end":[0.09955,0.04522,0.40644],"tcp_start":[0.09959,0.17499,0.43438],"tcp_to_object_dist_end":0.42089,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":666.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09927,0.09469,0.52386],"tcp_start":[0.09955,0.04522,0.40644],"tcp_to_object_dist_end":0.54152,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8ddc65539fcda71658f49649be9748aaabe492bbd016f1d18cf00d6d19f91cef`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90638,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.4087,"approach_1.arc_height":0.0605,"approach_1.speed":0.05366,"contact_1.contact_force":3.91487,"contact_1.contact_lateral_offset":-0.04602,"contact_1.speed":0.00828,"push_1.guard_force_threshold":24.31406,"push_1.max_time":13.03021,"push_1.push_depth":0.33063,"push_1.push_speed":0.03094,"retract_1.retract_height":0.07175,"retract_1.speed":0.02168},"optimized_scores":{"best_composite_score":0.57344,"best_fitness_score":0.90011,"best_task_score":0.90011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":67.0,"contact_point_centroid":[0.16508,0.1391,0.45178],"force_p95":28.80924,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.63034,"mean_force":20.04397,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09989,0.19658,0.42782]},{"body_a":"door_panel","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.10162,0.16634,0.54355],"force_p95":21.38951,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.16475,"mean_force":11.63864,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10001,0.23601,0.43774]},{"body_a":"door_panel","body_b":"link7","contact_count":769.0,"contact_point_centroid":[0.16536,0.06191,0.42944],"force_p95":18.98084,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.24691,"mean_force":12.70948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09953,0.11905,0.40386]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.165,0.1194,0.4425],"force_p95":8.76807,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.22955,"mean_force":4.61477,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09983,0.17691,0.41854]},{"body_a":"world","body_b":"door_panel","contact_count":608.0,"contact_point_centroid":[0.30149,0.17591,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10006,0.29776,0.41488]},{"body_a":"world","body_b":"door_panel","contact_count":48.0,"contact_point_centroid":[0.30807,0.14289,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09969,0.17642,0.41734]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.31934,0.11526,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09953,0.11902,0.40379]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16543,0.00538,0.43304],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09917,0.0625,0.40512]},{"body_a":"world","body_b":"door_panel","contact_count":392.0,"contact_point_centroid":[0.3316,0.09164,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09899,0.07866,0.43751]}],"total_contact_groups":9},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09897,0.10526,0.47009],"hinge_angle":0.51532,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.63034,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":757.0,"raw_peak_contact_force":29.63034,"tcp_end":[0.09987,0.17698,0.41862],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":31.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.55816,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":50.0,"raw_peak_contact_force":9.22955,"tcp_end":[0.09968,0.17567,0.41517],"tcp_start":[0.09987,0.17698,0.41862],"tcp_to_object_dist_end":0.4617,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.25171,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1657.0,"raw_peak_contact_force":24.24691,"subtask_id":"door_push_progress","tcp_end":[0.09917,0.0625,0.40512],"tcp_start":[0.09968,0.17567,0.41517],"tcp_to_object_dist_end":0.42174,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":393.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09897,0.10526,0.47009],"tcp_start":[0.09917,0.0625,0.40512],"tcp_to_object_dist_end":0.49179,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ff14b28c151409e7d588c8444930f7538b4d5212a336dd723b958144baa5103b`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.40155,"approach_1.arc_height":0.05262,"approach_1.speed":0.07705,"contact_1.contact_force":4.08283,"contact_1.contact_lateral_offset":-0.03661,"contact_1.speed":0.00834,"push_1.guard_force_threshold":25.00754,"push_1.max_time":14.97259,"push_1.push_depth":0.22973,"push_1.push_speed":0.02721,"retract_1.retract_height":0.12143,"retract_1.speed":0.0445},"optimized_scores":{"best_composite_score":0.67333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":168.0,"contact_point_centroid":[0.10092,0.18521,0.53267],"force_p95":27.30774,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.33301,"mean_force":14.25748,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09993,0.25867,0.42554]},{"body_a":"door_panel","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.16513,0.13969,0.4422],"force_p95":32.51149,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.42978,"mean_force":20.22016,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09995,0.19713,0.41821]},{"body_a":"door_panel","body_b":"link7","contact_count":751.0,"contact_point_centroid":[0.16525,0.06614,0.42175],"force_p95":18.29198,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.33173,"mean_force":12.30028,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09954,0.12335,0.39608]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16512,0.02255,0.43066],"force_p95":8.43021,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.87391,"mean_force":4.43695,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09907,0.07976,0.40243]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16505,0.12016,0.43434],"force_p95":2.13647,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.24891,"mean_force":1.12446,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09989,0.17766,0.41036]},{"body_a":"world","body_b":"door_panel","contact_count":648.0,"contact_point_centroid":[0.30094,0.18744,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10001,0.29352,0.40812]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30795,0.1433,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09977,0.17707,0.4085]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.31786,0.11813,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09955,0.12561,0.39596]},{"body_a":"world","body_b":"door_panel","contact_count":600.0,"contact_point_centroid":[0.32717,0.09886,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09888,0.11134,0.45464]}],"total_contact_groups":9},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09882,0.12903,0.51401],"hinge_angle":0.4711,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.33301,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.28474,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":37.33301,"tcp_end":[0.09993,0.17773,0.41043],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":21.9334,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":30.0,"raw_peak_contact_force":2.24891,"tcp_end":[0.09975,0.17644,0.40615],"tcp_start":[0.09993,0.17773,0.41043],"tcp_to_object_dist_end":0.45392,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.37741,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1599.0,"raw_peak_contact_force":21.33173,"subtask_id":"door_push_progress","tcp_end":[0.09907,0.07975,0.40242],"tcp_start":[0.09975,0.17644,0.40615],"tcp_to_object_dist_end":0.42204,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":602.0,"raw_peak_contact_force":8.87391,"tcp_end":[0.09882,0.12903,0.51401],"tcp_start":[0.09907,0.07975,0.40242],"tcp_to_object_dist_end":0.53909,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```