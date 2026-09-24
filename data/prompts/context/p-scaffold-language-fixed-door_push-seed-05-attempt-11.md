## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 9 | 1.4900 | 1.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 8 | 0.1141 | 0.57 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 6 | 0.9422 | 0.27 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 8 | 1.5400 | 1.00 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 8 | 1.5400 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`
- Frozen initial hinge angle: 0.106 rad
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
  frozen_initial_hinge_angle_rad: 0.1065
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618

## Current Skill (Q=1.490) — your mutation base

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
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - -0.05
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.1
  parameters:
    approach_time:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.1
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_detect
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.1
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_time:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_time:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.05, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - approach_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_detect, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 1.490
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1654 |
| contact_1 | 1.00 | 1.00 | 0.0008 |
| push_1 | 1.00 | 0.33 | 0.1214 |
| retract_1 | 1.00 | 0.67 | 0.2031 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.167, 0.251, 0.380) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.667 | 9.232 | 1558.607 |
| contact_1 | contact | 1.00 / force_exceeded | (0.167, 0.251, 0.380)→(0.167, 0.251, 0.380) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 4.000 | 189.023 | 269.041 |
| push_1 | push | 1.00 / time_limit | (0.167, 0.251, 0.380)→(0.180, 0.272, 0.264) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 752.161 |
| retract_1 | retract | 1.00 / time_limit | (0.180, 0.272, 0.264)→(0.216, 0.091, 0.322) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 5.795 | 277.116 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.490
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 2.7
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.50549,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_time":8.43999,"approach_1.speed":0.13542,"contact_1.force_threshold":15.76082,"contact_1.speed":0.0431,"push_1.push_depth":0.2881,"push_1.push_time":11.98795,"push_1.speed":0.05847,"retract_1.retract_speed":0.11307,"retract_1.retract_time":6.4342},"optimized_scores":{"best_composite_score":1.49,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":873.0,"contact_point_centroid":[0.11929,0.08662,0.60444],"force_p95":531.39923,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1615.06703,"mean_force":353.26719,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1177,0.34175,0.32578]},{"body_a":"door_panel","body_b":"link4","contact_count":71.0,"contact_point_centroid":[0.18166,-0.04108,0.57254],"force_p95":621.22348,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":747.26411,"mean_force":496.3799,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1823,0.24759,0.40665]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.16938,-0.02513,0.57634],"force_p95":262.66217,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":262.66217,"mean_force":262.66217,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.17343,0.24191,0.37727]},{"body_a":"door_panel","body_b":"link5","contact_count":32.0,"contact_point_centroid":[0.17577,-0.03388,0.54839],"force_p95":19.96561,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.84838,"mean_force":3.78801,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17908,0.24536,0.39494]},{"body_a":"door_panel","body_b":"link6","contact_count":234.0,"contact_point_centroid":[0.2891,-0.00172,0.35447],"force_p95":32.55327,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.99233,"mean_force":21.41889,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.19417,0.14262,0.29138]},{"body_a":"world","body_b":"door_panel","contact_count":972.0,"contact_point_centroid":[0.31274,0.13374,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11897,0.34143,0.32813]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.34031,0.07917,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.17343,0.24191,0.37727]},{"body_a":"world","body_b":"door_panel","contact_count":488.0,"contact_point_centroid":[0.35179,0.0654,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.19126,0.26779,0.28547]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.35509,0.06219,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.19216,0.19234,0.26655]}],"total_contact_groups":9},"final_pose_error":0.31201,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19482,0.1088,0.30837],"hinge_angle":0.84232,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1615.06703,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.97454,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1845.0,"raw_peak_contact_force":1615.06703,"tcp_end":[0.17343,0.24191,0.37727],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48056,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":262.66217,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":262.66217,"tcp_end":[0.17372,0.24156,0.37793],"tcp_start":[0.17343,0.24191,0.37727],"tcp_to_object_dist_end":0.481,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":591.0,"raw_peak_contact_force":747.26411,"tcp_end":[0.1922,0.27219,0.22694],"tcp_start":[0.17372,0.24156,0.37793],"tcp_to_object_dist_end":0.40315,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.38563,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1082.0,"raw_peak_contact_force":46.99233,"tcp_end":[0.19482,0.1088,0.30837],"tcp_start":[0.1922,0.27219,0.22694],"tcp_to_object_dist_end":0.38064,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.58947,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_time":9.65389,"approach_1.speed":0.12542,"contact_1.force_threshold":21.95114,"contact_1.speed":0.02507,"push_1.push_depth":0.26341,"push_1.push_time":10.70702,"push_1.speed":0.03363,"retract_1.retract_speed":0.12073,"retract_1.retract_time":6.15178},"optimized_scores":{"best_composite_score":1.49,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":766.0,"contact_point_centroid":[0.10604,0.14548,0.54456],"force_p95":692.36427,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1613.54416,"mean_force":535.54525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09111,0.36245,0.32356]},{"body_a":"door_panel","body_b":"link4","contact_count":255.0,"contact_point_centroid":[0.13254,0.05002,0.58546],"force_p95":631.84068,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":933.874,"mean_force":327.34341,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1482,0.29431,0.3415]},{"body_a":"door_panel","body_b":"link4","contact_count":7.0,"contact_point_centroid":[0.15949,-0.00987,0.57508],"force_p95":524.91126,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":541.91354,"mean_force":447.43126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.15909,0.26597,0.37944]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.15793,-0.00726,0.57516],"force_p95":348.08878,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":348.08878,"mean_force":348.08878,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.15759,0.26407,0.37504]},{"body_a":"door_panel","body_b":"link6","contact_count":108.0,"contact_point_centroid":[0.27111,0.01462,0.34731],"force_p95":32.80633,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.09983,"mean_force":21.24739,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17342,0.15869,0.28677]},{"body_a":"door_panel","body_b":"link5","contact_count":164.0,"contact_point_centroid":[0.21909,-0.08248,0.31083],"force_p95":25.74986,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.46937,"mean_force":15.19657,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17392,0.11674,0.30914]},{"body_a":"door_panel","body_b":"link4","contact_count":134.0,"contact_point_centroid":[0.16837,-0.0234,0.59354],"force_p95":20.38005,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.35791,"mean_force":12.71591,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17485,0.21148,0.25644]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.30804,0.15245,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10418,0.34679,0.32856]},{"body_a":"world","body_b":"door_panel","contact_count":564.0,"contact_point_centroid":[0.33582,0.08535,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17403,0.27809,0.26045]},{"body_a":"world","body_b":"door_panel","contact_count":816.0,"contact_point_centroid":[0.34806,0.07083,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.1745,0.18283,0.27244]}],"total_contact_groups":10},"final_pose_error":0.25859,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.17715,0.09549,0.31756],"hinge_angle":0.84144,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1613.54416,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.98345,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1941.0,"raw_peak_contact_force":1613.54416,"tcp_end":[0.15759,0.26407,0.37504],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.485,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":108.03528,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":348.08878,"tcp_end":[0.15775,0.26392,0.37565],"tcp_start":[0.15759,0.26407,0.37504],"tcp_to_object_dist_end":0.48544,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":571.0,"raw_peak_contact_force":541.91354,"tcp_end":[0.17637,0.266,0.22643],"tcp_start":[0.15775,0.26392,0.37565],"tcp_to_object_dist_end":0.39132,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1222.0,"raw_peak_contact_force":41.09983,"tcp_end":[0.17715,0.09549,0.31756],"tcp_start":[0.17637,0.266,0.22643],"tcp_to_object_dist_end":0.37596,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.31522,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_time":10.02852,"approach_1.speed":0.13177,"contact_1.force_threshold":16.501,"contact_1.speed":0.04406,"push_1.push_depth":0.30217,"push_1.push_time":10.99265,"push_1.speed":0.05986,"retract_1.retract_speed":0.10661,"retract_1.retract_time":6.13126},"optimized_scores":{"best_composite_score":1.49,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":865.0,"contact_point_centroid":[0.11765,0.09469,0.59304],"force_p95":681.13308,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1447.20844,"mean_force":361.22787,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11515,0.33501,0.33521]},{"body_a":"door_panel","body_b":"link5","contact_count":252.0,"contact_point_centroid":[0.10331,0.1572,0.56531],"force_p95":521.3816,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1124.67353,"mean_force":293.01698,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10327,0.40437,0.33523]},{"body_a":"door_panel","body_b":"link4","contact_count":165.0,"contact_point_centroid":[0.25877,-0.11361,0.53819],"force_p95":187.11902,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":967.3055,"mean_force":62.53361,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17176,0.27777,0.3259]},{"body_a":"link1","body_b":"link5","contact_count":910.0,"contact_point_centroid":[0.10528,0.02565,0.35898],"force_p95":359.66968,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":743.25677,"mean_force":259.84199,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.24844,0.17693,0.33308]},{"body_a":"link1","body_b":"link5","contact_count":302.0,"contact_point_centroid":[0.06915,0.0951,0.35418],"force_p95":440.25009,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":577.77083,"mean_force":246.82077,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17189,0.27814,0.32959]},{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.16842,-0.0234,0.54674],"force_p95":322.07584,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":323.04061,"mean_force":282.75003,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.16991,0.24605,0.38842]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.16765,-0.02218,0.54719],"force_p95":196.37109,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.37109,"mean_force":196.37109,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.16914,0.24673,0.38707]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.16733,-0.02204,0.57982],"force_p95":196.27306,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.27306,"mean_force":196.27306,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.16914,0.24673,0.38707]},{"body_a":"world","body_b":"door_panel","contact_count":1040.0,"contact_point_centroid":[0.31083,0.14047,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11508,0.33951,0.33525]},{"body_a":"world","body_b":"door_panel","contact_count":388.0,"contact_point_centroid":[0.37437,0.04801,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17499,0.27506,0.32772]},{"body_a":"world","body_b":"door_panel","contact_count":564.0,"contact_point_centroid":[0.41168,0.02031,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.24616,0.17726,0.33354]}],"total_contact_groups":11},"final_pose_error":0.35472,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.27733,0.06931,0.34068],"hinge_angle":1.0391,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1447.20844,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.73785,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2157.0,"raw_peak_contact_force":1447.20844,"tcp_end":[0.16914,0.24673,0.38707],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48919,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":196.37109,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":196.37109,"tcp_end":[0.16947,0.24634,0.38771],"tcp_start":[0.16914,0.24673,0.38707],"tcp_to_object_dist_end":0.48962,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":858.0,"raw_peak_contact_force":967.3055,"tcp_end":[0.17005,0.27658,0.33731],"tcp_start":[0.16947,0.24634,0.38771],"tcp_to_object_dist_end":0.46818,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1474.0,"raw_peak_contact_force":743.25677,"tcp_end":[0.27733,0.06931,0.34068],"tcp_start":[0.17005,0.27658,0.33731],"tcp_to_object_dist_end":0.44473,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```