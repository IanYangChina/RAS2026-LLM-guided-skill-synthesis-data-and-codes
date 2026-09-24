## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.6075 | 0.85 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.6070 | 0.94 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.4390 | 0.90 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.6066 | 0.74 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6934 | 0.75 | ❌ rejected |

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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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

## Current Skill (Q=0.607) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
- id: push
  offset:
  - 0.0
  - 0.03
  - 0.0
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
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
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
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.2
      default: 0.1
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
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.3
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.607
- **task_score** (E): 0.849
- **fitness_score**: 0.817  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2798 |
| contact_1 | 1.00 | 1.00 | 0.0414 |
| push_1 | 1.00 | 0.67 | 0.1711 |
| retract_1 | 0.00 | 1.00 | 0.1645 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.077, 0.036) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, 0.077, 0.036)→(0.510, 0.039, 0.022) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 18.299 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.510, 0.039, 0.022)→(0.498, -0.125, 0.020) | (0.513, 0.002, 0.025)→(0.511, -0.161, 0.026) | 0.160→0.017 | 0.67 / 1.333 | 2.434 | 58.809 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.125, 0.020)→(0.495, -0.056, 0.169) | (0.511, -0.161, 0.026)→(0.510, -0.171, 0.025) | 0.017→0.024 | 1.00 / 4.000 | 0.245 | 3.110 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.686
- goal_progress: 0.875
- terminal_score: 0.875
- phase_score: 0.821
- phase_breakdown.push_score: 0.858
- phase_breakdown.approach_score: 0.798
- phase_breakdown.contact_score: 0.775

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.843
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.875
- **Median Q (composite search score)**: 0.601
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: approach_1.speed
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8156,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01,"contact_1.contact_force":6.80465,"contact_1.contact_offset":0.02738,"contact_1.speed":0.0111,"push_1.push_depth":0.00661,"push_1.push_speed":0.09754,"push_1.push_tolerance":0.03326,"retract_1.retract_speed":0.0532},"optimized_scores":{"best_composite_score":0.58845,"best_fitness_score":0.79845,"best_task_score":0.84557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.46393,-0.06522,0.03303],"force_p95":15.32074,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.79775,"mean_force":3.96304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4602,-0.05351,0.02091]},{"body_a":"world","body_b":"push_box","contact_count":186.0,"contact_point_centroid":[0.47429,-0.09511,-9e-05],"force_p95":11.55952,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.80162,"mean_force":3.5791,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45766,-0.04687,0.0211]},{"body_a":"world","body_b":"push_box","contact_count":3892.0,"contact_point_centroid":[0.50176,-0.17012,-2e-05],"force_p95":0.24537,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.41509,"mean_force":0.25442,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48721,-0.10233,0.06798]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49155,-0.13895,0.03003],"force_p95":2.05002,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.17895,"mean_force":1.02288,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48867,-0.12706,0.02001]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.49554,-0.06168,0.05372],"force_p95":0.33999,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42953,"mean_force":0.09957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45957,-0.05272,0.02046]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47375,0.02272,0.16627]},{"body_a":"world","body_b":"push_box","contact_count":3844.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44155,0.02286,0.02672]}],"total_contact_groups":7},"final_pose_error":0.20249,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50173,-0.16976,0.02499],"final_tcp_position":[0.48932,-0.08118,0.11481],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":52.79775,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.44916,0.04573,0.03431],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":23.57302,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3844.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4382,0.00539,0.02348],"tcp_start":[0.44916,0.04573,0.03431],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50048,-0.16284,0.02505],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01285,"object_to_goal_dist_start":0.12843,"object_z_max":0.02755,"peak_contact_force":7.28451,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":333.0,"raw_peak_contact_force":52.79775,"subtask_id":"push","tcp_end":[0.48866,-0.12666,0.01997],"tcp_start":[0.4382,0.00539,0.02348],"tcp_to_object_dist_end":0.0384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50173,-0.16976,0.02499],"object_pos_start":[0.50048,-0.16284,0.02505],"object_to_goal_dist_end":0.01983,"object_to_goal_dist_start":0.01285,"object_z_max":0.02706,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3895.0,"raw_peak_contact_force":3.41509,"tcp_end":[0.48932,-0.08118,0.11481],"tcp_start":[0.48866,-0.12666,0.01997],"tcp_to_object_dist_end":0.12676,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10039,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04114,"contact_1.contact_force":13.20575,"contact_1.contact_offset":0.03019,"contact_1.speed":0.03678,"push_1.push_depth":0.0176,"push_1.push_speed":0.05316,"push_1.push_tolerance":0.04009,"retract_1.retract_speed":0.13143},"optimized_scores":{"best_composite_score":0.60141,"best_fitness_score":0.81141,"best_task_score":0.8258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":172.0,"contact_point_centroid":[0.53641,-0.04319,0.03583],"force_p95":13.24574,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.96045,"mean_force":2.63024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53191,-0.03143,0.01947]},{"body_a":"world","body_b":"push_box","contact_count":145.0,"contact_point_centroid":[0.5378,-0.0807,-8e-05],"force_p95":12.87691,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.27005,"mean_force":3.76718,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53291,-0.02883,0.01981]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53913,-0.11625,0.0536],"force_p95":4.94947,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.35655,"mean_force":1.5004,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5086,-0.10841,0.01925]},{"body_a":"world","body_b":"push_box","contact_count":3899.0,"contact_point_centroid":[0.51424,-0.17438,-1e-05],"force_p95":0.24535,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73321,"mean_force":0.25418,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49844,-0.0824,0.11459]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53167,-0.13874,0.05397],"force_p95":1.55319,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.56729,"mean_force":1.42627,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50126,-0.13066,0.01973]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5213,0.03683,0.17002]},{"body_a":"world","body_b":"push_box","contact_count":2568.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54828,0.05533,0.02974]}],"total_contact_groups":7},"final_pose_error":0.09654,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51409,-0.17414,0.02499],"final_tcp_position":[0.49811,-0.03818,0.21136],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":54.96045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54473,0.07403,0.04219],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":642.0,"n_steps_budget":870.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":15.47385,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2568.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.55498,0.03832,0.02261],"tcp_start":[0.54473,0.07403,0.04219],"tcp_to_object_dist_end":0.03708,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.51621,-0.16417,0.02648],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02158,"object_to_goal_dist_start":0.16043,"object_z_max":0.02703,"peak_contact_force":0.01739,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":324.0,"raw_peak_contact_force":54.96045,"subtask_id":"push","tcp_end":[0.50264,-0.1284,0.01948],"tcp_start":[0.55498,0.03832,0.02261],"tcp_to_object_dist_end":0.03889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51409,-0.17414,0.02499],"object_pos_start":[0.51621,-0.16417,0.02648],"object_to_goal_dist_end":0.02795,"object_to_goal_dist_start":0.02158,"object_z_max":0.02707,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3901.0,"raw_peak_contact_force":2.73321,"tcp_end":[0.49811,-0.03818,0.21136],"tcp_start":[0.50264,-0.1284,0.01948],"tcp_to_object_dist_end":0.23124,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79897,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08707,"contact_1.contact_force":6.81028,"contact_1.contact_offset":0.0308,"contact_1.speed":0.03375,"push_1.push_depth":0.01214,"push_1.push_speed":0.08073,"push_1.push_tolerance":0.04272,"retract_1.retract_speed":0.10934},"optimized_scores":{"best_composite_score":0.63263,"best_fitness_score":0.84263,"best_task_score":0.87506},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":192.0,"contact_point_centroid":[0.52368,-0.02326,0.03138],"force_p95":10.47608,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.66882,"mean_force":3.04833,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52014,-0.01161,0.01845]},{"body_a":"world","body_b":"push_box","contact_count":144.0,"contact_point_centroid":[0.52645,-0.0465,-5e-05],"force_p95":25.44649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.75792,"mean_force":4.62299,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52235,0.00051,0.01868]},{"body_a":"world","body_b":"push_box","contact_count":3937.0,"contact_point_centroid":[0.51556,-0.16804,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.18103,"mean_force":0.25195,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49797,-0.08415,0.09827]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51451,0.05527,0.16465]},{"body_a":"world","body_b":"push_box","contact_count":2640.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5319,0.09118,0.02409]}],"total_contact_groups":5},"final_pose_error":0.12922,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51555,-0.16802,0.02499],"final_tcp_position":[0.49785,-0.04893,0.18042],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":68.66882,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5309,0.11063,0.03243],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":660.0,"n_steps_budget":870.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":15.85042,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53618,0.07392,0.02073],"tcp_start":[0.5309,0.11063,0.03243],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.51536,-0.15603,0.02676],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.0166,"object_to_goal_dist_start":0.1905,"object_z_max":0.02706,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":336.0,"raw_peak_contact_force":68.66882,"subtask_id":"push","tcp_end":[0.50196,-0.12032,0.01924],"tcp_start":[0.53618,0.07392,0.02073],"tcp_to_object_dist_end":0.03888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51555,-0.16802,0.02499],"object_pos_start":[0.51536,-0.15603,0.02676],"object_to_goal_dist_end":0.0238,"object_to_goal_dist_start":0.0166,"object_z_max":0.02676,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3937.0,"raw_peak_contact_force":3.18103,"tcp_end":[0.49785,-0.04893,0.18042],"tcp_start":[0.50196,-0.12032,0.01924],"tcp_to_object_dist_end":0.1966,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```