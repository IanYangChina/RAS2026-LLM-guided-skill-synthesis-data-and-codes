## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 4 | 0.5837 | 0.03 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7829 | 0.87 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.7955 | 0.88 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

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

## Current Skill (Q=0.584) — your mutation base

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
    offset:
    - 0.0
    - 0.08
    - 0.0
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
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
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.0
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_depth:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
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
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0]
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.0, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.584
- **task_score** (E): 0.026
- **fitness_score**: 0.258  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.556
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2901 |
| contact_1 | 0.67 | 1.00 | 0.0402 |
| push_1 | 1.00 | 1.00 | 0.0040 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.496, 0.104, 0.032)→(0.495, 0.065, 0.021) | (0.500, 0.029, 0.025)→(0.500, 0.028, 0.025) | 0.180→0.179 | 1.00 / 4.333 | 14.502 | 3.636 |
| push_1 | push | 1.00 / force_exceeded | (0.495, 0.065, 0.021)→(0.493, 0.062, 0.019) | (0.500, 0.028, 0.025)→(0.499, 0.025, 0.025) | 0.179→0.175 | 1.00 / 5.000 | 2603.877 | 22.981 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.022
- lateral_force_integral: None
- approach_alignment: 0.363
- goal_progress: 0.021
- terminal_score: 0.021
- phase_score: 0.401
- phase_breakdown.push_score: 0.016
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.760

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.278
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.038
- **Median Q (composite search score)**: 0.684
- **K-run variance**: 0.0205
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.514


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65432,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":19.14695,"push_1.push_depth":0.04981,"push_1.push_force_limit":21.53118,"push_1.push_speed":0.10241},"optimized_scores":{"best_composite_score":0.38124,"best_fitness_score":0.2779,"best_task_score":0.03778},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53016,-0.01071,0.04996],"force_p95":22.25292,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.93135,"mean_force":11.92795,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49931,0.01371,0.02005]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.5122,0.00273,0.04589],"force_p95":15.36468,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.08467,"mean_force":5.86345,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49977,0.01458,0.02054]},{"body_a":"world","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.50195,-0.03732,-4e-05],"force_p95":11.14457,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.24481,"mean_force":5.01418,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49958,0.0142,0.02034]},{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.50444,0.00473,0.03052],"force_p95":7.87173,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.41805,"mean_force":2.72216,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49975,0.01661,0.02104]},{"body_a":"world","body_b":"push_box","contact_count":1970.0,"contact_point_centroid":[0.5046,-0.01915,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.26237,"mean_force":0.30114,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49829,0.03656,0.02496]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49925,0.02864,0.16605]}],"total_contact_groups":6},"final_pose_error":0.21314,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50542,-0.0238,0.02489],"final_tcp_position":[0.49916,0.01331,0.01988],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":23.93135,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.50565,-0.02204,0.02505],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12808,"object_to_goal_dist_start":0.13127,"object_z_max":0.02508,"peak_contact_force":1.08308,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2010.0,"raw_peak_contact_force":10.41805,"subtask_id":"contact","tcp_end":[0.49992,0.01485,0.02074],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.03758,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50542,-0.0238,0.02489],"object_pos_start":[0.50565,-0.02204,0.02505],"object_to_goal_dist_end":0.12631,"object_to_goal_dist_start":0.12808,"object_z_max":0.02511,"peak_contact_force":23.93135,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":30.0,"raw_peak_contact_force":23.93135,"subtask_id":"push","tcp_end":[0.49916,0.01331,0.01988],"tcp_start":[0.49992,0.01485,0.02074],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67857,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":3.96381,"push_1.push_depth":-0.01158,"push_1.push_force_limit":24.97045,"push_1.push_speed":0.12315},"optimized_scores":{"best_composite_score":0.68535,"best_fitness_score":0.24868,"best_task_score":0.02071},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":37.0,"contact_point_centroid":[0.51137,0.07074,0.02543],"force_p95":18.88001,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.42539,"mean_force":10.6184,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50866,0.08264,0.0196]},{"body_a":"push_box","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53836,0.06825,0.04977],"force_p95":21.5999,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.97042,"mean_force":13.21606,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5081,0.08158,0.01904]},{"body_a":"world","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.51358,0.04611,-7e-05],"force_p95":11.38606,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.45721,"mean_force":5.91058,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50862,0.08249,0.01955]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":1832.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50835,0.10239,0.02374]}],"total_contact_groups":5},"final_pose_error":0.21889,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51324,0.04368,0.02479],"final_tcp_position":[0.50775,0.08024,0.01872],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":3899.80745,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":21.47595,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50982,0.08463,0.02081],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.51324,0.04368,0.02479],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19413,"object_to_goal_dist_start":0.19823,"object_z_max":0.02519,"peak_contact_force":3899.80745,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":168.0,"raw_peak_contact_force":22.42539,"subtask_id":"push","tcp_end":[0.50775,0.08024,0.01872],"tcp_start":[0.50982,0.08463,0.02081],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68235,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.71454,"push_1.push_depth":0.04177,"push_1.push_force_limit":24.12863,"push_1.push_speed":0.1084},"optimized_scores":{"best_composite_score":0.68444,"best_fitness_score":0.24777,"best_task_score":0.01891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.47408,0.08136,0.02061],"force_p95":21.31343,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.58678,"mean_force":10.3492,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47377,0.09332,0.02049]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.50327,0.08102,0.04983],"force_p95":21.22079,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.54636,"mean_force":16.12843,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47336,0.0918,0.01988]},{"body_a":"world","body_b":"push_box","contact_count":102.0,"contact_point_centroid":[0.48058,0.05888,-3e-05],"force_p95":10.05647,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.10628,"mean_force":5.50743,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47375,0.0932,0.02045]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":1816.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47369,0.11284,0.02458]}],"total_contact_groups":5},"final_pose_error":0.28432,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47944,0.05451,0.02487],"final_tcp_position":[0.47327,0.09103,0.01968],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":3887.8908,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":20.94631,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4745,0.09544,0.02151],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":36.0,"n_steps_budget":1000.0,"object_pos_end":[0.47944,0.05451,0.02487],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20554,"object_to_goal_dist_start":0.2095,"object_z_max":0.02508,"peak_contact_force":3887.8908,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":151.0,"raw_peak_contact_force":22.58678,"subtask_id":"push","tcp_end":[0.47327,0.09103,0.01968],"tcp_start":[0.4745,0.09544,0.02151],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```