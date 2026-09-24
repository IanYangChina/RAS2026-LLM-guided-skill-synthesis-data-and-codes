## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ✅ accepted |
| 11 | approach → approach → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 10 | approach → approach → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 9 | approach → approach → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ✅ accepted |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 7 | -0.2182 | 0.13 | ❌ rejected |

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

## Current Skill (Q=1.120) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_handle
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
    - -0.02
    - 0.35
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.2
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
  guards:
  - id: contact_ok
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: contact_handle
  type: approach
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
    offset_along_axis:
      distance: 0.02
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_distance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 50.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_ok2
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
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
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_ok3
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: continue

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.2
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - guards:
    - id=contact_ok, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **contact_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_ok2, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_door** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_ok3, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.0

## Design Metrics

- **Composite score**: 1.120
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.00 | 1.00 | 0.1376 |
| contact_handle | 1.00 | 1.00 | 0.0253 |
| push_door | 1.00 | 1.00 | 0.3285 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.095, 0.284, 0.358) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 194.647 | 1330.126 |
| contact_handle | approach | 1.00 / force_exceeded | (0.095, 0.284, 0.358)→(0.107, 0.264, 0.367) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.667 | 193.623 | 462.022 |
| push_door | push | 1.00 / time_limit | (0.107, 0.264, 0.367)→(0.175, -0.012, 0.390) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 1569.301 | 1088.623 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.273


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.4,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.10554,"approach_handle.arc_height":0.26203,"contact_handle.contact_distance":0.0257,"contact_handle.contact_force_threshold":26.89356,"push_door.push_distance":0.34347,"push_door.push_duration":3.19669,"push_door.push_speed":0.13622},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":964.0,"contact_point_centroid":[0.10634,0.13753,0.55584],"force_p95":732.2289,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1439.02198,"mean_force":575.69069,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.07777,0.34983,0.34555]},{"body_a":"door_panel","body_b":"link5","contact_count":456.0,"contact_point_centroid":[0.11945,0.08118,0.55286],"force_p95":1087.47558,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1236.02674,"mean_force":757.10338,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.01627,0.29409,0.36308]},{"body_a":"link1","body_b":"link5","contact_count":552.0,"contact_point_centroid":[0.0733,0.00625,0.36822],"force_p95":450.26868,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":702.98216,"mean_force":283.82101,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12828,0.20598,0.43031]},{"body_a":"door_panel","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.10731,0.12322,0.543],"force_p95":339.65421,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":357.53075,"mean_force":178.76537,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.00045,0.31534,0.33324]},{"body_a":"door_panel","body_b":"link6","contact_count":264.0,"contact_point_centroid":[0.21416,0.02,0.41207],"force_p95":27.37325,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.61014,"mean_force":17.94932,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14776,0.18889,0.445]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.30349,0.16486,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.08005,0.35483,0.34565]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.32139,0.11558,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.07309,0.24954,0.39673]}],"total_contact_groups":7},"final_pose_error":0.34031,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18855,0.13776,0.48126],"hinge_angle":0.68885,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":4070.78456,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":558.24281,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2000.0,"raw_peak_contact_force":1439.02198,"tcp_end":[0.00057,0.31536,0.33324],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45881,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":357.53075,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":357.53075,"tcp_end":[0.0001,0.31529,0.33326],"tcp_start":[0.00057,0.31536,0.33324],"tcp_to_object_dist_end":0.45878,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4070.78456,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2092.0,"raw_peak_contact_force":1236.02674,"tcp_end":[0.18855,0.13776,0.48126],"tcp_start":[0.0001,0.31529,0.33326],"tcp_to_object_dist_end":0.53492,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.81111,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.10994,"approach_handle.arc_height":0.17181,"contact_handle.contact_distance":0.02268,"contact_handle.contact_force_threshold":22.99093,"push_door.push_distance":0.25698,"push_door.push_duration":2.67376,"push_door.push_speed":0.13931},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":400.0,"contact_point_centroid":[0.10312,0.1562,0.56126],"force_p95":552.32236,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1362.24544,"mean_force":416.29585,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.08971,0.39517,0.33965]},{"body_a":"door_panel","body_b":"link4","contact_count":651.0,"contact_point_centroid":[0.13609,0.05108,0.58957],"force_p95":622.06108,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1045.57909,"mean_force":378.39712,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.11382,0.3187,0.36058]},{"body_a":"link1","body_b":"link5","contact_count":912.0,"contact_point_centroid":[0.07272,-0.01496,0.37664],"force_p95":223.80756,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":417.85886,"mean_force":162.04269,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.26769,0.05647,0.4245]},{"body_a":"link1","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.06931,0.0279,0.37025],"force_p95":209.40957,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":210.01181,"mean_force":151.84095,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.20443,0.20008,0.40876]},{"body_a":"door_panel","body_b":"link7","contact_count":279.0,"contact_point_centroid":[0.32799,-0.03656,0.42762],"force_p95":41.51241,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.51094,"mean_force":26.83246,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.27969,0.03913,0.42534]},{"body_a":"world","body_b":"door_panel","contact_count":952.0,"contact_point_centroid":[0.31422,0.13705,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10418,0.34962,0.35435]},{"body_a":"door_panel","body_b":"link4","contact_count":3.0,"contact_point_centroid":[0.2082,-0.07344,0.57736],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.1697,0.25973,0.38124]},{"body_a":"world","body_b":"door_panel","contact_count":336.0,"contact_point_centroid":[0.36041,0.05642,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.18919,0.23197,0.39911]},{"body_a":"world","body_b":"door_panel","contact_count":608.0,"contact_point_centroid":[0.38187,0.04066,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.26446,0.06632,0.42356]}],"total_contact_groups":9},"final_pose_error":0.20637,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.27689,-0.10713,0.45193],"hinge_angle":1.0693,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1362.24544,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":23.46297,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2003.0,"raw_peak_contact_force":1362.24544,"tcp_end":[0.16939,0.25994,0.38132],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":457.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":210.01181,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":342.0,"raw_peak_contact_force":210.01181,"tcp_end":[0.2047,0.19959,0.40878],"tcp_start":[0.16939,0.25994,0.38132],"tcp_to_object_dist_end":0.49884,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.70711,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1799.0,"raw_peak_contact_force":417.85886,"tcp_end":[0.27689,-0.10713,0.45193],"tcp_start":[0.2047,0.19959,0.40878],"tcp_to_object_dist_end":0.54072,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.06494,"average_mean_iterations":22.44156,"average_solve_count":77.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.12643,"approach_handle.arc_height":0.18147,"contact_handle.contact_distance":0.02838,"contact_handle.contact_force_threshold":11.77421,"push_door.push_distance":0.23164,"push_door.push_duration":2.95432,"push_door.push_speed":0.12492},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":668.0,"contact_point_centroid":[0.04275,-0.00231,0.3349],"force_p95":803.84103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1611.9832,"mean_force":329.55934,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.17283,0.11541,0.32093]},{"body_a":"door_panel","body_b":"link5","contact_count":977.0,"contact_point_centroid":[0.10723,0.1378,0.53749],"force_p95":707.49639,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1189.11037,"mean_force":507.53593,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.08701,0.33625,0.35913]},{"body_a":"link1","body_b":"link6","contact_count":204.0,"contact_point_centroid":[-0.02225,-0.05495,0.15962],"force_p95":805.15024,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1084.48593,"mean_force":660.15851,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.06552,-0.06272,0.23607]},{"body_a":"link1","body_b":"link5","contact_count":41.0,"contact_point_centroid":[0.05074,0.06012,0.36337],"force_p95":657.48753,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":880.86509,"mean_force":299.83018,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10333,0.27773,0.36307]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.16726,0.10217,0.32047],"force_p95":818.52323,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":818.52323,"mean_force":818.52323,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.11528,0.27761,0.35882]},{"body_a":"door_panel","body_b":"link6","contact_count":740.0,"contact_point_centroid":[0.11804,0.16154,0.36361],"force_p95":558.28579,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":758.70611,"mean_force":335.12296,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.08873,0.34172,0.36048]},{"body_a":"link1","body_b":"link7","contact_count":121.0,"contact_point_centroid":[0.02581,-0.04759,0.22045],"force_p95":609.63517,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":698.927,"mean_force":365.47161,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.06487,-0.05956,0.23636]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.12185,0.06817,0.48072],"force_p95":643.14062,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":643.14062,"mean_force":643.14062,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.11528,0.27761,0.35882]},{"body_a":"door_panel","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.12199,0.06775,0.48067],"force_p95":287.18909,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":312.58407,"mean_force":120.79382,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11599,0.27746,0.35964]},{"body_a":"link1","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.05215,0.05918,0.36924],"force_p95":300.21505,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.21505,"mean_force":300.21505,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"approach","tcp_position_centroid":[0.11528,0.27761,0.35882]},{"body_a":"door_panel","body_b":"link6","contact_count":384.0,"contact_point_centroid":[0.23285,0.04439,0.37173],"force_p95":49.84288,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":252.309,"mean_force":27.31908,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.19406,0.21902,0.35944]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.30348,0.17058,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09085,0.3401,0.35471]},{"body_a":"world","body_b":"door_panel","contact_count":856.0,"contact_point_centroid":[0.36593,0.06335,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.16775,0.11037,0.31705]}],"total_contact_groups":13},"final_pose_error":0.12022,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.06101,-0.06676,0.23729],"hinge_angle":1.01381,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1611.9832,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":2.23607,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2750.0,"raw_peak_contact_force":1189.11037,"tcp_end":[0.11528,0.27761,0.35882],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46809,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.32637,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":818.52323,"tcp_end":[0.11547,0.27759,0.35904],"tcp_start":[0.11528,0.27761,0.35882],"tcp_to_object_dist_end":0.46829,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":636.41179,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2237.0,"raw_peak_contact_force":1611.9832,"tcp_end":[0.06101,-0.06676,0.23729],"tcp_start":[0.11547,0.27759,0.35904],"tcp_to_object_dist_end":0.25394,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```