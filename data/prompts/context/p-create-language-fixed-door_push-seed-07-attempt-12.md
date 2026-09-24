## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | time_limit | 8 | 1.0400 | 1.00 | ❌ rejected |
| 11 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | time_limit | 8 | 1.0400 | 1.00 | ❌ rejected |
| 10 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | time_limit | 8 | 0.8733 | 1.00 | ❌ rejected |
| 9 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | time_limit | 8 | 1.0400 | 1.00 | ✅ accepted |
| 8 | approach → contact → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.7900 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`
- Frozen initial hinge angle: 0.044 rad
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
  frozen_initial_hinge_angle_rad: 0.0437
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57

## Current Skill (Q=1.040) — your mutation base

```yaml
skill: door_push
dsl_version: 2
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
    - 0.1
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
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
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push1_distance:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.22
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push1_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_2
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
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push2_distance:
      type: scalar
      range:
      - 0.02
      - 0.5
      default: 0.22
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push2_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.1, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.12, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push1_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push1_speed: status=consumed; consumers=generator.speed (replace)
- **push_2** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push2_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push2_speed: status=consumed; consumers=generator.speed (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 1.040
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.67 | 0.1246 |
| contact_1 | 1.00 | 1.00 | 0.0608 |
| push_1 | 1.00 | 1.00 | 0.1060 |
| push_2 | 1.00 | 0.67 | 0.0992 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.275, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 0.000 |
| contact_1 | contact | 1.00 / force_exceeded | (0.102, 0.275, 0.348)→(0.101, 0.214, 0.346) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 2118.989 | 11.572 |
| push_1 | push | 1.00 / time_limit | (0.101, 0.214, 0.346)→(0.100, 0.118, 0.391) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 11.434 | 27.245 |
| push_2 | push | 1.00 / time_limit | (0.100, 0.118, 0.391)→(0.102, 0.024, 0.414) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 5.571 | 29.635 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.040
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 5.0
- **Final σ (mean)**: 0.318


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69061,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05734,"contact_1.contact_force":10.25791,"contact_1.contact_speed":0.02268,"push_1.push1_distance":0.2119,"push_1.push1_speed":0.04532,"push_2.push2_distance":0.25187,"push_2.push2_speed":0.07125,"push_2.push_duration":3.1577},"optimized_scores":{"best_composite_score":1.04,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":679.0,"contact_point_centroid":[0.16364,0.02298,0.43777],"force_p95":27.63476,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.507,"mean_force":13.0046,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09747,0.07904,0.40885]},{"body_a":"door_panel","body_b":"link7","contact_count":635.0,"contact_point_centroid":[0.16561,0.11334,0.37908],"force_p95":16.54091,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.6024,"mean_force":12.85381,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1003,0.17053,0.35471]},{"body_a":"door_panel","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.10316,0.15,0.45059],"force_p95":10.68511,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.73766,"mean_force":6.64382,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10038,0.21663,0.34498]},{"body_a":"door_panel","body_b":"link6","contact_count":263.0,"contact_point_centroid":[0.10131,0.16888,0.45304],"force_p95":8.9473,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.26184,"mean_force":7.35959,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10051,0.24051,0.34598]},{"body_a":"world","body_b":"door_panel","contact_count":540.0,"contact_point_centroid":[0.30062,0.1814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10024,0.33175,0.34783]},{"body_a":"world","body_b":"door_panel","contact_count":392.0,"contact_point_centroid":[0.30132,0.17545,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10054,0.24478,0.34617]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.3093,0.14038,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10032,0.1705,0.35525]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.32786,0.09904,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09767,0.07921,0.40792]}],"total_contact_groups":8},"final_pose_error":0.13631,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10106,0.01631,0.41598],"hinge_angle":0.61566,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":33.507,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10086,0.27213,0.34793],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.26184,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":655.0,"raw_peak_contact_force":10.26184,"tcp_end":[0.10054,0.22226,0.34602],"tcp_start":[0.10086,0.27213,0.34793],"tcp_to_object_dist_end":0.42336,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.11559,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1799.0,"raw_peak_contact_force":24.6024,"tcp_end":[0.09979,0.13663,0.38028],"tcp_start":[0.10054,0.22226,0.34602],"tcp_to_object_dist_end":0.41622,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1627.0,"raw_peak_contact_force":33.507,"tcp_end":[0.10106,0.01631,0.41598],"tcp_start":[0.09979,0.13663,0.38028],"tcp_to_object_dist_end":0.42839,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57513,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06001,"contact_1.contact_force":11.59185,"contact_1.contact_speed":0.02815,"push_1.push1_distance":0.22545,"push_1.push1_speed":0.04357,"push_2.push2_distance":0.18084,"push_2.push2_speed":0.03448,"push_2.push_duration":3.11281},"optimized_scores":{"best_composite_score":1.04,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":671.0,"contact_point_centroid":[0.16391,0.11188,0.38056],"force_p95":17.37431,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.50018,"mean_force":12.74109,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09858,0.16905,0.35617]},{"body_a":"door_panel","body_b":"link7","contact_count":731.0,"contact_point_centroid":[0.16167,0.04839,0.42988],"force_p95":12.96139,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.40153,"mean_force":11.05427,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09586,0.10524,0.40156]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.16421,0.15626,0.36995],"force_p95":13.93853,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.06636,"mean_force":11.80315,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09889,0.21357,0.34583]},{"body_a":"door_panel","body_b":"link6","contact_count":666.0,"contact_point_centroid":[0.10084,0.18636,0.45334],"force_p95":9.64611,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.72942,"mean_force":7.19474,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09878,0.26005,0.34571]},{"body_a":"world","body_b":"door_panel","contact_count":388.0,"contact_point_centroid":[0.29976,0.20198,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09939,0.3548,0.34783]},{"body_a":"world","body_b":"door_panel","contact_count":1008.0,"contact_point_centroid":[0.30068,0.18494,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0988,0.26463,0.34581]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.30979,0.13863,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09857,0.16662,0.35743]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.32183,0.10895,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09581,0.10438,0.40192]}],"total_contact_groups":8},"final_pose_error":0.12717,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09419,0.07645,0.4149],"hinge_angle":0.48786,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":24.50018,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":388.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09918,0.31376,0.34771],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.17407,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1678.0,"raw_peak_contact_force":14.06636,"tcp_end":[0.0989,0.21327,0.34583],"tcp_start":[0.09918,0.31376,0.34771],"tcp_to_object_dist_end":0.41817,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.41722,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1595.0,"raw_peak_contact_force":24.50018,"tcp_end":[0.09771,0.13422,0.38306],"tcp_start":[0.0989,0.21327,0.34583],"tcp_to_object_dist_end":0.41749,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.88636,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1659.0,"raw_peak_contact_force":24.40153,"tcp_end":[0.09419,0.07645,0.4149],"tcp_start":[0.09771,0.13422,0.38306],"tcp_to_object_dist_end":0.43227,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18831,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07251,"contact_1.contact_force":10.64501,"contact_1.contact_speed":0.02421,"push_1.push1_distance":0.34116,"push_1.push1_speed":0.07781,"push_2.push2_distance":0.23115,"push_2.push2_speed":0.06372,"push_2.push_duration":2.29053},"optimized_scores":{"best_composite_score":1.04,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":687.0,"contact_point_centroid":[0.16981,0.09094,0.39528],"force_p95":19.8168,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.63114,"mean_force":13.74514,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10449,0.14812,0.36937]},{"body_a":"door_panel","body_b":"link7","contact_count":599.0,"contact_point_centroid":[0.17236,-0.01834,0.4463],"force_p95":26.5513,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.99692,"mean_force":13.09219,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.10363,0.03324,0.41784]},{"body_a":"door_panel","body_b":"link6","contact_count":103.0,"contact_point_centroid":[0.10386,0.14478,0.45267],"force_p95":10.04696,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.38828,"mean_force":7.69681,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10502,0.214,0.3462]},{"body_a":"world","body_b":"door_panel","contact_count":736.0,"contact_point_centroid":[0.30289,0.16469,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1024,0.31919,0.34793]},{"body_a":"world","body_b":"door_panel","contact_count":300.0,"contact_point_centroid":[0.30304,0.16389,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10506,0.22232,0.34648]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10472,0.13877,0.45207],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10502,0.20632,0.34621]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.31394,0.12814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10455,0.14727,0.36956]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.34004,0.08021,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.10412,0.03018,0.41738]}],"total_contact_groups":8},"final_pose_error":0.1257,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11061,-0.02175,0.41242],"hinge_angle":0.69046,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":6334.53249,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10532,0.23841,0.34809],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6334.53249,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":403.0,"raw_peak_contact_force":10.38828,"tcp_end":[0.10502,0.20632,0.34621],"tcp_start":[0.10532,0.23841,0.34809],"tcp_to_object_dist_end":0.41648,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.76874,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1716.0,"raw_peak_contact_force":32.63114,"tcp_end":[0.10202,0.084,0.41094],"tcp_start":[0.10502,0.20632,0.34621],"tcp_to_object_dist_end":0.43167,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.82589,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1419.0,"raw_peak_contact_force":30.99692,"tcp_end":[0.11061,-0.02175,0.41242],"tcp_start":[0.10202,0.084,0.41094],"tcp_to_object_dist_end":0.42755,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```