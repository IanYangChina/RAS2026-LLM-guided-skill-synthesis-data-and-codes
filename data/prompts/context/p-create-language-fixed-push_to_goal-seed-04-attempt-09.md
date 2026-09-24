## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6484 | 0.66 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6137 | 0.67 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5565 | 0.66 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3556 | 0.61 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6406 | 0.70 | ✅ accepted |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.648) — your mutation base

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

- **Composite score**: 0.648
- **task_score** (E): 0.659
- **fitness_score**: 0.758  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2791 |
| contact_1 | 1.00 | 1.00 | 0.0387 |
| push_1 | 1.00 | 1.00 | 0.1701 |
| retract_1 | 1.00 | 1.00 | 0.2774 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.081, 0.036) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.526, 0.081, 0.036)→(0.524, 0.043, 0.026) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 36.118 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.524, 0.043, 0.026)→(0.500, -0.124, 0.020) | (0.531, 0.007, 0.025)→(0.546, -0.116, 0.026) | 0.161→0.059 | 1.00 / 4.000 | 10.831 | 67.182 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.124, 0.020)→(0.498, -0.124, 0.298) | (0.546, -0.116, 0.026)→(0.544, -0.116, 0.025) | 0.059→0.058 | 1.00 / 4.000 | 0.245 | 16.358 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 1.000
- goal_progress: 0.845
- terminal_score: 0.845
- phase_score: 0.819
- phase_breakdown.contact_score: 0.760
- phase_breakdown.push_score: 0.885
- phase_breakdown.approach_score: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.830
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.845
- **Median Q (composite search score)**: 0.622
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46939,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29199,"approach_1.approach_tolerance":0.00812,"contact_1.contact_force":16.42659,"push_1.push_speed":0.08951,"push_1.push_tolerance":0.02374,"retract_1.retract_speed":0.44956},"optimized_scores":{"best_composite_score":0.62171,"best_fitness_score":0.73171,"best_task_score":0.595},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":116.0,"contact_point_centroid":[0.55958,-0.04943,0.05437],"force_p95":45.58326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.76211,"mean_force":26.88848,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52182,-0.04696,0.02152]},{"body_a":"world","body_b":"push_box","contact_count":592.0,"contact_point_centroid":[0.56019,-0.08474,-0.0001],"force_p95":42.39295,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.26557,"mean_force":9.29661,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51822,-0.06143,0.02133]},{"body_a":"attachment","body_b":"push_box","contact_count":204.0,"contact_point_centroid":[0.53915,-0.03903,0.04967],"force_p95":39.48959,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.57062,"mean_force":11.44814,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52587,-0.03079,0.02183]},{"body_a":"world","body_b":"push_box","contact_count":2492.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52141,0.03633,0.17183]},{"body_a":"world","body_b":"push_box","contact_count":1044.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54406,0.05764,0.02887]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.5518,-0.11077,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24522,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49933,-0.12674,0.14769]}],"total_contact_groups":6},"final_pose_error":0.02461,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5518,-0.11077,0.02499],"final_tcp_position":[0.50056,-0.12684,0.29559],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":57.76211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":623.0,"n_steps_budget":660.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2492.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54633,0.0759,0.03601],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":261.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":36.31003,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.545,0.03832,0.02554],"tcp_start":[0.54633,0.0759,0.03601],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.55179,-0.11078,0.02495],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.06497,"object_to_goal_dist_start":0.16043,"object_z_max":0.0292,"peak_contact_force":0.24443,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":912.0,"raw_peak_contact_force":57.76211,"subtask_id":"push","tcp_end":[0.50177,-0.12712,0.02017],"tcp_start":[0.545,0.03832,0.02554],"tcp_to_object_dist_end":0.05284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.5518,-0.11077,0.02499],"object_pos_start":[0.55179,-0.11078,0.02495],"object_to_goal_dist_end":0.06497,"object_to_goal_dist_start":0.06497,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50056,-0.12684,0.29559],"tcp_start":[0.50177,-0.12712,0.02017],"tcp_to_object_dist_end":0.27588,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33333,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.2588,"approach_1.approach_tolerance":0.01317,"contact_1.contact_force":8.37129,"push_1.push_speed":0.10867,"push_1.push_tolerance":0.02697,"retract_1.retract_speed":0.28275},"optimized_scores":{"best_composite_score":0.60377,"best_fitness_score":0.71377,"best_task_score":0.53819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":141.0,"contact_point_centroid":[0.52673,0.00566,0.04245],"force_p95":41.02761,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.84501,"mean_force":7.60449,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51901,0.01685,0.0213]},{"body_a":"world","body_b":"push_box","contact_count":598.0,"contact_point_centroid":[0.55643,-0.069,-9e-05],"force_p95":11.42099,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.98144,"mean_force":2.2957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50844,-0.06025,0.02049]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.55296,-0.01519,0.05286],"force_p95":11.56536,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.57628,"mean_force":2.05579,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51449,-0.01294,0.02031]},{"body_a":"world","body_b":"push_box","contact_count":2676.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05447,0.16654]},{"body_a":"world","body_b":"push_box","contact_count":2644.0,"contact_point_centroid":[0.5613,-0.08689,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49739,-0.12334,0.14944]},{"body_a":"world","body_b":"push_box","contact_count":1012.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5284,0.0923,0.0279]}],"total_contact_groups":6},"final_pose_error":0.02237,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5613,-0.08689,0.02499],"final_tcp_position":[0.49855,-0.12342,0.29768],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":67.84501,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":750.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2676.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53082,0.10982,0.03438],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":253.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":39.53096,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.52905,0.07394,0.02502],"tcp_start":[0.53082,0.10982,0.03438],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.5613,-0.0869,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.08797,"object_to_goal_dist_start":0.1905,"object_z_max":0.02701,"peak_contact_force":0.24526,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":753.0,"raw_peak_contact_force":67.84501,"subtask_id":"push","tcp_end":[0.49989,-0.12371,0.02001],"tcp_start":[0.52905,0.07394,0.02502],"tcp_to_object_dist_end":0.07177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.5613,-0.08689,0.02499],"object_pos_start":[0.5613,-0.0869,0.02499],"object_to_goal_dist_end":0.08798,"object_to_goal_dist_start":0.08797,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.24526,"tcp_end":[0.49855,-0.12342,0.29768],"tcp_start":[0.49989,-0.12371,0.02001],"tcp_to_object_dist_end":0.28219,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31959,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.3472,"approach_1.approach_tolerance":0.00503,"contact_1.contact_force":2.75995,"push_1.push_speed":0.08517,"push_1.push_tolerance":0.02965,"retract_1.retract_speed":0.25403},"optimized_scores":{"best_composite_score":0.71978,"best_fitness_score":0.82978,"best_task_score":0.84522},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":198.0,"contact_point_centroid":[0.52504,-0.09776,-0.00011],"force_p95":45.10791,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.93895,"mean_force":10.56677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49682,-0.0495,0.02327]},{"body_a":"push_box","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.53314,-0.10992,0.05427],"force_p95":58.19753,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.59895,"mean_force":24.13151,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49664,-0.1048,0.02116]},{"body_a":"attachment","body_b":"push_box","contact_count":151.0,"contact_point_centroid":[0.50403,-0.0619,0.03831],"force_p95":41.54325,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.27694,"mean_force":8.54908,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49665,-0.05113,0.02298]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53362,-0.12983,0.05481],"force_p95":27.09093,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.58483,"mean_force":5.02977,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49668,-0.12188,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2641.0,"contact_point_centroid":[0.52182,-0.1525,-1e-05],"force_p95":0.39024,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.66534,"mean_force":0.2815,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49473,-0.12057,0.16314]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.51167,-0.1266,0.05526],"force_p95":1.44525,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.04866,"mean_force":1.18306,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,-0.12129,0.02994]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49957,0.0267,0.17499]},{"body_a":"world","body_b":"push_box","contact_count":1064.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49806,0.03798,0.03151]}],"total_contact_groups":8},"final_pose_error":0.02088,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52026,-0.15157,0.02499],"final_tcp_position":[0.49585,-0.12073,0.30045],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75.93895,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50063,0.05669,0.03847],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":266.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":32.51321,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49839,0.01816,0.02775],"tcp_start":[0.50063,0.05669,0.03847],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.52441,-0.15169,0.02863],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.02473,"object_to_goal_dist_start":0.13127,"object_z_max":0.02947,"peak_contact_force":32.00479,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":380.0,"raw_peak_contact_force":75.93895,"subtask_id":"push","tcp_end":[0.49727,-0.12104,0.02128],"tcp_start":[0.49839,0.01816,0.02775],"tcp_to_object_dist_end":0.0416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":718.0,"n_steps_budget":750.0,"object_pos_end":[0.52026,-0.15157,0.02499],"object_pos_start":[0.52441,-0.15169,0.02863],"object_to_goal_dist_end":0.02032,"object_to_goal_dist_start":0.02473,"object_z_max":0.02909,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2701.0,"raw_peak_contact_force":48.58483,"tcp_end":[0.49585,-0.12073,0.30045],"tcp_start":[0.49727,-0.12104,0.02128],"tcp_to_object_dist_end":0.27826,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```