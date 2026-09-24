## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.3049 | 0.85 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.4634 | 0.96 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.6400 | 0.97 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.3222 | 0.98 | ✅ accepted |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 12 | 0.4145 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`
- Frozen initial hinge angle: 0.013 rad
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
  frozen_initial_hinge_angle_rad: 0.0133
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80

## Current Skill (Q=0.305) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: door_push_progress
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_1
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
    - -0.04
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.3
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
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
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_height:
      type: scalar
      range:
      - 0.3
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.003
      - 0.02
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.35
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    guard_force_threshold:
      type: scalar
      range:
      - 10.0
      - 28.0
      default: 22.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 12.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 22.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: door_push_progress
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.05
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.04, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.35, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - guard_force_threshold: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=22.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.305
- **task_score** (E): 0.854
- **fitness_score**: 0.854  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2312 |
| contact_1 | 0.33 | 0.33 | 0.0320 |
| push_1 | 0.33 | 0.33 | 0.0397 |
| retract_1 | 1.00 | 0.00 | 0.0979 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.176, 0.400) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 5.940 | 31.128 |
| contact_1 | contact | 0.33 / step_budget | (0.100, 0.176, 0.400)→(0.100, 0.179, 0.406) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 2.541 | 4.165 |
| push_1 | push | 0.33 / guard_failure | (0.100, 0.124, 0.400)→(0.099, 0.084, 0.402) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 3.152 | 26.961 |
| retract_1 | retract | 1.00 / step_budget | (0.099, 0.084, 0.402)→(0.099, 0.128, 0.489) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.200
- **K-run variance**: 0.0721
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.273


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60c29f30561fee2ce06b067ae52309dfc2791a8d10a0f8247d4f057dc1f7bbf4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `34da519aca1008b6dc2cb922623d951e3d277879157a381e988a54565a8fccc4`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.58601,"average_solve_count":343.0,"average_success_count":343.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.34179,"approach_1.arc_height":0.05179,"approach_1.speed":0.03954,"contact_1.contact_force":4.19861,"contact_1.contact_height":0.40885,"contact_1.speed":0.01098,"push_1.guard_force_threshold":27.98755,"push_1.max_time":5.80245,"push_1.push_depth":0.45441,"push_1.push_speed":0.02492,"retract_1.retract_height":0.08903,"retract_1.speed":0.02174},"optimized_scores":{"best_composite_score":0.20007,"best_fitness_score":0.86007,"best_task_score":0.86007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.16534,0.07437,0.42221],"force_p95":18.60208,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.01195,"mean_force":13.1752,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09964,0.13152,0.39715]},{"body_a":"door_panel","body_b":"link6","contact_count":107.0,"contact_point_centroid":[0.10126,0.17246,0.49576],"force_p95":24.18465,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.25841,"mean_force":16.21876,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09988,0.24383,0.38944]},{"body_a":"door_panel","body_b":"link7","contact_count":81.0,"contact_point_centroid":[0.16504,0.13414,0.39132],"force_p95":25.05547,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.20109,"mean_force":18.93796,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09983,0.19159,0.36738]},{"body_a":"world","body_b":"door_panel","contact_count":548.0,"contact_point_centroid":[0.30139,0.17859,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09997,0.28865,0.38008]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16511,0.11637,0.37998],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09986,0.17387,0.35611]},{"body_a":"world","body_b":"door_panel","contact_count":936.0,"contact_point_centroid":[0.30818,0.1425,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09973,0.17573,0.37895]},{"body_a":"world","body_b":"door_panel","contact_count":668.0,"contact_point_centroid":[0.31612,0.12207,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09965,0.13394,0.39742]},{"body_a":"world","body_b":"door_panel","contact_count":540.0,"contact_point_centroid":[0.3263,0.10036,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09932,0.10107,0.43877]}],"total_contact_groups":8},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09928,0.12844,0.47897],"hinge_angle":0.464,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.01195,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":27.25841,"tcp_end":[0.09986,0.17387,0.35611],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":937.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09977,0.17872,0.40403],"tcp_start":[0.09986,0.17387,0.35611],"tcp_to_object_dist_end":0.45291,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1218.0,"raw_peak_contact_force":28.01195,"subtask_id":"door_push_progress","tcp_end":[0.09951,0.08517,0.39725],"tcp_start":[0.09951,0.08516,0.39723],"tcp_to_object_dist_end":0.41829,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":540.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09928,0.12844,0.47897],"tcp_start":[0.09951,0.08517,0.39725],"tcp_to_object_dist_end":0.50573,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8ddc65539fcda71658f49649be9748aaabe492bbd016f1d18cf00d6d19f91cef`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16216,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.39053,"approach_1.arc_height":0.06801,"approach_1.speed":0.05324,"contact_1.contact_force":4.7182,"contact_1.contact_height":0.41621,"contact_1.speed":0.00908,"push_1.guard_force_threshold":26.00958,"push_1.max_time":14.68207,"push_1.push_depth":0.44964,"push_1.push_speed":0.0274,"retract_1.retract_height":0.1014,"retract_1.speed":0.0664},"optimized_scores":{"best_composite_score":0.04118,"best_fitness_score":0.70118,"best_task_score":0.70118},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.16502,0.13749,0.44064],"force_p95":29.54103,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.27211,"mean_force":20.68941,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09982,0.19498,0.41668]},{"body_a":"door_panel","body_b":"link6","contact_count":76.0,"contact_point_centroid":[0.10155,0.1672,0.53848],"force_p95":27.51634,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.21767,"mean_force":16.08524,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09994,0.237,0.43265]},{"body_a":"door_panel","body_b":"link7","contact_count":401.0,"contact_point_centroid":[0.16482,0.08461,0.42929],"force_p95":17.55785,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.02542,"mean_force":13.36284,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09959,0.14196,0.40501]},{"body_a":"world","body_b":"door_panel","contact_count":636.0,"contact_point_centroid":[0.30169,0.17467,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10002,0.29276,0.41208]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16501,0.11765,0.42736],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09981,0.17519,0.40344]},{"body_a":"world","body_b":"door_panel","contact_count":252.0,"contact_point_centroid":[0.30833,0.14202,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0997,0.17644,0.40716]},{"body_a":"world","body_b":"door_panel","contact_count":436.0,"contact_point_centroid":[0.31455,0.12524,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09959,0.14107,0.40495]},{"body_a":"world","body_b":"door_panel","contact_count":504.0,"contact_point_centroid":[0.32119,0.10985,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09935,0.12293,0.44833]}],"total_contact_groups":8},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09932,0.15098,0.49376],"hinge_angle":0.41109,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":30.27211,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.82055,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":781.0,"raw_peak_contact_force":30.27211,"tcp_end":[0.09981,0.17519,0.40344],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":217.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":253.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09973,0.17812,0.41158],"tcp_start":[0.09981,0.17519,0.40344],"tcp_to_object_dist_end":0.45943,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":837.0,"raw_peak_contact_force":27.02542,"subtask_id":"door_push_progress","tcp_end":[0.09957,0.1074,0.40001],"tcp_start":[0.09956,0.10741,0.40004],"tcp_to_object_dist_end":0.42598,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":504.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09932,0.15098,0.49376],"tcp_start":[0.09957,0.1074,0.40001],"tcp_to_object_dist_end":0.52579,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ff14b28c151409e7d588c8444930f7538b4d5212a336dd723b958144baa5103b`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1036,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.44034,"approach_1.arc_height":0.03692,"approach_1.speed":0.06169,"contact_1.contact_force":4.08517,"contact_1.contact_height":0.33187,"contact_1.speed":0.01358,"push_1.guard_force_threshold":27.97149,"push_1.max_time":12.98098,"push_1.push_depth":0.37976,"push_1.push_speed":0.02004,"retract_1.retract_height":0.09534,"retract_1.speed":0.0452},"optimized_scores":{"best_composite_score":0.67333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":165.0,"contact_point_centroid":[0.10093,0.18505,0.54202],"force_p95":30.43736,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.85497,"mean_force":17.75559,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09991,0.25844,0.4349]},{"body_a":"door_panel","body_b":"link7","contact_count":773.0,"contact_point_centroid":[0.16538,0.06268,0.42208],"force_p95":19.0101,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.84481,"mean_force":12.77237,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09962,0.11984,0.39648]},{"body_a":"door_panel","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.16533,0.14011,0.46634],"force_p95":23.9918,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.88157,"mean_force":17.71871,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1001,0.19755,0.44241]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.16516,0.1217,0.4386],"force_p95":12.49409,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.49542,"mean_force":8.94694,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09994,0.17918,0.41459]},{"body_a":"world","body_b":"door_panel","contact_count":560.0,"contact_point_centroid":[0.30067,0.19061,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10003,0.3049,0.41021]},{"body_a":"world","body_b":"door_panel","contact_count":332.0,"contact_point_centroid":[0.30762,0.1444,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09989,0.17908,0.42144]},{"body_a":"world","body_b":"door_panel","contact_count":1016.0,"contact_point_centroid":[0.31991,0.11417,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09961,0.11655,0.39656]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16486,0.00263,0.43582],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09892,0.05992,0.40744]},{"body_a":"world","body_b":"door_panel","contact_count":500.0,"contact_point_centroid":[0.33197,0.09107,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09873,0.07734,0.45638]}],"total_contact_groups":9},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.0987,0.10334,0.49529],"hinge_angle":0.51842,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":35.85497,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":794.0,"raw_peak_contact_force":35.85497,"tcp_end":[0.10015,0.17982,0.44143],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.62236,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":336.0,"raw_peak_contact_force":12.49542,"tcp_end":[0.09986,0.17896,0.40217],"tcp_start":[0.10015,0.17982,0.44143],"tcp_to_object_dist_end":0.45137,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.45566,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1789.0,"raw_peak_contact_force":25.84481,"subtask_id":"door_push_progress","tcp_end":[0.09892,0.05992,0.40744],"tcp_start":[0.09986,0.17896,0.40217],"tcp_to_object_dist_end":0.42354,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":501.0,"raw_peak_contact_force":0.0,"tcp_end":[0.0987,0.10334,0.49529],"tcp_start":[0.09892,0.05992,0.40744],"tcp_to_object_dist_end":0.51549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```