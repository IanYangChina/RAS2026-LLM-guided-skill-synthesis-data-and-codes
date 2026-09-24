## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.5900 | 1.00 | ❌ rejected |
| 13 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.5900 | 1.00 | ❌ rejected |
| 12 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.5900 | 1.00 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.5900 | 1.00 | ✅ accepted |
| 10 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.4649 | 0.92 | ❌ rejected |

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
| approach_1 | 0.33 | 1.00 | 0.3013 |
| align_1 | 1.00 | 0.67 | 0.1765 |
| push_1 | 0.33 | 0.33 | 0.0404 |
| retract_1 | 1.00 | 0.00 | 0.1241 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.101, 0.170, 0.545) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 81.366 | 227.401 |
| align_1 | align | 1.00 / step_budget | (0.101, 0.170, 0.545)→(0.144, 0.099, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 0.000 | 61.720 |
| push_1 | push | 0.33 / guard_failure | (0.144, 0.097, 0.392)→(0.147, 0.057, 0.386) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 29.493 |
| retract_1 | retract | 1.00 / step_budget | (0.147, 0.057, 0.386)→(0.147, 0.057, 0.510) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 18.541 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.590
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29123,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.contact_offset_x":0.04995,"approach_1.approach_offset_z":0.27208,"approach_1.speed":0.07321,"push_1.push_distance":0.15849,"push_1.push_speed":0.05641,"retract_1.retract_offset_z":0.13893,"retract_1.speed":0.0107},"optimized_scores":{"best_composite_score":0.59,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":129.0,"contact_point_centroid":[0.11819,0.18834,0.75031],"force_p95":269.96836,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.25609,"mean_force":238.33178,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09921,0.15168,0.56693]},{"body_a":"door_panel","body_b":"link7","contact_count":74.0,"contact_point_centroid":[0.2004,0.03713,0.50873],"force_p95":52.08933,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.90699,"mean_force":41.55827,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13147,0.09153,0.48501]},{"body_a":"door_panel","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.1039,0.14502,0.64433],"force_p95":43.32153,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.97368,"mean_force":28.39998,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10571,0.21321,0.53844]},{"body_a":"door_panel","body_b":"link7","contact_count":112.0,"contact_point_centroid":[0.16711,0.1029,0.5884],"force_p95":37.52206,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.78195,"mean_force":22.31402,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10015,0.15844,0.56482]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.23898,-0.00158,0.41741],"force_p95":23.60278,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.29751,"mean_force":17.14569,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1694,0.05269,0.39221]},{"body_a":"door_panel","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.23874,-0.00259,0.48927],"force_p95":19.86489,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.26394,"mean_force":18.96794,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.16912,0.05184,0.46424]},{"body_a":"world","body_b":"door_panel","contact_count":508.0,"contact_point_centroid":[0.30587,0.1538,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10247,0.25647,0.48308]},{"body_a":"door_frame","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.1268,0.17502,0.75023],"force_p95":0.0,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09455,0.12593,0.57119]},{"body_a":"world","body_b":"door_panel","contact_count":172.0,"contact_point_centroid":[0.32876,0.09776,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.12813,0.09466,0.49283]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.34756,0.07014,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.16944,0.05372,0.39275]},{"body_a":"world","body_b":"door_panel","contact_count":300.0,"contact_point_centroid":[0.34814,0.06947,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.16911,0.05186,0.44808]}],"total_contact_groups":11},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16919,0.05187,0.51109],"hinge_angle":0.65978,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":308.25609,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.70711,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":759.0,"raw_peak_contact_force":308.25609,"tcp_end":[0.09456,0.12617,0.57141],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59277,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":252.0,"raw_peak_contact_force":56.90699,"tcp_end":[0.16937,0.05573,0.39488],"tcp_start":[0.09456,0.12617,0.57141],"tcp_to_object_dist_end":0.43327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":33.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":40.0,"raw_peak_contact_force":32.29751,"tcp_end":[0.16938,0.05208,0.3921],"tcp_start":[0.16937,0.05211,0.39212],"tcp_to_object_dist_end":0.43028,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":313.0,"raw_peak_contact_force":20.26394,"tcp_end":[0.16919,0.05187,0.51109],"tcp_start":[0.16938,0.05208,0.3921],"tcp_to_object_dist_end":0.54086,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31438,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.contact_offset_x":0.04658,"approach_1.approach_offset_z":0.29961,"approach_1.speed":0.03471,"push_1.push_distance":0.20197,"push_1.push_speed":0.04575,"retract_1.retract_offset_z":0.17742,"retract_1.speed":0.01394},"optimized_scores":{"best_composite_score":0.59,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":456.0,"contact_point_centroid":[0.1263,0.18069,0.75017],"force_p95":255.95567,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.97261,"mean_force":230.34276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10491,0.14176,0.56856]},{"body_a":"door_panel","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.2085,0.0279,0.51029],"force_p95":53.40752,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.44361,"mean_force":40.90643,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13874,0.08177,0.48709]},{"body_a":"door_panel","body_b":"link7","contact_count":342.0,"contact_point_centroid":[0.17274,0.08829,0.59122],"force_p95":29.66593,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.37409,"mean_force":15.11424,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10496,0.14308,0.56832]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.24362,-0.01315,0.41694],"force_p95":25.63006,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.94233,"mean_force":14.88407,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1735,0.04081,0.39261]},{"body_a":"door_panel","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.24346,-0.01378,0.50356],"force_p95":18.70134,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.77026,"mean_force":18.35071,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17323,0.04026,0.4794]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.10513,0.13653,0.66482],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10719,0.20357,0.55933]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.30957,0.14091,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10456,0.21627,0.51473]},{"body_a":"door_frame","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.1419,0.17502,0.75014],"force_p95":0.0,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10568,0.11748,0.57304]},{"body_a":"world","body_b":"door_panel","contact_count":160.0,"contact_point_centroid":[0.33295,0.09098,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13704,0.08362,0.49153]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.35246,0.0646,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17357,0.04184,0.39277]},{"body_a":"world","body_b":"door_panel","contact_count":388.0,"contact_point_centroid":[0.35278,0.06425,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17323,0.04028,0.47197]}],"total_contact_groups":11},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.17336,0.04031,0.55008],"hinge_angle":0.69495,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":312.97261,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":243.39011,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1623.0,"raw_peak_contact_force":312.97261,"tcp_end":[0.10576,0.11757,0.5731],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59451,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":241.0,"raw_peak_contact_force":57.44361,"tcp_end":[0.17347,0.0439,0.39518],"tcp_start":[0.10576,0.11757,0.5731],"tcp_to_object_dist_end":0.43381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":33.0,"raw_peak_contact_force":31.94233,"tcp_end":[0.17345,0.04048,0.39253],"tcp_start":[0.17349,0.04054,0.39256],"tcp_to_object_dist_end":0.43105,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":411.0,"raw_peak_contact_force":18.77026,"tcp_end":[0.17336,0.04031,0.55008],"tcp_start":[0.17345,0.04048,0.39253],"tcp_to_object_dist_end":0.57815,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29717,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.contact_offset_x":-0.01514,"approach_1.approach_offset_z":0.17593,"approach_1.speed":0.06873,"push_1.push_distance":0.17989,"push_1.push_speed":0.03805,"retract_1.retract_offset_z":0.11585,"retract_1.speed":0.05061},"optimized_scores":{"best_composite_score":0.59,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":21.0,"contact_point_centroid":[0.10075,0.17743,0.5688],"force_p95":58.62582,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.80932,"mean_force":42.45233,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.0981,0.24687,0.46239]},{"body_a":"door_panel","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.1007,0.2174,0.56631],"force_p95":60.11087,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.97444,"mean_force":46.0279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10256,0.29828,0.45544]},{"body_a":"door_panel","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.15685,0.15609,0.43717],"force_p95":45.50074,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.81579,"mean_force":37.38295,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09157,0.21317,0.41249]},{"body_a":"door_panel","body_b":"link7","contact_count":657.0,"contact_point_centroid":[0.15263,0.07701,0.40809],"force_p95":23.57893,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.23969,"mean_force":13.41975,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09307,0.13912,0.38]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14971,0.01088,0.45645],"force_p95":16.15455,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.58973,"mean_force":15.06683,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09773,0.07819,0.42178]},{"body_a":"world","body_b":"door_panel","contact_count":216.0,"contact_point_centroid":[0.29997,0.20558,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10212,0.33528,0.41586]},{"body_a":"world","body_b":"door_panel","contact_count":168.0,"contact_point_centroid":[0.30189,0.17209,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09508,0.23135,0.43953]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.31583,0.12353,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09324,0.13674,0.37962]},{"body_a":"world","body_b":"door_panel","contact_count":220.0,"contact_point_centroid":[0.32879,0.09614,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09774,0.07819,0.41872]}],"total_contact_groups":9},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09767,0.07824,0.46937],"hinge_angle":0.49502,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":70.80932,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":249.0,"raw_peak_contact_force":60.97444,"tcp_end":[0.10229,0.26628,0.48983],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":209.0,"raw_peak_contact_force":70.80932,"tcp_end":[0.08881,0.19807,0.39064],"tcp_start":[0.10229,0.26628,0.48983],"tcp_to_object_dist_end":0.4469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1649.0,"raw_peak_contact_force":24.23969,"tcp_end":[0.09796,0.07843,0.37349],"tcp_start":[0.08881,0.19807,0.39064],"tcp_to_object_dist_end":0.39401,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":229.0,"raw_peak_contact_force":16.58973,"tcp_end":[0.09767,0.07824,0.46937],"tcp_start":[0.09796,0.07843,0.37349],"tcp_to_object_dist_end":0.48577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```