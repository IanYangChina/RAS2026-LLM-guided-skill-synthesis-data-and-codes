## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.5900 | 1.00 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.5900 | 1.00 | ✅ accepted |
| 10 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.4649 | 0.92 | ❌ rejected |
| 9 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.4974 | 0.96 | ❌ rejected |
| 8 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.5025 | 0.96 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`
- Frozen initial hinge angle: 0.129 rad
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
  frozen_initial_hinge_angle_rad: 0.1292
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5

## Current Skill (Q=0.590) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: hinge_progress
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
    - 0.0
    - 0.12
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: align_1
  type: align
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
    - 0.0
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    contact_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
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
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 28.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.08
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.12], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_offset_x: status=consumed; consumers=target.offset.x (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=28.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.590
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2445 |
| align_1 | 0.33 | 0.67 | 0.1148 |
| push_1 | 0.67 | 0.00 | 0.0606 |
| retract_1 | 1.00 | 0.33 | 0.1111 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.106, 0.199, 0.483) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 9.046 | 56.557 |
| align_1 | align | 0.33 / step_budget | (0.106, 0.199, 0.483)→(0.095, 0.122, 0.403) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 18.674 | 62.150 |
| push_1 | push | 0.67 / time_limit | (0.097, 0.096, 0.399)→(0.110, 0.038, 0.391) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 27.364 |
| retract_1 | retract | 1.00 / step_budget | (0.110, 0.038, 0.391)→(0.110, 0.038, 0.502) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 16.481 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.590
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.331


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d324a70682be50916187e25da5a0a59a7678607fbe49b53fdc39aa246f41ddf9`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d82b7d31aa43f8d3a4479d5f34069ef44e70dc4ca62021414a1e013fa43805ad`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55507,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.contact_offset_x":-0.02787,"approach_1.approach_offset_z":0.14422,"approach_1.speed":0.05527,"push_1.push_distance":0.14831,"push_1.push_speed":0.05919,"retract_1.retract_offset_z":0.14599,"retract_1.speed":0.06588},"optimized_scores":{"best_composite_score":0.59,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":112.0,"contact_point_centroid":[0.15959,0.06071,0.4459],"force_p95":47.18617,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.84568,"mean_force":21.01236,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09428,0.11808,0.41907]},{"body_a":"door_panel","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.17203,0.13357,0.48607],"force_p95":42.42713,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.09012,"mean_force":34.0893,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10697,0.19089,0.46162]},{"body_a":"door_panel","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.10394,0.14584,0.5555],"force_p95":40.5747,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.99317,"mean_force":32.77858,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10665,0.21427,0.44916]},{"body_a":"door_panel","body_b":"link7","contact_count":749.0,"contact_point_centroid":[0.16391,-0.01147,0.43192],"force_p95":16.84679,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.32877,"mean_force":11.00512,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09899,0.04461,0.40382]},{"body_a":"door_panel","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.18642,-0.04832,0.48609],"force_p95":15.32794,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.33846,"mean_force":15.16093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11153,-0.00132,0.46843]},{"body_a":"world","body_b":"door_panel","contact_count":320.0,"contact_point_centroid":[0.30332,0.1627,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10437,0.29209,0.40655]},{"body_a":"world","body_b":"door_panel","contact_count":144.0,"contact_point_centroid":[0.31826,0.11676,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.0949,0.12098,0.4224]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.33622,0.0854,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09889,0.04488,0.40398]},{"body_a":"world","body_b":"door_panel","contact_count":212.0,"contact_point_centroid":[0.34945,0.06796,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11155,-0.0013,0.45805]}],"total_contact_groups":9},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11151,-0.00131,0.52121],"hinge_angle":0.66983,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":61.84568,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":356.0,"raw_peak_contact_force":44.09012,"tcp_end":[0.10724,0.17278,0.47131],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":212.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":256.0,"raw_peak_contact_force":61.84568,"tcp_end":[0.08655,0.09302,0.40843],"tcp_start":[0.10724,0.17278,0.47131],"tcp_to_object_dist_end":0.42773,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1597.0,"raw_peak_contact_force":26.32877,"tcp_end":[0.11184,-0.0011,0.39511],"tcp_start":[0.08655,0.09302,0.40843],"tcp_to_object_dist_end":0.41064,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":229.0,"raw_peak_contact_force":15.33846,"tcp_end":[0.11151,-0.00131,0.52121],"tcp_start":[0.11184,-0.0011,0.39511],"tcp_to_object_dist_end":0.533,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70952,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.contact_offset_x":-0.01221,"approach_1.approach_offset_z":0.13045,"approach_1.speed":0.08311,"push_1.push_distance":0.18836,"push_1.push_speed":0.02871,"retract_1.retract_offset_z":0.14057,"retract_1.speed":0.0437},"optimized_scores":{"best_composite_score":0.59,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.17479,0.04722,0.44277],"force_p95":47.94556,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.61177,"mean_force":20.96371,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10955,0.10469,0.41487]},{"body_a":"door_panel","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.17381,0.12813,0.4741],"force_p95":46.92116,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.54158,"mean_force":33.96239,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10885,0.18519,0.44952]},{"body_a":"door_panel","body_b":"link7","contact_count":682.0,"contact_point_centroid":[0.17698,-0.02137,0.43399],"force_p95":16.42492,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.75795,"mean_force":11.94361,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11651,0.03977,0.40424]},{"body_a":"door_panel","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.19197,-0.05519,0.48982],"force_p95":17.09846,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.1576,"mean_force":15.97169,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.12376,-0.00158,0.46682]},{"body_a":"door_panel","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.10545,0.13511,0.54785],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10844,0.20214,0.44175]},{"body_a":"world","body_b":"door_panel","contact_count":312.0,"contact_point_centroid":[0.30447,0.157,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10524,0.28838,0.40081]},{"body_a":"world","body_b":"door_panel","contact_count":228.0,"contact_point_centroid":[0.32283,0.10769,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.1095,0.10743,0.41823]},{"body_a":"world","body_b":"door_panel","contact_count":832.0,"contact_point_centroid":[0.34089,0.07891,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1166,0.03931,0.40412]},{"body_a":"world","body_b":"door_panel","contact_count":292.0,"contact_point_centroid":[0.35241,0.06466,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.12378,-0.00156,0.45539]}],"total_contact_groups":9},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12375,-0.00158,0.51759],"hinge_angle":0.69181,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":66.61177,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":27.13926,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":354.0,"raw_peak_contact_force":53.54158,"tcp_end":[0.10943,0.16219,0.46013],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":204.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.9445,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":355.0,"raw_peak_contact_force":66.61177,"tcp_end":[0.10951,0.07993,0.40816],"tcp_start":[0.10943,0.16219,0.46013],"tcp_to_object_dist_end":0.43009,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1514.0,"raw_peak_contact_force":27.75795,"tcp_end":[0.12407,-0.00137,0.39678],"tcp_start":[0.10951,0.07993,0.40816],"tcp_to_object_dist_end":0.41573,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":306.0,"raw_peak_contact_force":17.1576,"tcp_end":[0.12375,-0.00158,0.51759],"tcp_start":[0.12407,-0.00137,0.39678],"tcp_to_object_dist_end":0.53218,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.12965,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3399,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.contact_offset_x":-0.01501,"approach_1.approach_offset_z":0.20438,"approach_1.speed":0.06133,"push_1.push_distance":0.22151,"push_1.push_speed":0.06571,"retract_1.retract_offset_z":0.10612,"retract_1.speed":0.04762},"optimized_scores":{"best_composite_score":0.59,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":38.0,"contact_point_centroid":[0.10063,0.21457,0.58766],"force_p95":60.49882,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.03905,"mean_force":45.9366,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10233,0.29488,0.47733]},{"body_a":"door_panel","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.10089,0.17457,0.58762],"force_p95":55.73633,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.99109,"mean_force":42.09121,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09775,0.24325,0.48166]},{"body_a":"door_panel","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.15707,0.15352,0.44824],"force_p95":45.41289,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.66929,"mean_force":38.21558,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09167,0.21055,0.42378]},{"body_a":"door_panel","body_b":"link7","contact_count":477.0,"contact_point_centroid":[0.1528,0.09296,0.41135],"force_p95":18.23003,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.00519,"mean_force":12.94141,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09111,0.15345,0.38547]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.15261,0.05279,0.47414],"force_p95":16.78298,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.94805,"mean_force":16.1095,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09349,0.11616,0.44372]},{"body_a":"world","body_b":"door_panel","contact_count":212.0,"contact_point_centroid":[0.30001,0.20582,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.102,0.33879,0.42248]},{"body_a":"world","body_b":"door_panel","contact_count":152.0,"contact_point_centroid":[0.30211,0.17067,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09502,0.22841,0.45545]},{"body_a":"world","body_b":"door_panel","contact_count":540.0,"contact_point_centroid":[0.3121,0.13191,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09111,0.15343,0.38544]},{"body_a":"world","body_b":"door_panel","contact_count":224.0,"contact_point_centroid":[0.31982,0.11263,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09354,0.11614,0.42214]}],"total_contact_groups":9},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09346,0.1162,0.46662],"hinge_angle":0.40109,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":72.03905,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":250.0,"raw_peak_contact_force":72.03905,"tcp_end":[0.10199,0.26348,0.51658],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.58879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":43.07834,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":194.0,"raw_peak_contact_force":57.99109,"tcp_end":[0.08851,0.19257,0.39264],"tcp_start":[0.10199,0.26348,0.51658],"tcp_to_object_dist_end":0.44619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1017.0,"raw_peak_contact_force":28.00519,"tcp_end":[0.09372,0.1164,0.38035],"tcp_start":[0.09373,0.11641,0.38039],"tcp_to_object_dist_end":0.40866,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":228.0,"raw_peak_contact_force":16.94805,"tcp_end":[0.09346,0.1162,0.46662],"tcp_start":[0.09372,0.1164,0.38035],"tcp_to_object_dist_end":0.48987,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```