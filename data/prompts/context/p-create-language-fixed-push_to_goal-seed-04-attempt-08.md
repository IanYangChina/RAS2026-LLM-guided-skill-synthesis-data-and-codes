## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6137 | 0.67 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5565 | 0.66 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3556 | 0.61 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6406 | 0.70 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4187 | 0.66 | ❌ rejected |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.614) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.08
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - -0.01
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - -0.01
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push
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
    - 0.3
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, -0.01, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, -0.01, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.614
- **task_score** (E): 0.665
- **fitness_score**: 0.724  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2719 |
| contact_1 | 1.00 | 1.00 | 0.0371 |
| push_1 | 0.67 | 1.00 | 0.1781 |
| retract_1 | 1.00 | 1.00 | 0.2781 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.078, 0.043) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.526, 0.078, 0.043)→(0.524, 0.043, 0.031) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 35.044 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.524, 0.043, 0.031)→(0.500, -0.132, 0.022) | (0.531, 0.007, 0.025)→(0.546, -0.117, 0.027) | 0.161→0.057 | 1.00 / 3.333 | 6.766 | 45.102 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.132, 0.022)→(0.498, -0.132, 0.300) | (0.546, -0.117, 0.027)→(0.544, -0.117, 0.025) | 0.057→0.055 | 1.00 / 4.000 | 0.245 | 4.538 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.881
- lateral_force_integral: None
- approach_alignment: 1.000
- goal_progress: 0.775
- terminal_score: 0.775
- phase_score: 0.707
- phase_breakdown.contact_score: 0.760
- phase_breakdown.push_score: 0.660
- phase_breakdown.approach_score: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.734
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.775
- **Median Q (composite search score)**: 0.623
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: push_1.push_tolerance
- **Final σ (mean)**: 0.333


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.5,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.28645,"approach_1.approach_tolerance":0.0121,"contact_1.contact_force":4.1151,"push_1.push_distance":0.14433,"push_1.push_tolerance":0.01827,"retract_1.retract_speed":0.31643},"optimized_scores":{"best_composite_score":0.59377,"best_fitness_score":0.70377,"best_task_score":0.55082},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":295.0,"contact_point_centroid":[0.54161,-0.03703,0.05009],"force_p95":31.68329,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.33789,"mean_force":11.70221,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5275,-0.02981,0.02188]},{"body_a":"push_box","body_b":"link7","contact_count":188.0,"contact_point_centroid":[0.56106,-0.04939,0.05474],"force_p95":41.79636,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.65415,"mean_force":27.60143,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52351,-0.04783,0.02177]},{"body_a":"world","body_b":"push_box","contact_count":859.0,"contact_point_centroid":[0.56445,-0.0849,-6e-05],"force_p95":39.93923,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.40034,"mean_force":9.76075,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51954,-0.06451,0.02123]},{"body_a":"world","body_b":"push_box","contact_count":2436.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52191,0.03708,0.16926]},{"body_a":"world","body_b":"push_box","contact_count":1044.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54406,0.05764,0.02887]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.55711,-0.10606,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50269,-0.12687,0.14749]}],"total_contact_groups":6},"final_pose_error":0.02467,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55711,-0.10606,0.02499],"final_tcp_position":[0.50392,-0.12701,0.29539],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":52.33789,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":609.0,"n_steps_budget":660.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54633,0.0759,0.03601],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":261.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":36.31004,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.545,0.03832,0.02554],"tcp_start":[0.54633,0.0759,0.03601],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.55711,-0.10606,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.07206,"object_to_goal_dist_start":0.16043,"object_z_max":0.02949,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1342.0,"raw_peak_contact_force":52.33789,"subtask_id":"push","tcp_end":[0.50514,-0.12729,0.02003],"tcp_start":[0.545,0.03832,0.02554],"tcp_to_object_dist_end":0.05636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.55711,-0.10606,0.02499],"object_pos_start":[0.55711,-0.10606,0.02499],"object_to_goal_dist_end":0.07206,"object_to_goal_dist_start":0.07206,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50392,-0.12701,0.29539],"tcp_start":[0.50514,-0.12729,0.02003],"tcp_to_object_dist_end":0.27638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47222,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.39105,"approach_1.approach_tolerance":0.03444,"contact_1.contact_force":11.15092,"push_1.push_distance":0.20116,"push_1.push_tolerance":0.04577,"retract_1.retract_speed":0.23558},"optimized_scores":{"best_composite_score":0.62342,"best_fitness_score":0.73342,"best_task_score":0.67009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":80.0,"contact_point_centroid":[0.52534,-0.00589,0.04182],"force_p95":23.0491,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.66222,"mean_force":5.61567,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51827,0.00405,0.03112]},{"body_a":"world","body_b":"push_box","contact_count":224.0,"contact_point_centroid":[0.54685,-0.07137,-0.0001],"force_p95":13.65356,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.37828,"mean_force":2.68563,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51188,-0.04507,0.02778]},{"body_a":"world","body_b":"push_box","contact_count":3108.0,"contact_point_centroid":[0.55038,-0.1125,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49239,"mean_force":0.24556,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49885,-0.1248,0.15475]},{"body_a":"world","body_b":"push_box","contact_count":1196.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5148,0.0496,0.1788]},{"body_a":"world","body_b":"push_box","contact_count":876.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5277,0.08825,0.04404]}],"total_contact_groups":5},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55041,-0.11247,0.02499],"final_tcp_position":[0.50002,-0.12475,0.30275],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":46.66222,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53047,0.10183,0.05448],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":36.30963,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":876.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.52859,0.07391,0.03835],"tcp_start":[0.53047,0.10183,0.05448],"tcp_to_object_dist_end":0.04011,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.55037,-0.11252,0.02496],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.06279,"object_to_goal_dist_start":0.1905,"object_z_max":0.02943,"peak_contact_force":0.49311,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":304.0,"raw_peak_contact_force":46.66222,"subtask_id":"push","tcp_end":[0.5015,-0.12508,0.02243],"tcp_start":[0.52859,0.07391,0.03835],"tcp_to_object_dist_end":0.05052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":810.0,"object_pos_end":[0.55041,-0.11247,0.02499],"object_pos_start":[0.55037,-0.11252,0.02496],"object_to_goal_dist_end":0.06285,"object_to_goal_dist_start":0.06279,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3108.0,"raw_peak_contact_force":0.49239,"tcp_end":[0.50002,-0.12475,0.30275],"tcp_start":[0.5015,-0.12508,0.02243],"tcp_to_object_dist_end":0.28256,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32967,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.38657,"approach_1.approach_tolerance":0.00844,"contact_1.contact_force":19.99101,"push_1.push_distance":0.3702,"push_1.push_tolerance":0.005,"retract_1.retract_speed":0.27207},"optimized_scores":{"best_composite_score":0.62392,"best_fitness_score":0.73392,"best_task_score":0.77481},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1535.0,"contact_point_centroid":[0.53563,-0.09455,-8e-05],"force_p95":18.42238,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.30729,"mean_force":6.84465,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49369,-0.0627,0.02316]},{"body_a":"push_box","body_b":"link7","contact_count":354.0,"contact_point_centroid":[0.52988,-0.09214,0.05576],"force_p95":20.49474,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.56309,"mean_force":13.04302,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49305,-0.09894,0.02275]},{"body_a":"attachment","body_b":"push_box","contact_count":814.0,"contact_point_centroid":[0.50721,-0.06771,0.0508],"force_p95":19.18142,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.30821,"mean_force":6.7178,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49368,-0.06037,0.02313]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53029,-0.14271,0.05495],"force_p95":12.34938,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.87525,"mean_force":7.6281,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49209,-0.14425,0.02228]},{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.50779,-0.14178,0.05584],"force_p95":4.05285,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.46925,"mean_force":1.1811,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48998,-0.14388,0.03091]},{"body_a":"world","body_b":"push_box","contact_count":2516.0,"contact_point_centroid":[0.52611,-0.13239,-2e-05],"force_p95":0.39293,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.42301,"mean_force":0.27131,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48976,-0.14349,0.16408]},{"body_a":"world","body_b":"push_box","contact_count":2256.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49959,0.027,0.17367]},{"body_a":"world","body_b":"push_box","contact_count":1064.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49806,0.03798,0.03151]}],"total_contact_groups":8},"final_pose_error":0.02158,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52401,-0.13275,0.02499],"final_tcp_position":[0.49087,-0.14372,0.30074],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":36.30729,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50063,0.05669,0.03847],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":266.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":32.51321,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49839,0.01816,0.02775],"tcp_start":[0.50063,0.05669,0.03847],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53086,-0.13128,0.02963],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.03639,"object_to_goal_dist_start":0.13127,"object_z_max":0.02963,"peak_contact_force":19.55881,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2703.0,"raw_peak_contact_force":36.30729,"subtask_id":"push","tcp_end":[0.49222,-0.14409,0.02227],"tcp_start":[0.49839,0.01816,0.02775],"tcp_to_object_dist_end":0.04137,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":691.0,"n_steps_budget":720.0,"object_pos_end":[0.52401,-0.13275,0.02499],"object_pos_start":[0.53086,-0.13128,0.02963],"object_to_goal_dist_end":0.02956,"object_to_goal_dist_start":0.03639,"object_z_max":0.02963,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2570.0,"raw_peak_contact_force":12.87525,"tcp_end":[0.49087,-0.14372,0.30074],"tcp_start":[0.49222,-0.14409,0.02227],"tcp_to_object_dist_end":0.27795,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```