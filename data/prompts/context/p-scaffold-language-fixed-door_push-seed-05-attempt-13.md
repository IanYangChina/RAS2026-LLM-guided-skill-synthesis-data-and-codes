## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 12 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ✅ accepted |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 9 | 1.4900 | 1.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 8 | 0.1141 | 0.57 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 6 | 0.9422 | 0.27 | ❌ rejected |

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

## Current Skill (Q=1.620) — your mutation base

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
  generator: arc_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - -0.05
    - 0.05
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
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
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
      distance: 0.2
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
      - 0.35
      default: 0.2
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
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.05, 0.05]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - approach_time: status=consumed; consumers=duration.max_time (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
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
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

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
| approach_1 | 1.00 | 1.00 | 0.3244 |
| contact_1 | 1.00 | 1.00 | 0.0040 |
| push_1 | 1.00 | 0.67 | 0.1516 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.170, 0.134, 0.521) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 226.165 | 1347.714 |
| contact_1 | contact | 1.00 / force_exceeded | (0.170, 0.134, 0.521)→(0.173, 0.132, 0.523) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 1339.586 | 319.082 |
| push_1 | push | 1.00 / time_limit | (0.173, 0.132, 0.523)→(0.251, 0.143, 0.397) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 103.268 | 459.651 |

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
- **Mean generations**: 3.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.5,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_time":11.25166,"approach_1.arc_height":0.15878,"approach_1.speed":0.17147,"contact_1.force_threshold":20.79085,"push_1.push_depth":0.20485,"push_1.push_time":10.15873,"push_1.speed":0.07071},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":249.0,"contact_point_centroid":[0.10596,0.13563,0.62198],"force_p95":622.06419,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1374.5894,"mean_force":524.45598,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10622,0.42025,0.35789]},{"body_a":"link1","body_b":"link5","contact_count":194.0,"contact_point_centroid":[0.09963,-0.0233,0.37805],"force_p95":558.6029,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":686.27534,"mean_force":441.21412,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.13691,0.13275,0.53108]},{"body_a":"door_panel","body_b":"link5","contact_count":79.0,"contact_point_centroid":[0.11581,0.08939,0.58682],"force_p95":314.85372,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":352.83774,"mean_force":60.33127,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10762,0.3655,0.4555]},{"body_a":"door_panel","body_b":"link6","contact_count":338.0,"contact_point_centroid":[0.32839,-0.04317,0.48256],"force_p95":41.27235,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.52212,"mean_force":20.53737,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.20431,0.0899,0.49274]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.24819,-0.05371,0.45338],"force_p95":59.62705,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.62705,"mean_force":59.62705,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.18763,0.07996,0.54275]},{"body_a":"door_panel","body_b":"link6","contact_count":297.0,"contact_point_centroid":[0.18196,0.01286,0.4884],"force_p95":32.10415,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.89718,"mean_force":18.95742,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11875,0.17612,0.52805]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.31676,0.12718,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11037,0.31114,0.45161]},{"body_a":"link1","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.09546,-0.03902,0.37863],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.18652,0.08075,0.54225]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.39439,0.02997,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.20566,0.09045,0.47997]}],"total_contact_groups":9},"final_pose_error":0.07088,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.21667,0.09661,0.4183],"hinge_angle":0.99263,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1374.5894,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":393.15521,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1811.0,"raw_peak_contact_force":1374.5894,"tcp_end":[0.18613,0.08106,0.54215],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.57892,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":59.62705,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":59.62705,"tcp_end":[0.18831,0.07965,0.54328],"tcp_start":[0.18613,0.08106,0.54215],"tcp_to_object_dist_end":0.58048,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1054.0,"raw_peak_contact_force":80.52212,"tcp_end":[0.21667,0.09661,0.4183],"tcp_start":[0.18831,0.07965,0.54328],"tcp_to_object_dist_end":0.48089,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.59459,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_time":10.09633,"approach_1.arc_height":0.10393,"approach_1.speed":0.14547,"contact_1.force_threshold":13.01016,"push_1.push_depth":0.24048,"push_1.push_time":9.97141,"push_1.speed":0.06433},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":552.0,"contact_point_centroid":[0.10505,0.15446,0.56339],"force_p95":622.23683,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1403.60233,"mean_force":485.8128,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.08005,0.3898,0.36199]},{"body_a":"link1","body_b":"link5","contact_count":587.0,"contact_point_centroid":[0.12714,0.00777,0.34449],"force_p95":466.2468,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":620.95353,"mean_force":363.65319,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.22894,0.15857,0.44196]},{"body_a":"link1","body_b":"link5","contact_count":94.0,"contact_point_centroid":[0.06267,0.01156,0.37747],"force_p95":319.19079,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.07101,"mean_force":138.23675,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.15743,0.16631,0.5017]},{"body_a":"link1","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.06158,0.00341,0.38189],"force_p95":380.65601,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.19353,"mean_force":357.8183,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.17898,0.15073,0.50028]},{"body_a":"door_panel","body_b":"link6","contact_count":208.0,"contact_point_centroid":[0.1573,0.01826,0.48947],"force_p95":23.89399,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.44994,"mean_force":16.24168,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.13828,0.20227,0.50187]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.17462,-0.03265,0.4762],"force_p95":44.28956,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.70396,"mean_force":41.24177,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.18092,0.15011,0.5007]},{"body_a":"door_panel","body_b":"link6","contact_count":241.0,"contact_point_centroid":[0.26145,-0.0159,0.42641],"force_p95":32.90327,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.56419,"mean_force":19.36145,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.22676,0.15506,0.45828]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.30984,0.14932,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09694,0.33678,0.40136]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.34315,0.07551,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.18116,0.1499,0.50051]},{"body_a":"world","body_b":"door_panel","contact_count":756.0,"contact_point_centroid":[0.35784,0.05906,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.20926,0.15618,0.46365]}],"total_contact_groups":10},"final_pose_error":0.11101,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.27538,0.15494,0.40896],"hinge_angle":0.79114,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1403.60233,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":111.73365,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1734.0,"raw_peak_contact_force":1403.60233,"tcp_end":[0.1786,0.15093,0.5003],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.55225,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":38.46136,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":383.19353,"tcp_end":[0.185,0.14909,0.50251],"tcp_start":[0.1786,0.15093,0.5003],"tcp_to_object_dist_end":0.55585,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":309.8036,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1584.0,"raw_peak_contact_force":620.95353,"tcp_end":[0.27538,0.15494,0.40896],"tcp_start":[0.185,0.14909,0.50251],"tcp_to_object_dist_end":0.51681,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.40541,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_time":5.07156,"approach_1.arc_height":0.14968,"approach_1.speed":0.13652,"contact_1.force_threshold":16.63833,"push_1.push_depth":0.21808,"push_1.push_time":9.45094,"push_1.speed":0.07276},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":256.0,"contact_point_centroid":[0.10294,0.151,0.61567],"force_p95":490.20815,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1264.94942,"mean_force":230.62232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09043,0.4226,0.35903]},{"body_a":"door_panel","body_b":"link5","contact_count":477.0,"contact_point_centroid":[0.10538,0.14686,0.57669],"force_p95":546.48071,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":977.6895,"mean_force":288.50894,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09338,0.40737,0.38251]},{"body_a":"link1","body_b":"link5","contact_count":78.0,"contact_point_centroid":[0.0596,0.01546,0.38116],"force_p95":594.58035,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":700.17706,"mean_force":239.72242,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12654,0.18058,0.51866]},{"body_a":"link1","body_b":"link5","contact_count":899.0,"contact_point_centroid":[0.09493,0.01157,0.37853],"force_p95":370.63791,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":677.47707,"mean_force":193.9858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.21584,0.16934,0.45836]},{"body_a":"link1","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.0595,0.01108,0.38311],"force_p95":507.70264,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":514.42496,"mean_force":447.20183,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.14451,0.16849,0.52178]},{"body_a":"door_panel","body_b":"link6","contact_count":297.0,"contact_point_centroid":[0.24504,-0.0088,0.46113],"force_p95":39.07755,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.67249,"mean_force":18.8921,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.20589,0.16787,0.47503]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.16189,-0.01373,0.50439],"force_p95":38.54115,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.60865,"mean_force":37.9336,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.14482,0.16828,0.52184]},{"body_a":"door_panel","body_b":"link6","contact_count":198.0,"contact_point_centroid":[0.14106,0.02852,0.50545],"force_p95":23.97798,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.67928,"mean_force":15.20368,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11174,0.21217,0.51584]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.31081,0.14186,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10084,0.34145,0.43359]},{"body_a":"world","body_b":"door_panel","contact_count":764.0,"contact_point_centroid":[0.35479,0.06259,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.21654,0.1694,0.45631]}],"total_contact_groups":10},"final_pose_error":0.08957,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.26121,0.17777,0.3646],"hinge_angle":0.77274,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":3920.66918,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":173.60702,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1933.0,"raw_peak_contact_force":1264.94942,"tcp_end":[0.14424,0.16869,0.52174],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56699,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3920.66918,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":514.42496,"tcp_end":[0.14604,0.16744,0.52194],"tcp_start":[0.14424,0.16869,0.52174],"tcp_to_object_dist_end":0.56726,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1960.0,"raw_peak_contact_force":677.47707,"tcp_end":[0.26121,0.17777,0.3646],"tcp_start":[0.14604,0.16744,0.52194],"tcp_to_object_dist_end":0.48246,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```