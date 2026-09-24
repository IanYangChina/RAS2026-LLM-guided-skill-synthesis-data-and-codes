## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.9922 | 1.00 | ❌ rejected |
| 11 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8811 | 1.00 | ❌ rejected |
| 10 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 1.1033 | 1.00 | ✅ accepted |
| 9 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | time_limit | pose_tolerance | 6 | 0.8367 | 1.00 | ✅ accepted |
| 8 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.5400 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`
- Frozen initial hinge angle: 0.004 rad
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
  frozen_initial_hinge_angle_rad: 0.0041
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91

## Current Skill (Q=0.992) — your mutation base

```yaml
skill: door_push
dsl_version: 2
phases:
- id: approach_contact
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - -0.01
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
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
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
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
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.1
    - -0.1
    - 0.15
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_contact** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, -0.01, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.1, -0.1, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.992
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_contact | 0.67 | 1.00 | 0.1221 |
| push_1 | 1.00 | 0.33 | 0.1725 |
| retract_1 | 1.00 | 0.67 | 0.3907 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_contact | contact | 0.67 / force_exceeded | (0.100, 0.399, 0.350)→(0.100, 0.277, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 18.255 | 12.648 |
| push_1 | push | 1.00 / step_budget | (0.100, 0.277, 0.348)→(0.097, 0.450, 0.346) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 2.000 | 0.238 | 142.640 |
| retract_1 | retract | 1.00 / step_budget | (0.097, 0.450, 0.346)→(0.191, 0.118, 0.529) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 14.521 | 354.649 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.103
- **K-run variance**: 0.0247
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 5.7
- **Final σ (mean)**: 0.234


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `083132501f1ba139cf05fa7994a1ee954b157d46058e9396ba8b78c93b367725`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a0caaf91521131af8da2ca1e0ce4fb631dc10b8d496fc3757eb1acd97f543da3`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.00413,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95028,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.contact_force_threshold":16.46938,"push_1.push_distance":0.19889,"retract_1.retract_arc_height":0.24124,"retract_1.retract_speed":0.07543},"optimized_scores":{"best_composite_score":1.10333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":464.0,"contact_point_centroid":[0.10897,0.22493,0.75011],"force_p95":345.16082,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.31784,"mean_force":293.75354,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.14254,0.24973,0.57327]},{"body_a":"door_panel","body_b":"link7","contact_count":87.0,"contact_point_centroid":[0.23655,0.11618,0.58789],"force_p95":60.72737,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.78186,"mean_force":43.15436,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.16923,0.16867,0.55973]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.10008,0.1974,0.45604],"force_p95":45.82859,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.08894,"mean_force":21.85815,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09964,0.27472,0.34784]},{"body_a":"door_panel","body_b":"link6","contact_count":236.0,"contact_point_centroid":[0.10128,0.17391,0.69955],"force_p95":28.76525,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.76945,"mean_force":12.26866,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.14142,0.24299,0.57103]},{"body_a":"door_panel","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.10009,0.1981,0.45609],"force_p95":12.52483,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.5815,"mean_force":8.23374,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09966,0.2755,0.34787]},{"body_a":"world","body_b":"door_panel","contact_count":824.0,"contact_point_centroid":[0.30004,0.18919,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09958,0.33823,0.34775]},{"body_a":"world","body_b":"door_panel","contact_count":408.0,"contact_point_centroid":[0.30009,0.18835,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09927,0.35171,0.3459]},{"body_a":"world","body_b":"door_panel","contact_count":1012.0,"contact_point_centroid":[0.30209,0.17689,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13495,0.29749,0.54348]}],"total_contact_groups":8},"final_pose_error":0.04932,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19092,0.11416,0.5344],"hinge_angle":0.52954,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":562.31784,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.5815,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":834.0,"raw_peak_contact_force":16.5815,"tcp_end":[0.09964,0.27475,0.34788],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45436,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":411.0,"raw_peak_contact_force":49.08894,"tcp_end":[0.09886,0.45402,0.34492],"tcp_start":[0.09964,0.27475,0.34788],"tcp_to_object_dist_end":0.57868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1799.0,"raw_peak_contact_force":562.31784,"tcp_end":[0.19092,0.11416,0.5344],"tcp_start":[0.09886,0.45402,0.34492],"tcp_to_object_dist_end":0.57884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94924,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.contact_force_threshold":24.06223,"push_1.push_distance":0.19987,"retract_1.retract_arc_height":0.31774,"retract_1.retract_speed":0.05694},"optimized_scores":{"best_composite_score":0.77,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.24176,0.10922,0.55991],"force_p95":51.31719,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.23509,"mean_force":40.00686,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17637,0.166,0.53447]},{"body_a":"door_panel","body_b":"link6","contact_count":47.0,"contact_point_centroid":[0.1223,0.14493,0.66401],"force_p95":27.68978,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.9588,"mean_force":19.83323,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15886,0.22491,0.53813]},{"body_a":"door_panel","body_b":"link6","contact_count":414.0,"contact_point_centroid":[0.10055,0.19865,0.45608],"force_p95":16.37022,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.36125,"mean_force":7.83317,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09957,0.27595,0.34795]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10169,0.16348,0.45392],"force_p95":4.83224,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.08657,"mean_force":2.54328,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09967,0.23356,0.34811]},{"body_a":"world","body_b":"door_panel","contact_count":1024.0,"contact_point_centroid":[0.30003,0.19916,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09956,0.3225,0.34781]},{"body_a":"world","body_b":"door_panel","contact_count":516.0,"contact_point_centroid":[0.30175,0.17178,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09939,0.32851,0.34619]},{"body_a":"world","body_b":"door_panel","contact_count":380.0,"contact_point_centroid":[0.30532,0.15951,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13808,0.29262,0.48628]}],"total_contact_groups":7},"final_pose_error":0.04917,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18935,0.12266,0.52201],"hinge_angle":0.49922,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":53.23509,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1438.0,"raw_peak_contact_force":21.36125,"tcp_end":[0.09967,0.23359,0.34812],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43092,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":518.0,"raw_peak_contact_force":5.08657,"tcp_end":[0.09903,0.41395,0.34536],"tcp_start":[0.09967,0.23359,0.34812],"tcp_to_object_dist_end":0.54812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":43.56275,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":495.0,"raw_peak_contact_force":53.23509,"tcp_end":[0.18935,0.12266,0.52201],"tcp_start":[0.09903,0.41395,0.34536],"tcp_to_object_dist_end":0.56867,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.contact_force_threshold":17.6045,"push_1.push_distance":0.17622,"retract_1.retract_arc_height":0.3017,"retract_1.retract_speed":0.03596},"optimized_scores":{"best_composite_score":1.10333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":95.0,"contact_point_centroid":[0.12514,0.22494,0.75013],"force_p95":385.72962,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":448.39475,"mean_force":320.86612,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15222,0.25058,0.5718]},{"body_a":"door_panel","body_b":"link4","contact_count":15.0,"contact_point_centroid":[0.10036,0.22161,0.64448],"force_p95":369.13746,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":373.74404,"mean_force":303.28376,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09549,0.47742,0.3456]},{"body_a":"door_panel","body_b":"link5","contact_count":21.0,"contact_point_centroid":[0.10251,0.24063,0.62247],"force_p95":265.23696,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":275.07482,"mean_force":170.27525,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09634,0.47611,0.34534]},{"body_a":"door_panel","body_b":"link4","contact_count":7.0,"contact_point_centroid":[0.10042,0.2238,0.64436],"force_p95":133.53783,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.27144,"mean_force":35.80795,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.0921,0.4811,0.34708]},{"body_a":"door_panel","body_b":"link5","contact_count":6.0,"contact_point_centroid":[0.10261,0.24361,0.62406],"force_p95":138.12919,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.60091,"mean_force":78.33422,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09216,0.48112,0.34701]},{"body_a":"door_panel","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.24458,0.10973,0.58051],"force_p95":57.73133,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.60173,"mean_force":44.69165,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17757,0.16445,0.55454]},{"body_a":"door_panel","body_b":"link6","contact_count":125.0,"contact_point_centroid":[0.1069,0.18568,0.69573],"force_p95":32.00005,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.12439,"mean_force":19.57504,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.14886,0.26736,0.5726]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.10197,0.23932,0.45905],"force_p95":8.05643,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.95158,"mean_force":2.98386,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09956,0.32334,0.34765]},{"body_a":"world","body_b":"door_panel","contact_count":416.0,"contact_point_centroid":[0.30001,0.21014,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09956,0.36046,0.34772]},{"body_a":"world","body_b":"door_panel","contact_count":392.0,"contact_point_centroid":[0.29998,0.20959,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09897,0.39642,0.34535]},{"body_a":"world","body_b":"door_panel","contact_count":604.0,"contact_point_centroid":[0.30317,0.18877,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13194,0.33888,0.51838]}],"total_contact_groups":11},"final_pose_error":0.04972,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1915,0.1172,0.53187],"hinge_angle":0.52004,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":448.39475,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":38.18469,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":416.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09957,0.32332,0.34764],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48508,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.71428,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":431.0,"raw_peak_contact_force":373.74404,"tcp_end":[0.09252,0.48096,0.34682],"tcp_start":[0.09957,0.32332,0.34764],"tcp_to_object_dist_end":0.60014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":907.0,"raw_peak_contact_force":448.39475,"tcp_end":[0.1915,0.1172,0.53187],"tcp_start":[0.09252,0.48096,0.34682],"tcp_to_object_dist_end":0.57732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```