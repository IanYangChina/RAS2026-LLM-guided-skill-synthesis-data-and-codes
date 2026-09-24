## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 1.0533 | 1.00 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 1.0533 | 1.00 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 1.0033 | 1.00 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 1.0533 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 1.0533 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`
- Frozen initial hinge angle: -0.083 rad
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
  frozen_initial_hinge_angle_rad: -0.0832
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d

## Current Skill (Q=1.053) — your mutation base

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
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 30.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
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
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: world_x
      tolerance: 0.05
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=world_x, tolerance=0.05
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.053
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.33 | 0.2590 |
| contact_1 | 1.00 | 1.00 | 0.0090 |
| push_1 | 1.00 | 0.67 | 0.2569 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.103, 0.204, 0.518) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 5.372 | 55.389 |
| contact_1 | contact | 1.00 / force_exceeded | (0.103, 0.204, 0.518)→(0.103, 0.200, 0.510) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 18.943 | 20.453 |
| push_1 | push | 1.00 / step_budget | (0.103, 0.200, 0.510)→(0.292, 0.115, 0.359) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 4.000 | 0.212 | 346.946 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.053
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 3.7
- **Final σ (mean)**: 0.260


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7dec7b9d265217827596e50fcdf4f13e307fabe21fe4cab198e2a5d141ff1ba8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2703841599a88ffb6fe3c9276875d1c87ae4a75b7467b1c48183ebe23e97d755`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99057,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17181,"approach_1.approach_speed":0.12052,"contact_1.contact_force_threshold":18.50394,"push_1.push_distance":0.18016,"push_1.push_speed":0.09012},"optimized_scores":{"best_composite_score":1.05333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":345.0,"contact_point_centroid":[0.17739,0.10685,0.5493],"force_p95":98.58379,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":331.35988,"mean_force":28.47351,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.19584,0.17724,0.42018]},{"body_a":"door_panel","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.14692,0.0119,0.6161],"force_p95":218.18336,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":225.72783,"mean_force":155.22913,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.27236,0.14212,0.35745]},{"body_a":"door_panel","body_b":"link6","contact_count":135.0,"contact_point_centroid":[0.10062,0.19625,0.5729],"force_p95":36.71023,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.05556,"mean_force":24.972,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09967,0.27146,0.4652]},{"body_a":"door_panel","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.10224,0.15783,0.60874],"force_p95":19.85997,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.01534,"mean_force":15.0678,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09948,0.22484,0.50366]},{"body_a":"world","body_b":"door_panel","contact_count":616.0,"contact_point_centroid":[0.30013,0.19743,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09988,0.313,0.42676]},{"body_a":"world","body_b":"door_panel","contact_count":48.0,"contact_point_centroid":[0.30216,0.16904,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09949,0.22518,0.50437]},{"body_a":"world","body_b":"door_panel","contact_count":780.0,"contact_point_centroid":[0.31021,0.13901,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17795,0.18501,0.43506]}],"total_contact_groups":7},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.27284,0.14195,0.35714],"hinge_angle":0.45952,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":331.35988,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":751.0,"raw_peak_contact_force":79.05556,"tcp_end":[0.09961,0.22668,0.50707],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":46.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.01534,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":58.0,"raw_peak_contact_force":20.01534,"tcp_end":[0.09951,0.22327,0.50046],"tcp_start":[0.09961,0.22668,0.50707],"tcp_to_object_dist_end":0.55696,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.31885,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1129.0,"raw_peak_contact_force":331.35988,"tcp_end":[0.27284,0.14195,0.35714],"tcp_start":[0.09951,0.22327,0.50046],"tcp_to_object_dist_end":0.47132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58861,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1813,"approach_1.approach_speed":0.06025,"contact_1.contact_force_threshold":12.48025,"push_1.push_distance":0.17407,"push_1.push_speed":0.07186},"optimized_scores":{"best_composite_score":1.05333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":59.0,"contact_point_centroid":[0.13576,0.03425,0.62012],"force_p95":627.48803,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":629.42679,"mean_force":494.06486,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.26301,0.16339,0.3619]},{"body_a":"door_panel","body_b":"link6","contact_count":377.0,"contact_point_centroid":[0.17507,0.12419,0.5485],"force_p95":534.52696,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":575.75486,"mean_force":104.43717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.19822,0.19578,0.41974]},{"body_a":"door_panel","body_b":"link6","contact_count":119.0,"contact_point_centroid":[0.10054,0.20857,0.58182],"force_p95":37.47204,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.43803,"mean_force":25.91054,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10063,0.28694,0.47306]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10075,0.1757,0.61854],"force_p95":13.71317,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.71317,"mean_force":13.71317,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10075,0.24791,0.51159]},{"body_a":"world","body_b":"door_panel","contact_count":512.0,"contact_point_centroid":[0.30004,0.20208,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1005,0.32356,0.43177]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30097,0.17789,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10076,0.24858,0.51302]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.30773,0.14757,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1848,0.2023,0.43213]}],"total_contact_groups":7},"final_pose_error":0.01815,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.2654,0.16304,0.36276],"hinge_angle":0.38604,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":629.42679,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":631.0,"raw_peak_contact_force":55.43803,"tcp_end":[0.10094,0.24986,0.51533],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.58154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.71317,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":21.0,"raw_peak_contact_force":13.71317,"tcp_end":[0.10074,0.24785,0.51146],"tcp_start":[0.10094,0.24986,0.51533],"tcp_to_object_dist_end":0.57721,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.31754,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1316.0,"raw_peak_contact_force":629.42679,"tcp_end":[0.2654,0.16304,0.36276],"tcp_start":[0.10074,0.24785,0.51146],"tcp_to_object_dist_end":0.47814,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31429,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19312,"approach_1.approach_speed":0.04635,"contact_1.contact_force_threshold":18.76595,"push_1.push_distance":0.21498,"push_1.push_speed":0.12969},"optimized_scores":{"best_composite_score":1.05333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.34466,0.02999,0.3998],"force_p95":51.15392,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.05169,"mean_force":34.01182,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.30722,0.05055,0.37848]},{"body_a":"door_panel","body_b":"link6","contact_count":383.0,"contact_point_centroid":[0.22328,0.01852,0.56348],"force_p95":32.75407,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.78262,"mean_force":20.32461,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.22427,0.0821,0.43579]},{"body_a":"door_panel","body_b":"link7","contact_count":146.0,"contact_point_centroid":[0.17169,0.11367,0.52863],"force_p95":28.68606,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.67237,"mean_force":20.40104,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10634,0.17107,0.5049]},{"body_a":"door_panel","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.1734,0.07317,0.54693],"force_p95":23.36505,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.63017,"mean_force":14.76371,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10801,0.13056,0.52319]},{"body_a":"door_panel","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.10466,0.13952,0.5856],"force_p95":13.85532,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.47376,"mean_force":3.07896,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10547,0.20684,0.48031]},{"body_a":"world","body_b":"door_panel","contact_count":836.0,"contact_point_centroid":[0.30518,0.15484,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1036,0.27235,0.4349]},{"body_a":"world","body_b":"door_panel","contact_count":100.0,"contact_point_centroid":[0.31712,0.11843,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10793,0.13092,0.52401]},{"body_a":"world","body_b":"door_panel","contact_count":676.0,"contact_point_centroid":[0.34032,0.08354,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.21141,0.08521,0.44519]}],"total_contact_groups":8},"final_pose_error":0.01494,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.33852,0.03867,0.35668],"hinge_angle":0.95907,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":80.05169,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.11726,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":988.0,"raw_peak_contact_force":31.67237,"tcp_end":[0.10732,0.13414,0.53054],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.55766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":23.10099,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":139.0,"raw_peak_contact_force":27.63017,"tcp_end":[0.10876,0.12755,0.51697],"tcp_start":[0.10732,0.13414,0.53054],"tcp_to_object_dist_end":0.54347,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1163.0,"raw_peak_contact_force":80.05169,"tcp_end":[0.33852,0.03867,0.35668],"tcp_start":[0.10876,0.12755,0.51697],"tcp_to_object_dist_end":0.49327,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```