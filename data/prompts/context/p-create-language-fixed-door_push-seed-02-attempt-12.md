## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ✅ accepted |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.9900 | 1.00 | ❌ rejected |

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

## Parent Skill (Best Known, Q=1.620)

```yaml
skill: door_push
dsl_version: 2
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
    - 0.0
    - 0.15
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
    approach_time:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
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
      default: 5.0
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
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
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

## Last Evaluated Skill (Q=1.620)

```yaml
skill: door_push
dsl_version: 2
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
    - 0.0
    - 0.15
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
    approach_time:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
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
      default: 5.0
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
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_duration:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: hinge_progress
    when: after_phase
    predicate: hinge_delta_reached
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.1
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_time: status=consumed; consumers=duration.max_time (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=hinge_progress, when=after_phase, predicate=hinge_delta_reached, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.1, 0.0]

## Design Metrics

- **Composite score**: 1.620
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.33 | 0.1542 |
| contact_1 | 1.00 | 1.00 | 0.0366 |
| push_1 | 1.00 | 0.33 | 0.1934 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.101, 0.290, 0.457) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 38.012 |
| contact_1 | contact | 1.00 / force_exceeded | (0.101, 0.290, 0.457)→(0.101, 0.256, 0.447) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 12.826 | 12.826 |
| push_1 | push | 1.00 / time_limit | (0.101, 0.140, 0.455)→(0.104, -0.053, 0.451) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 1.297 | 44.241 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.620
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60194,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24062,"approach_1.approach_speed":0.10488,"approach_1.approach_time":2.94955,"contact_1.contact_force":10.90964,"contact_1.speed":0.01454,"push_1.push_duration":3.10422,"push_1.push_speed":0.0588},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":77.0,"contact_point_centroid":[0.10073,0.22355,0.57961],"force_p95":29.51973,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.27027,"mean_force":20.00374,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09939,0.30318,0.47074]},{"body_a":"door_panel","body_b":"link7","contact_count":1018.0,"contact_point_centroid":[0.16604,0.06657,0.50319],"force_p95":17.68758,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.92788,"mean_force":13.00632,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09883,0.12167,0.47801]},{"body_a":"door_panel","body_b":"link6","contact_count":609.0,"contact_point_centroid":[0.10081,0.18271,0.58607],"force_p95":10.98282,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.00709,"mean_force":7.31651,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09885,0.25408,0.47899]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10027,0.21442,0.58987],"force_p95":19.19679,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.19679,"mean_force":19.19679,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09922,0.29246,0.4813]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.29984,0.20562,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09957,0.34815,0.4122]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.29977,0.19731,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09926,0.29314,0.48247]},{"body_a":"world","body_b":"door_panel","contact_count":1764.0,"contact_point_centroid":[0.31391,0.13967,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09883,0.16415,0.47837]}],"total_contact_groups":7},"final_pose_error":0.00366,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09876,-0.00866,0.47769],"hinge_angle":0.64509,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.27027,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1173.0,"raw_peak_contact_force":49.27027,"tcp_end":[0.09934,0.29366,0.48316],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.57406,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.19679,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":33.0,"raw_peak_contact_force":19.19679,"tcp_end":[0.09921,0.29239,0.48117],"tcp_start":[0.09934,0.29366,0.48316],"tcp_to_object_dist_end":0.57172,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1941.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.89194,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3391.0,"raw_peak_contact_force":41.92788,"tcp_end":[0.09876,-0.00866,0.47769],"tcp_start":[0.09898,0.18447,0.47916],"tcp_to_object_dist_end":0.48787,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87234,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16762,"approach_1.approach_speed":0.12007,"approach_1.approach_time":2.58174,"contact_1.contact_force":8.29154,"contact_1.speed":0.02938,"push_1.push_duration":1.81445,"push_1.push_speed":0.06619},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":204.0,"contact_point_centroid":[0.10054,0.21451,0.56491],"force_p95":28.7297,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.76581,"mean_force":19.48324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10035,0.29384,0.45599]},{"body_a":"door_panel","body_b":"link7","contact_count":1197.0,"contact_point_centroid":[0.16879,0.05862,0.50899],"force_p95":17.80358,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.98486,"mean_force":12.70527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10026,0.1113,0.4844]},{"body_a":"door_panel","body_b":"link6","contact_count":369.0,"contact_point_centroid":[0.10142,0.16872,0.59172],"force_p95":11.05697,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.54143,"mean_force":7.57396,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1003,0.23876,0.48523]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10016,0.18897,0.59487],"force_p95":8.79871,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.79871,"mean_force":8.79871,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10064,0.26418,0.48716]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.29996,0.20381,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10016,0.32885,0.41956]},{"body_a":"world","body_b":"door_panel","contact_count":1820.0,"contact_point_centroid":[0.31788,0.12789,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10027,0.13706,0.4846]}],"total_contact_groups":6},"final_pose_error":0.00801,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10016,-0.04312,0.48391],"hinge_angle":0.68564,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":64.76581,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":64.76581,"tcp_end":[0.10064,0.26418,0.48716],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56325,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.79871,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":8.79871,"tcp_end":[0.10063,0.26416,0.48723],"tcp_start":[0.10064,0.26418,0.48716],"tcp_to_object_dist_end":0.56329,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1941.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3386.0,"raw_peak_contact_force":40.98486,"tcp_end":[0.10016,-0.04312,0.48391],"tcp_start":[0.10038,0.1499,0.4853],"tcp_to_object_dist_end":0.49605,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65031,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1813,"approach_1.approach_speed":0.06025,"approach_1.approach_time":2.18433,"contact_1.contact_force":10.42926,"contact_1.speed":0.01965,"push_1.push_duration":2.45496,"push_1.push_speed":0.07205},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":1258.0,"contact_point_centroid":[0.17388,0.04113,0.41576],"force_p95":19.4079,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.81047,"mean_force":12.99555,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10487,0.09258,0.39077]},{"body_a":"door_panel","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.10432,0.14163,0.47812],"force_p95":16.60951,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.27196,"mean_force":10.13251,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10445,0.20919,0.37208]},{"body_a":"door_panel","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.10412,0.14309,0.47872],"force_p95":10.33817,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.48143,"mean_force":9.19109,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10451,0.21114,0.3726]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.30379,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10077,0.35584,0.3748]},{"body_a":"world","body_b":"door_panel","contact_count":776.0,"contact_point_centroid":[0.30353,0.16127,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10313,0.25948,0.38561]},{"body_a":"world","body_b":"door_panel","contact_count":1572.0,"contact_point_centroid":[0.32883,0.10328,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10578,0.07757,0.39026]}],"total_contact_groups":6},"final_pose_error":0.02754,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11183,-0.10728,0.39211],"hinge_angle":0.73687,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.81047,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10199,0.31361,0.40209],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52003,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.48143,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":784.0,"raw_peak_contact_force":10.48143,"tcp_end":[0.10452,0.21059,0.37247],"tcp_start":[0.10199,0.31361,0.40209],"tcp_to_object_dist_end":0.44046,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2841.0,"raw_peak_contact_force":49.81047,"tcp_end":[0.11183,-0.10728,0.39211],"tcp_start":[0.1039,0.08653,0.40032],"tcp_to_object_dist_end":0.42162,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```