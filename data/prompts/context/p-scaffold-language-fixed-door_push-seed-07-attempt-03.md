## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5733 | 1.00 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.6233 | 1.00 | ✅ accepted |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2210 | 0.28 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.0221 | 0.34 | ✅ accepted |

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

## Current Skill (Q=0.573) — your mutation base

```yaml
skill: door_push
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: ''
    offset:
    - 0.02
    - -0.05
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: ''
    offset:
    - 0.01
    - -0.005
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
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
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: ''
    offset:
    - 0.02
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.19
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.19
      binds_to:
      - path: target.offset_along_axis.distance
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
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_during_push
    when: during_phase
    predicate: contact_detected
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: ''
    offset:
    - 0.0
    - -0.1
    - 0.2
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=, offset=[0.02, -0.05, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, entity=, offset=[0.01, -0.005, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=, offset=[0.02, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.19, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_push, when=during_phase, predicate=contact_detected, on_failure=retry
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=, offset=[0.0, -0.1, 0.2], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.573
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.2962 |
| contact_1 | 0.33 | 0.33 | 0.1061 |
| push_1 | 1.00 | 0.33 | 0.1839 |
| retract_1 | 1.00 | 0.00 | 0.1507 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.117, 0.175, 0.542) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 21.894 | 30.709 |
| contact_1 | contact | 0.33 / step_budget | (0.117, 0.175, 0.542)→(0.113, 0.177, 0.436) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 4.882 | 4.417 |
| push_1 | push | 1.00 / step_budget | (0.113, 0.177, 0.436)→(0.123, 0.015, 0.365) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 1.132 | 31.183 |
| retract_1 | retract | 1.00 / step_budget | (0.123, 0.015, 0.365)→(0.109, 0.065, 0.505) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.490
- **K-run variance**: 0.0139
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 2.3
- **Final σ (mean)**: 0.260


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37086,"average_solve_count":302.0,"average_success_count":302.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.15075,"approach_1.speed":0.06229,"approach_1.tolerance":0.03084,"contact_1.force_threshold":14.34356,"contact_1.speed":0.03175,"push_1.push_distance":0.1398,"push_1.speed":0.06012,"push_1.tolerance":0.03188,"retract_1.speed":0.05445},"optimized_scores":{"best_composite_score":0.49,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.14626,0.14455,0.59572],"force_p95":31.61406,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.77732,"mean_force":17.9369,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11299,0.22609,0.56661]},{"body_a":"door_panel","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.16314,0.04356,0.41384],"force_p95":29.82511,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.42151,"mean_force":18.28547,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11637,0.11114,0.37938]},{"body_a":"door_panel","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.1465,0.1001,0.50542],"force_p95":12.63793,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.25238,"mean_force":10.51132,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11361,0.17896,0.47208]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.30132,0.17724,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10395,0.34731,0.49803]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.31028,0.13593,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11366,0.17902,0.47394]},{"body_a":"world","body_b":"door_panel","contact_count":332.0,"contact_point_centroid":[0.32417,0.10572,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11654,0.10816,0.37798]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.19152,-0.00248,0.38869],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.12214,0.05418,0.36406]},{"body_a":"world","body_b":"door_panel","contact_count":92.0,"contact_point_centroid":[0.33837,0.08178,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11674,0.06354,0.42555]}],"total_contact_groups":8},"final_pose_error":0.04908,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10838,0.07464,0.50194],"hinge_angle":0.57943,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":32.77732,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":21.12051,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1078.0,"raw_peak_contact_force":32.77732,"tcp_end":[0.11608,0.18234,0.55072],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59162,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":944.0,"raw_peak_contact_force":13.25238,"tcp_end":[0.1115,0.17614,0.40436],"tcp_start":[0.11608,0.18234,0.55072],"tcp_to_object_dist_end":0.45493,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.39677,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":552.0,"raw_peak_contact_force":31.42151,"tcp_end":[0.12214,0.05418,0.36406],"tcp_start":[0.1115,0.17614,0.40436],"tcp_to_object_dist_end":0.3878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":93.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10838,0.07464,0.50194],"tcp_start":[0.12214,0.05418,0.36406],"tcp_to_object_dist_end":0.5189,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55921,"average_solve_count":304.0,"average_success_count":304.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.14851,"approach_1.speed":0.05113,"approach_1.tolerance":0.04055,"contact_1.force_threshold":6.19155,"contact_1.speed":0.02602,"push_1.push_distance":0.17265,"push_1.speed":0.04428,"push_1.tolerance":0.03056,"retract_1.speed":0.06432},"optimized_scores":{"best_composite_score":0.74,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":222.0,"contact_point_centroid":[0.14649,0.16485,0.59702],"force_p95":27.31929,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.26244,"mean_force":16.67144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11161,0.24517,0.56651]},{"body_a":"door_panel","body_b":"link7","contact_count":345.0,"contact_point_centroid":[0.16541,0.01563,0.45569],"force_p95":23.43288,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.37405,"mean_force":17.77172,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1186,0.08751,0.42917]},{"body_a":"world","body_b":"door_panel","contact_count":1008.0,"contact_point_centroid":[0.30048,0.1946,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1036,0.35199,0.49347]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14457,0.10164,0.57992],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11583,0.18519,0.55125]},{"body_a":"world","body_b":"door_panel","contact_count":212.0,"contact_point_centroid":[0.31005,0.13662,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11532,0.18424,0.53567]},{"body_a":"world","body_b":"door_panel","contact_count":512.0,"contact_point_centroid":[0.32852,0.09925,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11814,0.09609,0.43652]},{"body_a":"world","body_b":"door_panel","contact_count":132.0,"contact_point_centroid":[0.35024,0.06706,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11881,0.03398,0.42491]}],"total_contact_groups":7},"final_pose_error":0.04925,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1092,0.06341,0.50455],"hinge_angle":0.67324,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":30.26244,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.09408,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1230.0,"raw_peak_contact_force":30.26244,"tcp_end":[0.11586,0.18525,0.55131],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.6465,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":214.0,"raw_peak_contact_force":0.0,"tcp_end":[0.11484,0.18332,0.5189],"tcp_start":[0.11586,0.18525,0.55131],"tcp_to_object_dist_end":0.56219,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":857.0,"raw_peak_contact_force":29.37405,"tcp_end":[0.12428,0.01293,0.36869],"tcp_start":[0.11484,0.18332,0.5189],"tcp_to_object_dist_end":0.38929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":132.0,"raw_peak_contact_force":0.0,"tcp_end":[0.1092,0.06341,0.50455],"tcp_start":[0.12428,0.01293,0.36869],"tcp_to_object_dist_end":0.52011,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38974,"average_solve_count":390.0,"average_success_count":390.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.18259,"approach_1.speed":0.05055,"approach_1.tolerance":0.048,"contact_1.force_threshold":17.71065,"contact_1.speed":0.01869,"push_1.push_distance":0.21928,"push_1.speed":0.05473,"push_1.tolerance":0.03469,"retract_1.speed":0.04587},"optimized_scores":{"best_composite_score":0.49,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":228.0,"contact_point_centroid":[0.16954,0.01569,0.40453],"force_p95":31.49166,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.75277,"mean_force":19.42512,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11645,0.07927,0.37253]},{"body_a":"door_panel","body_b":"link7","contact_count":140.0,"contact_point_centroid":[0.14585,0.11702,0.57203],"force_p95":28.08316,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.08842,"mean_force":18.07352,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11503,0.19893,0.54465]},{"body_a":"world","body_b":"door_panel","contact_count":1092.0,"contact_point_centroid":[0.30381,0.16109,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1053,0.32928,0.48743]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14389,0.07433,0.55205],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11795,0.15813,0.52482]},{"body_a":"world","body_b":"door_panel","contact_count":876.0,"contact_point_centroid":[0.31457,0.12441,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11493,0.16357,0.46021]},{"body_a":"world","body_b":"door_panel","contact_count":476.0,"contact_point_centroid":[0.33251,0.09319,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.117,0.07418,0.37271]},{"body_a":"world","body_b":"door_panel","contact_count":136.0,"contact_point_centroid":[0.34981,0.06755,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11692,0.01687,0.43538]}],"total_contact_groups":7},"final_pose_error":0.04996,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10879,0.05606,0.50704],"hinge_angle":0.67006,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":32.75277,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":27.46719,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":29.08842,"tcp_end":[0.11795,0.15813,0.52482],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":877.0,"raw_peak_contact_force":0.0,"tcp_end":[0.11149,0.1703,0.38622],"tcp_start":[0.11795,0.15813,0.52482],"tcp_to_object_dist_end":0.43657,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":704.0,"raw_peak_contact_force":32.75277,"tcp_end":[0.12351,-0.02337,0.36155],"tcp_start":[0.11149,0.1703,0.38622],"tcp_to_object_dist_end":0.38277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":136.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10879,0.05606,0.50704],"tcp_start":[0.12351,-0.02337,0.36155],"tcp_to_object_dist_end":0.5216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```