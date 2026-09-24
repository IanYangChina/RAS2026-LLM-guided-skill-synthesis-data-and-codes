## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.7500 | 1.00 | ❌ rejected |
| 10 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.7500 | 1.00 | ❌ rejected |
| 9 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | time_limit | time_limit | 6 | 0.7000 | 1.00 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.7500 | 1.00 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.7500 | 1.00 | ❌ rejected |

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

## Parent Skill (Best Known, Q=0.750)

```yaml
skill: door_push
dsl_version: 2
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
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
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
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Last Evaluated Skill (Q=0.750)

```yaml
skill: door_push
dsl_version: 2
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
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
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
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.750
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 0.67 | 0.2107 |
| push_door | 0.00 | 0.67 | 0.1705 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.189, 0.367) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 13.105 | 33.664 |
| push_door | push | 0.00 / step_budget | (0.100, 0.189, 0.367)→(0.098, 0.026, 0.416) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 8.155 | 43.676 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.750
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 5.0
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31469,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.arc_height":0.13722,"approach_handle.speed":0.04775,"push_door.pose_tol":0.03226,"push_door.push_distance":0.17811,"push_door.push_speed":0.06861},"optimized_scores":{"best_composite_score":0.75,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":692.0,"contact_point_centroid":[0.16328,0.03778,0.42798],"force_p95":27.19816,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.94367,"mean_force":13.84595,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09765,0.09465,0.40003]},{"body_a":"door_panel","body_b":"link6","contact_count":66.0,"contact_point_centroid":[0.10166,0.16562,0.52488],"force_p95":30.40559,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.42881,"mean_force":20.27396,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09979,0.23514,0.4192]},{"body_a":"door_panel","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.16495,0.14317,0.41279],"force_p95":26.46863,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.28764,"mean_force":21.7268,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0997,0.20065,0.38891]},{"body_a":"world","body_b":"door_panel","contact_count":532.0,"contact_point_centroid":[0.30126,0.17666,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09998,0.30413,0.40845]},{"body_a":"world","body_b":"door_panel","contact_count":896.0,"contact_point_centroid":[0.32426,0.10596,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09779,0.0959,0.39921]}],"total_contact_groups":5},"final_pose_error":0.07125,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09803,0.02567,0.41713],"hinge_angle":0.59372,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":34.94367,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.6545,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":646.0,"raw_peak_contact_force":32.42881,"tcp_end":[0.09976,0.18805,0.36823],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.31598,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1588.0,"raw_peak_contact_force":34.94367,"tcp_end":[0.09803,0.02567,0.41713],"tcp_start":[0.09976,0.18805,0.36823],"tcp_to_object_dist_end":0.42926,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81739,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.arc_height":0.17359,"approach_handle.speed":0.04942,"push_door.pose_tol":0.03034,"push_door.push_distance":0.1324,"push_door.push_speed":0.1239},"optimized_scores":{"best_composite_score":0.75,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":384.0,"contact_point_centroid":[0.16359,0.0614,0.41718],"force_p95":24.9678,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.43824,"mean_force":15.36014,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09836,0.11886,0.39024]},{"body_a":"door_panel","body_b":"link6","contact_count":99.0,"contact_point_centroid":[0.10112,0.17506,0.51302],"force_p95":30.42049,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.47688,"mean_force":20.63754,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0998,0.2467,0.40664]},{"body_a":"door_panel","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.16494,0.14528,0.40312],"force_p95":26.95516,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.23667,"mean_force":21.70634,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09971,0.20273,0.37921]},{"body_a":"world","body_b":"door_panel","contact_count":692.0,"contact_point_centroid":[0.30091,0.18174,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09995,0.29944,0.39501]},{"body_a":"world","body_b":"door_panel","contact_count":404.0,"contact_point_centroid":[0.31985,0.11453,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09822,0.11639,0.39163]}],"total_contact_groups":5},"final_pose_error":0.07049,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09441,0.05702,0.41963],"hinge_angle":0.53258,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":46.43824,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.6591,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":830.0,"raw_peak_contact_force":31.47688,"tcp_end":[0.09971,0.19137,0.36594],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.14862,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":788.0,"raw_peak_contact_force":46.43824,"tcp_end":[0.09441,0.05702,0.41963],"tcp_start":[0.09971,0.19137,0.36594],"tcp_to_object_dist_end":0.43388,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.625,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.arc_height":0.13927,"approach_handle.speed":0.06805,"push_door.pose_tol":0.03085,"push_door.push_distance":0.18195,"push_door.push_speed":0.13611},"optimized_scores":{"best_composite_score":0.75,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":500.0,"contact_point_centroid":[0.16549,0.03586,0.42447],"force_p95":33.30697,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.64587,"mean_force":15.1762,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09858,0.09083,0.39771]},{"body_a":"door_panel","body_b":"link6","contact_count":166.0,"contact_point_centroid":[0.10083,0.1943,0.53402],"force_p95":36.16761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.08557,"mean_force":18.37538,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0998,0.26919,0.42653]},{"body_a":"door_panel","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.16495,0.14383,0.41257],"force_p95":28.13676,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.05781,"mean_force":21.21236,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09971,0.20131,0.38867]},{"body_a":"world","body_b":"door_panel","contact_count":692.0,"contact_point_centroid":[0.3007,0.19306,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09995,0.30743,0.40713]},{"body_a":"world","body_b":"door_panel","contact_count":628.0,"contact_point_centroid":[0.32526,0.10499,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09856,0.09191,0.3977]}],"total_contact_groups":5},"final_pose_error":0.06134,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10231,-0.00403,0.41126],"hinge_angle":0.6487,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.64587,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":906.0,"raw_peak_contact_force":37.08557,"tcp_end":[0.09973,0.18836,0.36801],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":697.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1128.0,"raw_peak_contact_force":49.64587,"tcp_end":[0.10231,-0.00403,0.41126],"tcp_start":[0.09973,0.18836,0.36801],"tcp_to_object_dist_end":0.42381,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```