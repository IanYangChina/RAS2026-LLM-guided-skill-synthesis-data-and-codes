## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.6900 | 1.00 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | contact_detected | force_exceeded | pose_tolerance | 6 | 0.5151 | 0.51 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 7 | 0.8400 | 1.00 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 8 | 0.7900 | 1.00 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.8400 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.690) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: hinge_progress
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.05
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 10.0
      - 30.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: abort
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.05
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.05, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_contact, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=0.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.05, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.690
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1665 |
| contact_2 | 1.00 | 1.00 | 0.0036 |
| push_3 | 0.00 | 1.00 | 0.3153 |
| retract_4 | 0.33 | 0.67 | 0.0475 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.104, 0.234, 0.370) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 0.000 | 46.298 |
| contact_2 | contact | 1.00 / force_exceeded | (0.104, 0.234, 0.370)→(0.104, 0.231, 0.369) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 16.565 | 15.177 |
| push_3 | push | 0.00 / step_budget | (0.104, 0.231, 0.369)→(0.205, -0.047, 0.321) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 138.930 | 694.239 |
| retract_4 | retract | 0.33 / guard_failure | (0.205, -0.047, 0.321)→(0.250, -0.034, 0.312) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 129.433 | 97.923 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.690
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.7
- **Final σ (mean)**: 0.281


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.41489,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.11912,"approach_1.speed":0.10488,"approach_1.tolerance":0.03177,"contact_2.force_threshold":12.8234,"contact_2.speed":0.02515,"push_3.push_distance":0.28151,"push_3.speed":0.0667,"push_3.tolerance":0.06409,"retract_4.speed":0.08853,"retract_4.tolerance":0.03677},"optimized_scores":{"best_composite_score":0.69,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":762.0,"contact_point_centroid":[0.11522,0.01692,0.35064],"force_p95":921.22614,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1298.45854,"mean_force":324.62075,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.26901,0.10291,0.28494]},{"body_a":"door_panel","body_b":"link5","contact_count":337.0,"contact_point_centroid":[0.12919,0.05081,0.44953],"force_p95":852.95733,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1242.76437,"mean_force":570.74012,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.1431,0.27201,0.38704]},{"body_a":"door_panel","body_b":"link6","contact_count":380.0,"contact_point_centroid":[0.20159,0.09303,0.41946],"force_p95":674.89546,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":741.18835,"mean_force":327.14782,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.1512,0.26167,0.37429]},{"body_a":"link1","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.12338,-0.00731,0.34607],"force_p95":244.26698,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.26698,"mean_force":244.26698,"phase_index":3.0,"phase_name":"retract_4","phase_type":"retract","tcp_position_centroid":[0.3275,-0.00294,0.28661]},{"body_a":"door_panel","body_b":"link7","contact_count":144.0,"contact_point_centroid":[0.37319,-0.00339,0.29247],"force_p95":69.09456,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.15914,"mean_force":31.76454,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.31356,0.04034,0.24169]},{"body_a":"door_panel","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.10205,0.2374,0.4746],"force_p95":41.64321,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.94646,"mean_force":27.36352,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.101,0.32062,0.36325]},{"body_a":"door_panel","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.1012,0.23007,0.47151],"force_p95":20.40984,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.69895,"mean_force":11.95242,"phase_index":1.0,"phase_name":"contact_2","phase_type":"contact","tcp_position_centroid":[0.10074,0.31289,0.36022]},{"body_a":"world","body_b":"door_panel","contact_count":116.0,"contact_point_centroid":[0.30004,0.21068,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10083,0.35939,0.36355]},{"body_a":"world","body_b":"door_panel","contact_count":48.0,"contact_point_centroid":[0.29982,0.20509,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_2","phase_type":"contact","tcp_position_centroid":[0.10079,0.3134,0.36032]},{"body_a":"world","body_b":"door_panel","contact_count":764.0,"contact_point_centroid":[0.34924,0.0875,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.20956,0.18105,0.32687]}],"total_contact_groups":10},"final_pose_error":0.17671,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.32753,-0.00306,0.28652],"hinge_angle":1.0713,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1298.45854,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":131.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":127.0,"raw_peak_contact_force":50.94646,"tcp_end":[0.10091,0.31684,0.36177],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.5009,"phase_name":"contact_2","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":63.0,"raw_peak_contact_force":25.69895,"tcp_end":[0.10063,0.31152,0.35984],"tcp_start":[0.10091,0.31684,0.36177],"tcp_to_object_dist_end":0.48648,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":274.02319,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2387.0,"raw_peak_contact_force":1298.45854,"tcp_end":[0.3275,-0.00294,0.28661],"tcp_start":[0.10063,0.31152,0.35984],"tcp_to_object_dist_end":0.43521,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":244.26698,"phase_name":"retract_4","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1.0,"raw_peak_contact_force":244.26698,"tcp_end":[0.32753,-0.00306,0.28652],"tcp_start":[0.3275,-0.00294,0.28661],"tcp_to_object_dist_end":0.43517,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":21.0,"average_failure_rate":0.13907,"average_mean_iterations":32.52318,"average_solve_count":151.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08334,"approach_1.speed":0.12052,"approach_1.tolerance":0.03358,"contact_2.force_threshold":12.80937,"contact_2.speed":0.04506,"push_3.push_distance":0.28952,"push_3.speed":0.1041,"push_3.tolerance":0.07809,"retract_4.speed":0.12369,"retract_4.tolerance":0.0318},"optimized_scores":{"best_composite_score":0.69,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.14612,0.04305,0.53219],"force_p95":129.39464,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.89015,"mean_force":72.5189,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.11243,0.13512,0.40337]},{"body_a":"door_panel","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.17534,0.1159,0.3971],"force_p95":61.43437,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.87318,"mean_force":37.1831,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.10884,0.17405,0.37963]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.10489,0.13835,0.50466],"force_p95":45.994,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.061,"mean_force":15.3574,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10694,0.20664,0.3989]},{"body_a":"door_panel","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.17221,0.14012,0.41377],"force_p95":44.70816,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.49578,"mean_force":30.63206,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10712,0.19766,0.38965]},{"body_a":"door_panel","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.17243,0.12771,0.39936],"force_p95":16.71568,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.83231,"mean_force":11.66643,"phase_index":1.0,"phase_name":"contact_2","phase_type":"contact","tcp_position_centroid":[0.10732,0.18513,0.37526]},{"body_a":"world","body_b":"door_panel","contact_count":360.0,"contact_point_centroid":[0.30399,0.15905,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10354,0.31882,0.39747]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30683,0.14723,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_2","phase_type":"contact","tcp_position_centroid":[0.10731,0.18521,0.37527]},{"body_a":"world","body_b":"door_panel","contact_count":392.0,"contact_point_centroid":[0.35246,0.06644,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.08904,-0.02065,0.434]},{"body_a":"world","body_b":"door_panel","contact_count":128.0,"contact_point_centroid":[0.35563,0.06123,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_4","phase_type":"retract","tcp_position_centroid":[0.16466,-0.11024,0.37069]}],"total_contact_groups":9},"final_pose_error":0.03127,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.23331,-0.0886,0.35633],"hinge_angle":0.71198,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":134.89015,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":385.0,"raw_peak_contact_force":51.061,"tcp_end":[0.10733,0.18749,0.37714],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.83231,"phase_name":"contact_2","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":46.0,"raw_peak_contact_force":19.83231,"tcp_end":[0.10735,0.18381,0.37472],"tcp_start":[0.10733,0.18749,0.37714],"tcp_to_object_dist_end":0.43096,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":434.0,"raw_peak_contact_force":134.89015,"tcp_end":[0.09929,-0.12786,0.38384],"tcp_start":[0.10735,0.18381,0.37472],"tcp_to_object_dist_end":0.41658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":214.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_4","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":128.0,"raw_peak_contact_force":0.0,"tcp_end":[0.23331,-0.0886,0.35633],"tcp_start":[0.09929,-0.12786,0.38384],"tcp_to_object_dist_end":0.43503,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.168,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.08828,"approach_1.speed":0.06025,"approach_1.tolerance":0.02497,"contact_2.force_threshold":12.44415,"contact_2.speed":0.03593,"push_3.push_distance":0.24094,"push_3.speed":0.08607,"push_3.tolerance":0.06854,"retract_4.speed":0.07478,"retract_4.tolerance":0.0318},"optimized_scores":{"best_composite_score":0.69,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link6","contact_count":781.0,"contact_point_centroid":[0.11557,-0.05195,0.33558],"force_p95":439.13755,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":649.36893,"mean_force":281.48796,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.20438,0.04005,0.31153]},{"body_a":"door_panel","body_b":"link5","contact_count":296.0,"contact_point_centroid":[0.28242,-0.11055,0.41693],"force_p95":38.95714,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":256.71814,"mean_force":22.12636,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.20609,0.05613,0.32554]},{"body_a":"door_panel","body_b":"link6","contact_count":52.0,"contact_point_centroid":[0.14351,0.06059,0.52013],"force_p95":108.52226,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.48162,"mean_force":62.52194,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.09873,0.18622,0.43981]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.16914,0.1387,0.3929],"force_p95":48.15651,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.53994,"mean_force":26.98182,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.10328,0.19599,0.37033]},{"body_a":"link1","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10427,-0.07503,0.32382],"force_p95":49.50243,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.50243,"mean_force":49.50243,"phase_index":3.0,"phase_name":"retract_4","phase_type":"retract","tcp_position_centroid":[0.18942,-0.01158,0.29221]},{"body_a":"door_panel","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.10321,0.15007,0.50869],"force_p95":35.8989,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.88541,"mean_force":24.96723,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10362,0.21932,0.40289]},{"body_a":"door_panel","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.16907,0.14551,0.40592],"force_p95":29.88632,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.03446,"mean_force":25.95499,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10384,0.20301,0.38202]},{"body_a":"world","body_b":"door_panel","contact_count":540.0,"contact_point_centroid":[0.30233,0.16809,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10203,0.31194,0.40722]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30495,0.15466,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_2","phase_type":"contact","tcp_position_centroid":[0.10394,0.19797,0.37223]},{"body_a":"world","body_b":"door_panel","contact_count":636.0,"contact_point_centroid":[0.38758,0.03906,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.19138,0.06177,0.33797]}],"total_contact_groups":10},"final_pose_error":0.23609,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18942,-0.01162,0.29223],"hinge_angle":1.04598,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":649.36893,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":580.0,"raw_peak_contact_force":36.88541,"tcp_end":[0.10394,0.19797,0.37223],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.36217,"phase_name":"contact_2","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10393,0.19757,0.3716],"tcp_start":[0.10394,0.19797,0.37223],"tcp_to_object_dist_end":0.4335,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":142.76601,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1770.0,"raw_peak_contact_force":649.36893,"tcp_end":[0.18942,-0.01158,0.29221],"tcp_start":[0.10393,0.19757,0.3716],"tcp_to_object_dist_end":0.34843,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":144.03245,"phase_name":"retract_4","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1.0,"raw_peak_contact_force":49.50243,"tcp_end":[0.18942,-0.01162,0.29223],"tcp_start":[0.18942,-0.01158,0.29221],"tcp_to_object_dist_end":0.34845,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```