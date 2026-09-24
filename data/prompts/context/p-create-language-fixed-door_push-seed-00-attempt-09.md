## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 5 | 1.6972 | 0.98 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 1.2200 | 1.00 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.8200 | 1.00 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.7200 | 1.00 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 1.2200 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.98). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`
- Frozen initial hinge angle: 0.048 rad
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
  frozen_initial_hinge_angle_rad: 0.0478
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73

## Current Skill (Q=1.697) — your mutation base

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
    - -0.1
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    standoff_distance:
      type: scalar
      range:
      - -0.2
      - -0.05
      default: -0.1
      binds_to:
      - path: target.offset.y
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
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
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
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.21
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
      - 0.3
      default: 0.21
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.1, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - standoff_distance: status=consumed; consumers=target.offset.y (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.21, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.697
- **task_score** (E): 0.977
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1645 |
| contact_1 | 1.00 | 1.00 | 0.0280 |
| push_1 | 1.00 | 1.00 | 0.1592 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.100, 0.235, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 7.657 | 21.112 |
| contact_1 | contact | 1.00 / force_exceeded | (0.100, 0.235, 0.348)→(0.101, 0.207, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 2123.407 | 28.489 |
| push_1 | push | 1.00 / time_limit | (0.101, 0.207, 0.348)→(0.101, 0.063, 0.414) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 8.151 | 36.053 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.720
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.380


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `275c70960dc683bb9d0f514db4e615bd3a6644bf8e38d8dd2bfa731bf179f097`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `35996939e2e1630dea7cedb55906290b2cb0393492844f540c2c9d9496e5416e`; realized-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04781,"panel":{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.45872,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.standoff_distance":-0.12803,"contact_1.contact_force":18.93963,"contact_1.contact_speed":0.03758,"push_1.push_distance":0.28924,"push_1.push_speed":0.09018},"optimized_scores":{"best_composite_score":1.72,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":686.0,"contact_point_centroid":[0.16847,0.04809,0.41997],"force_p95":20.85659,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.39106,"mean_force":13.88431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10341,0.10529,0.39208]},{"body_a":"door_panel","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.10266,0.15445,0.45255],"force_p95":11.46221,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.10981,"mean_force":7.90164,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10045,0.22263,0.3469]},{"body_a":"door_panel","body_b":"link6","contact_count":116.0,"contact_point_centroid":[0.10097,0.17296,0.45482],"force_p95":12.71166,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.76176,"mean_force":7.77312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10025,0.24574,0.34805]},{"body_a":"door_panel","body_b":"link7","contact_count":268.0,"contact_point_centroid":[0.1668,0.13573,0.3713],"force_p95":16.84274,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.95084,"mean_force":12.67871,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1015,0.19304,0.34725]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.30076,0.18001,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09994,0.31195,0.34781]},{"body_a":"world","body_b":"door_panel","contact_count":540.0,"contact_point_centroid":[0.30434,0.15839,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10108,0.20505,0.34713]},{"body_a":"world","body_b":"door_panel","contact_count":852.0,"contact_point_centroid":[0.32275,0.10935,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10346,0.10578,0.39175]}],"total_contact_groups":7},"final_pose_error":0.23797,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10473,0.02155,0.42105],"hinge_angle":0.61307,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":39.39106,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.69135,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1076.0,"raw_peak_contact_force":20.76176,"tcp_end":[0.10031,0.23465,0.34811],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43163,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.95084,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":960.0,"raw_peak_contact_force":29.10981,"tcp_end":[0.10217,0.17444,0.34768],"tcp_start":[0.10031,0.23465,0.34811],"tcp_to_object_dist_end":0.40218,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.01244,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1538.0,"raw_peak_contact_force":39.39106,"tcp_end":[0.10473,0.02155,0.42105],"tcp_start":[0.10217,0.17444,0.34768],"tcp_to_object_dist_end":0.43441,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.00413,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.58108,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.standoff_distance":-0.07679,"contact_1.contact_force":15.95509,"contact_1.contact_speed":0.00557,"push_1.push_distance":0.20891,"push_1.push_speed":0.09975},"optimized_scores":{"best_composite_score":1.65153,"best_fitness_score":0.93153,"best_task_score":0.93153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":636.0,"contact_point_centroid":[0.16528,0.09258,0.39637],"force_p95":19.80516,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.1582,"mean_force":14.00395,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09993,0.14986,0.37067]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10164,0.16404,0.45399],"force_p95":28.031,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.50631,"mean_force":14.75316,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09972,0.23429,0.34812]},{"body_a":"door_panel","body_b":"link6","contact_count":210.0,"contact_point_centroid":[0.10058,0.18182,0.4552],"force_p95":16.73776,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.22046,"mean_force":8.09584,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09967,0.25593,0.34804]},{"body_a":"door_panel","body_b":"link6","contact_count":121.0,"contact_point_centroid":[0.10254,0.15557,0.45239],"force_p95":15.75783,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.3415,"mean_force":8.0532,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09961,0.22332,0.34701]},{"body_a":"world","body_b":"door_panel","contact_count":1052.0,"contact_point_centroid":[0.30021,0.18718,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09962,0.32007,0.34782]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.3122,0.13395,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10002,0.15721,0.36795]}],"total_contact_groups":6},"final_pose_error":0.1555,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09768,0.07676,0.41391],"hinge_angle":0.49225,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.1582,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.65599,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1262.0,"raw_peak_contact_force":21.22046,"tcp_end":[0.09972,0.23432,0.34813],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43133,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":29.50631,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":29.50631,"tcp_end":[0.09971,0.23422,0.34808],"tcp_start":[0.09972,0.23432,0.34813],"tcp_to_object_dist_end":0.43123,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1705.0,"raw_peak_contact_force":36.1582,"tcp_end":[0.09768,0.07676,0.41391],"tcp_start":[0.09971,0.23422,0.34808],"tcp_to_object_dist_end":0.43215,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38372,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.standoff_distance":-0.13923,"contact_1.contact_force":15.83901,"contact_1.contact_speed":0.04774,"push_1.push_distance":0.17517,"push_1.push_speed":0.07836},"optimized_scores":{"best_composite_score":1.72,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":682.0,"contact_point_centroid":[0.16649,0.09597,0.39309],"force_p95":20.75974,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.61007,"mean_force":13.65351,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10112,0.15311,0.36751]},{"body_a":"door_panel","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.10251,0.15574,0.45243],"force_p95":12.69206,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.84948,"mean_force":7.85525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09975,0.22365,0.34694]},{"body_a":"door_panel","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.10052,0.19891,0.45607],"force_p95":16.25252,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.35516,"mean_force":7.77256,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09947,0.27618,0.34796]},{"body_a":"world","body_b":"door_panel","contact_count":1012.0,"contact_point_centroid":[0.30004,0.19902,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0995,0.32268,0.34781]},{"body_a":"world","body_b":"door_panel","contact_count":180.0,"contact_point_centroid":[0.30241,0.16762,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09978,0.22284,0.34691]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.10366,0.14617,0.4516],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10018,0.21194,0.3467]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.31247,0.13206,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10118,0.15402,0.3661]}],"total_contact_groups":7},"final_pose_error":0.15004,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10053,0.08944,0.40831],"hinge_angle":0.46509,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":6321.76408,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.62348,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1424.0,"raw_peak_contact_force":21.35516,"tcp_end":[0.09953,0.23547,0.34813],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43192,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6321.76408,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":332.0,"raw_peak_contact_force":26.84948,"tcp_end":[0.10017,0.21203,0.34674],"tcp_start":[0.09953,0.23547,0.34813],"tcp_to_object_dist_end":0.41859,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.43941,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1585.0,"raw_peak_contact_force":32.61007,"tcp_end":[0.10053,0.08944,0.40831],"tcp_start":[0.10017,0.21203,0.34674],"tcp_to_object_dist_end":0.42991,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```