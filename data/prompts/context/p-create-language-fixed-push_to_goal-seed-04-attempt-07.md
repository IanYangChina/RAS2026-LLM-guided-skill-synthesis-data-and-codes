## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5565 | 0.66 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3556 | 0.61 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6406 | 0.70 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4187 | 0.66 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6216 | 0.64 | ❌ rejected |

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

## Current Skill (Q=0.557) — your mutation base

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

- **Composite score**: 0.557
- **task_score** (E): 0.658
- **fitness_score**: 0.717  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2740 |
| contact_1 | 1.00 | 1.00 | 0.0382 |
| push_1 | 1.00 | 1.00 | 0.1624 |
| retract_1 | 0.67 | 1.00 | 0.2317 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.080, 0.041) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.526, 0.080, 0.041)→(0.524, 0.043, 0.029) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 37.674 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.524, 0.043, 0.029)→(0.504, -0.117, 0.023) | (0.531, 0.007, 0.025)→(0.551, -0.125, 0.026) | 0.161→0.057 | 1.00 / 2.667 | 14.055 | 115.303 |
| retract_1 | retract | 0.67 / step_budget | (0.504, -0.117, 0.023)→(0.502, -0.117, 0.255) | (0.551, -0.125, 0.026)→(0.550, -0.126, 0.025) | 0.057→0.056 | 1.00 / 4.000 | 0.245 | 2.174 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.963
- lateral_force_integral: None
- approach_alignment: 0.995
- goal_progress: 0.708
- terminal_score: 0.708
- phase_score: 0.782
- phase_breakdown.contact_score: 0.745
- phase_breakdown.push_score: 0.852
- phase_breakdown.approach_score: 0.663

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.752
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.708
- **Median Q (composite search score)**: 0.547
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.80682,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31086,"approach_1.approach_tolerance":0.02271,"contact_1.contact_force":3.46957,"push_1.push_distance":0.16425,"push_1.push_speed":0.19342,"push_1.push_tolerance":0.04513,"retract_1.retract_speed":0.18424},"optimized_scores":{"best_composite_score":0.54657,"best_fitness_score":0.70657,"best_task_score":0.66545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":106.0,"contact_point_centroid":[0.55633,-0.07877,0.06054],"force_p95":170.04461,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.16445,"mean_force":129.07112,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51908,-0.08043,0.02671]},{"body_a":"world","body_b":"push_box","contact_count":259.0,"contact_point_centroid":[0.56405,-0.09494,-0.00024],"force_p95":127.65187,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":145.69946,"mean_force":62.58007,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52334,-0.06002,0.0272]},{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.53334,-0.05938,0.03412],"force_p95":57.38058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.48877,"mean_force":22.69377,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52573,-0.05019,0.02791]},{"body_a":"world","body_b":"push_box","contact_count":3755.0,"contact_point_centroid":[0.55004,-0.12982,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.69045,"mean_force":0.25489,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50923,-0.12098,0.16922]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.52648,-0.12753,0.05422],"force_p95":2.96275,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.48159,"mean_force":2.1054,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50969,-0.12374,0.02943]},{"body_a":"world","body_b":"push_box","contact_count":1644.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52191,0.036,0.17329]},{"body_a":"world","body_b":"push_box","contact_count":1012.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54334,0.05641,0.03546]}],"total_contact_groups":7},"final_pose_error":0.01692,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5498,-0.13,0.02499],"final_tcp_position":[0.51039,-0.12107,0.31091],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":189.16445,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54553,0.07356,0.04443],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":253.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":38.9498,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54449,0.03824,0.03056],"tcp_start":[0.54553,0.07356,0.04443],"tcp_to_object_dist_end":0.03829,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":690.0,"object_pos_end":[0.55286,-0.12573,0.03018],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.0584,"object_to_goal_dist_start":0.16043,"object_z_max":0.03162,"peak_contact_force":0.38903,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":475.0,"raw_peak_contact_force":189.16445,"subtask_id":"push","tcp_end":[0.512,-0.1214,0.02775],"tcp_start":[0.54449,0.03824,0.03056],"tcp_to_object_dist_end":0.04116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.5498,-0.13,0.02499],"object_pos_start":[0.55286,-0.12573,0.03018],"object_to_goal_dist_end":0.05367,"object_to_goal_dist_start":0.0584,"object_z_max":0.03018,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3767.0,"raw_peak_contact_force":3.69045,"tcp_end":[0.51039,-0.12107,0.31091],"tcp_start":[0.512,-0.1214,0.02775],"tcp_to_object_dist_end":0.28876,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11207,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.24229,"approach_1.approach_tolerance":0.01357,"contact_1.contact_force":8.69047,"push_1.push_distance":0.17742,"push_1.push_speed":0.111,"push_1.push_tolerance":0.03632,"retract_1.retract_speed":0.09188},"optimized_scores":{"best_composite_score":0.53054,"best_fitness_score":0.69054,"best_task_score":0.59988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":130.0,"contact_point_centroid":[0.52757,-0.00114,0.04493],"force_p95":51.17109,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.32219,"mean_force":8.28676,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51922,0.00989,0.02171]},{"body_a":"world","body_b":"push_box","contact_count":259.0,"contact_point_centroid":[0.54833,-0.06644,-0.00029],"force_p95":36.82764,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.01308,"mean_force":6.98207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51393,-0.03287,0.0212]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.55133,-0.03625,0.05314],"force_p95":62.37128,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.79699,"mean_force":15.7991,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51325,-0.03472,0.02041]},{"body_a":"world","body_b":"push_box","contact_count":3978.0,"contact_point_centroid":[0.56353,-0.10781,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7862,"mean_force":0.24714,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50054,-0.11112,0.09412]},{"body_a":"world","body_b":"push_box","contact_count":2644.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5145,0.05439,0.16673]},{"body_a":"world","body_b":"push_box","contact_count":1012.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52817,0.09217,0.02803]}],"total_contact_groups":6},"final_pose_error":0.1509,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.56342,-0.10772,0.02499],"final_tcp_position":[0.50092,-0.11105,0.16935],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":70.32219,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":661.0,"n_steps_budget":780.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53054,0.10966,0.03455],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":253.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":39.77919,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1012.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.52889,0.07385,0.02512],"tcp_start":[0.53054,0.10966,0.03455],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.56409,-0.1087,0.02437],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.07625,"object_to_goal_dist_start":0.1905,"object_z_max":0.02769,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":425.0,"raw_peak_contact_force":70.32219,"subtask_id":"push","tcp_end":[0.50401,-0.11163,0.02022],"tcp_start":[0.52889,0.07385,0.02512],"tcp_to_object_dist_end":0.0603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56342,-0.10772,0.02499],"object_pos_start":[0.56409,-0.1087,0.02437],"object_to_goal_dist_end":0.07622,"object_to_goal_dist_start":0.07625,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3978.0,"raw_peak_contact_force":0.7862,"tcp_end":[0.50092,-0.11105,0.16935],"tcp_start":[0.50401,-0.11163,0.02022],"tcp_to_object_dist_end":0.15734,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.74038,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15712,"approach_1.approach_tolerance":0.02084,"contact_1.contact_force":17.70529,"push_1.push_distance":0.11678,"push_1.push_speed":0.17394,"push_1.push_tolerance":0.02783,"retract_1.retract_speed":0.16551},"optimized_scores":{"best_composite_score":0.59242,"best_fitness_score":0.75242,"best_task_score":0.708},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":104.0,"contact_point_centroid":[0.50253,-0.04444,0.04107],"force_p95":51.14828,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.42376,"mean_force":9.25161,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49714,-0.03291,0.02608]},{"body_a":"world","body_b":"push_box","contact_count":202.0,"contact_point_centroid":[0.52519,-0.09701,-0.00017],"force_p95":31.0846,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.57692,"mean_force":5.51728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,-0.05483,0.0249]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.53733,-0.14099,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04474,"mean_force":0.24684,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49431,-0.11806,0.15018]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.5102,-0.12894,0.04913],"force_p95":0.93487,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.25882,"mean_force":0.23538,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49674,-0.11937,0.02134]},{"body_a":"world","body_b":"push_box","contact_count":1864.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50002,0.0272,0.1731]},{"body_a":"world","body_b":"push_box","contact_count":1044.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49828,0.03739,0.03609]}],"total_contact_groups":6},"final_pose_error":0.03733,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53723,-0.14089,0.02499],"final_tcp_position":[0.49513,-0.11813,0.28394],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":86.42376,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50106,0.05546,0.04441],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07685,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":261.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":34.29193,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49862,0.01817,0.03118],"tcp_start":[0.50106,0.05546,0.04441],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":231.0,"n_steps_budget":600.0,"object_pos_end":[0.5364,-0.14034,0.02407],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.03767,"object_to_goal_dist_start":0.13127,"object_z_max":0.02724,"peak_contact_force":41.77623,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":306.0,"raw_peak_contact_force":86.42376,"subtask_id":"push","tcp_end":[0.49714,-0.11855,0.02121],"tcp_start":[0.49862,0.01817,0.03118],"tcp_to_object_dist_end":0.04499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53723,-0.14089,0.02499],"object_pos_start":[0.5364,-0.14034,0.02407],"object_to_goal_dist_end":0.03833,"object_to_goal_dist_start":0.03767,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3979.0,"raw_peak_contact_force":2.04474,"tcp_end":[0.49513,-0.11813,0.28394],"tcp_start":[0.49714,-0.11855,0.02121],"tcp_to_object_dist_end":0.26334,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```