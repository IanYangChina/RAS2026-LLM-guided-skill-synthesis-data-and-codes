## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5959 | 0.71 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 3 | 0.1763 | 0.33 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | 0.0920 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

## Current Skill (Q=0.596) — your mutation base

```yaml
skill: door_push
dsl_version: 2
phases:
- id: approach_handle
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_door
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
    tolerance: 0.01
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_door_open
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
      distance: 0.35
      axis: world_y
      mode: add_to_offset
      sign: positive
    tolerance: 0.05
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_door** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_door_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.35, mode=add_to_offset, sign=positive}, tolerance=0.05
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.596
- **task_score** (E): 0.709
- **fitness_score**: 0.709  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2644 |
| descend_to_door | 0.67 | 0.67 | 0.1214 |
| push_door_open | 1.00 | 0.00 | 0.2224 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.174, 0.488) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 4.206 | 46.117 |
| descend_to_door | contact | 0.67 / step_budget | (0.102, 0.174, 0.488)→(0.114, 0.103, 0.390) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 14.827 | 19.309 |
| push_door_open | push | 1.00 / time_limit | (0.114, 0.103, 0.390)→(0.113, 0.326, 0.388) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.560
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.813
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.813
- **Median Q (composite search score)**: 0.533
- **K-run variance**: 0.0175
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53571,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.26196,"descend_to_door.contact_force_threshold":24.99768,"descend_to_door.descend_speed":0.01189,"push_door_open.push_speed":0.10076,"push_door_open.push_stroke":0.23916},"optimized_scores":{"best_composite_score":0.77988,"best_fitness_score":0.55988,"best_task_score":0.55988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":141.0,"contact_point_centroid":[0.13879,0.11941,0.50708],"force_p95":38.32067,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.73398,"mean_force":18.05615,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10412,0.1924,0.46674]},{"body_a":"door_panel","body_b":"link7","contact_count":271.0,"contact_point_centroid":[0.13719,0.05836,0.50345],"force_p95":15.27078,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.22376,"mean_force":12.41565,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.1088,0.13443,0.46119]},{"body_a":"world","body_b":"door_panel","contact_count":644.0,"contact_point_centroid":[0.30365,0.16263,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10243,0.27769,0.41763]},{"body_a":"world","body_b":"door_panel","contact_count":468.0,"contact_point_centroid":[0.31736,0.11807,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10875,0.13465,0.46151]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14707,0.043,0.47631],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.11295,0.11572,0.43521]},{"body_a":"world","body_b":"door_panel","contact_count":964.0,"contact_point_centroid":[0.32049,0.11126,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.1128,0.19802,0.4333]}],"total_contact_groups":6},"final_pose_error":0.07588,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1127,0.27906,0.43296],"hinge_angle":0.39984,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.73398,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":576.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.61714,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":785.0,"raw_peak_contact_force":49.73398,"tcp_end":[0.10477,0.1539,0.48905],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":32.06156,"phase_name":"descend_to_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":739.0,"raw_peak_contact_force":16.22376,"tcp_end":[0.11294,0.11574,0.43525],"tcp_start":[0.10477,0.1539,0.48905],"tcp_to_object_dist_end":0.46432,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":966.0,"raw_peak_contact_force":0.0,"tcp_end":[0.1127,0.27906,0.43296],"tcp_start":[0.11294,0.11574,0.43525],"tcp_to_object_dist_end":0.52729,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52308,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.13816,"descend_to_door.contact_force_threshold":20.57226,"descend_to_door.descend_speed":0.05515,"push_door_open.push_speed":0.12908,"push_door_open.push_stroke":0.47238},"optimized_scores":{"best_composite_score":0.47453,"best_fitness_score":0.75453,"best_task_score":0.75453},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":143.0,"contact_point_centroid":[0.14019,0.15542,0.50283],"force_p95":37.0745,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.89164,"mean_force":18.48072,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10052,0.22598,0.46345]},{"body_a":"door_panel","body_b":"link7","contact_count":540.0,"contact_point_centroid":[0.13926,0.07603,0.47171],"force_p95":17.12648,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.01386,"mean_force":12.67259,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10623,0.1485,0.42981]},{"body_a":"world","body_b":"door_panel","contact_count":588.0,"contact_point_centroid":[0.3012,0.17962,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1003,0.28787,0.42208]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.314,0.12674,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10592,0.1507,0.43286]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.15096,0.04088,0.42001],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.11184,0.10855,0.37497]},{"body_a":"world","body_b":"door_panel","contact_count":832.0,"contact_point_centroid":[0.32132,0.10959,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.11163,0.20747,0.37311]}],"total_contact_groups":6},"final_pose_error":0.26739,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11144,0.31357,0.37267],"hinge_angle":0.40869,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":40.89164,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":731.0,"raw_peak_contact_force":40.89164,"tcp_end":[0.10064,0.18998,0.48769],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.41942,"phase_name":"descend_to_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1456.0,"raw_peak_contact_force":19.01386,"tcp_end":[0.11184,0.10857,0.37502],"tcp_start":[0.10064,0.18998,0.48769],"tcp_to_object_dist_end":0.40612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":834.0,"raw_peak_contact_force":0.0,"tcp_end":[0.11144,0.31357,0.37267],"tcp_start":[0.11184,0.10857,0.37502],"tcp_to_object_dist_end":0.49963,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48485,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.25324,"descend_to_door.contact_force_threshold":24.54267,"descend_to_door.descend_speed":0.08736,"push_door_open.push_speed":0.19078,"push_door_open.push_stroke":0.43006},"optimized_scores":{"best_composite_score":0.53325,"best_fitness_score":0.81325,"best_task_score":0.81325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":134.0,"contact_point_centroid":[0.13948,0.14342,0.50443],"force_p95":32.86065,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.72388,"mean_force":18.94643,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10149,0.21478,0.46489]},{"body_a":"door_panel","body_b":"link7","contact_count":531.0,"contact_point_centroid":[0.14524,0.06005,0.46242],"force_p95":17.40807,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.69088,"mean_force":13.27577,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10926,0.13116,0.42254]},{"body_a":"world","body_b":"door_panel","contact_count":504.0,"contact_point_centroid":[0.30198,0.17335,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10094,0.2855,0.41986]},{"body_a":"world","body_b":"door_panel","contact_count":940.0,"contact_point_centroid":[0.3179,0.11774,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_door","phase_type":"contact","tcp_position_centroid":[0.10914,0.1319,0.42358]},{"body_a":"world","body_b":"door_panel","contact_count":752.0,"contact_point_centroid":[0.32734,0.09858,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.11656,0.22777,0.35846]}],"total_contact_groups":5},"final_pose_error":0.13115,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11622,0.38484,0.35783],"hinge_angle":0.46981,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":47.72388,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":638.0,"raw_peak_contact_force":47.72388,"tcp_end":[0.10166,0.17834,0.4882],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1471.0,"raw_peak_contact_force":22.69088,"tcp_end":[0.11676,0.0859,0.36043],"tcp_start":[0.10166,0.17834,0.4882],"tcp_to_object_dist_end":0.38849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":752.0,"raw_peak_contact_force":0.0,"tcp_end":[0.11622,0.38484,0.35783],"tcp_start":[0.11676,0.0859,0.36043],"tcp_to_object_dist_end":0.53819,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```