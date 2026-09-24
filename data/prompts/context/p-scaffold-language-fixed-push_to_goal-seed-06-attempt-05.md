## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5115 | 0.95 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.5289 | 0.82 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4839 | 0.76 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4843 | 0.76 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4871 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.511) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
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
    - 0.03
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
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
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
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
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.05], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.511
- **task_score** (E): 0.947
- **fitness_score**: 0.805  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2450 |
| contact_1 | 0.67 | 1.00 | 0.0586 |
| push_1 | 1.00 | 1.00 | 0.1883 |
| retract_1 | 1.00 | 1.00 | 0.1133 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.099, 0.079) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.496, 0.099, 0.079)→(0.495, 0.066, 0.031) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.667 | 25303.057 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.066, 0.031)→(0.493, -0.121, 0.027) | (0.500, 0.029, 0.025)→(0.511, -0.155, 0.030) | 0.180→0.015 | 1.00 / 3.333 | 30.276 | 62.459 |
| retract_1 | retract | 1.00 / step_budget | (0.493, -0.121, 0.027)→(0.506, -0.150, 0.135) | (0.511, -0.155, 0.030)→(0.506, -0.153, 0.025) | 0.015→0.009 | 1.00 / 4.000 | 0.245 | 26.887 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.873
- goal_progress: 0.973
- terminal_score: 0.973
- phase_score: 0.717
- phase_breakdown.push_score: 0.839
- phase_breakdown.approach_score: 0.353
- phase_breakdown.contact_score: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.819
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.973
- **Median Q (composite search score)**: 0.582
- **K-run variance**: 0.0143
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11828,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03003,"approach_1.speed":0.07893,"contact_1.contact_force":10.93399,"contact_1.speed":0.02783,"push_1.push_depth":0.16048,"push_1.speed":0.0329,"retract_1.retract_height":0.12278,"retract_1.speed":0.0373},"optimized_scores":{"best_composite_score":0.34311,"best_fitness_score":0.80311,"best_task_score":0.93455},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":263.0,"contact_point_centroid":[0.50427,-0.06041,0.04337],"force_p95":49.39859,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.21308,"mean_force":9.23719,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49414,-0.04881,0.0247]},{"body_a":"push_box","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.52891,-0.0698,0.05236],"force_p95":33.22916,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.91116,"mean_force":7.07796,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49368,-0.05555,0.02439]},{"body_a":"world","body_b":"push_box","contact_count":405.0,"contact_point_centroid":[0.50711,-0.09215,-0.00012],"force_p95":26.82039,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.20126,"mean_force":7.51399,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49473,-0.03959,0.02506]},{"body_a":"world","body_b":"push_box","contact_count":1192.0,"contact_point_centroid":[0.50244,-0.16488,-6e-05],"force_p95":0.49682,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.76986,"mean_force":0.31838,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49416,-0.14045,0.08476]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52591,-0.13733,0.05184],"force_p95":2.02909,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.16278,"mean_force":1.1634,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49065,-0.12315,0.02374]},{"body_a":"attachment","body_b":"push_box","contact_count":69.0,"contact_point_centroid":[0.4944,-0.13915,0.04294],"force_p95":0.97572,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.13223,"mean_force":0.68467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49015,-0.12742,0.03845]},{"body_a":"world","body_b":"push_box","contact_count":1848.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.02679,0.18811]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49859,0.03436,0.04618]}],"total_contact_groups":8},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50158,-0.15844,0.02499],"final_tcp_position":[0.4988,-0.15329,0.13011],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":56.21308,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50086,0.05499,0.07344],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49966,0.01878,0.02871],"tcp_start":[0.50086,0.05499,0.07344],"tcp_to_object_dist_end":0.03809,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.50326,-0.15788,0.026],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00858,"object_to_goal_dist_start":0.13127,"object_z_max":0.02712,"peak_contact_force":4e-05,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":737.0,"raw_peak_contact_force":56.21308,"subtask_id":"push","tcp_end":[0.49094,-0.1225,0.02382],"tcp_start":[0.49966,0.01878,0.02871],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.50158,-0.15844,0.02499],"object_pos_start":[0.50326,-0.15788,0.026],"object_to_goal_dist_end":0.00859,"object_to_goal_dist_start":0.00858,"object_z_max":0.02933,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1267.0,"raw_peak_contact_force":2.76986,"tcp_end":[0.4988,-0.15329,0.13011],"tcp_start":[0.49094,-0.1225,0.02382],"tcp_to_object_dist_end":0.10529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93623,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03545,"approach_1.speed":0.0196,"contact_1.contact_force":7.80196,"contact_1.speed":0.0289,"push_1.push_depth":0.22567,"push_1.speed":0.01242,"retract_1.retract_height":0.15447,"retract_1.speed":0.0501},"optimized_scores":{"best_composite_score":0.60936,"best_fitness_score":0.81936,"best_task_score":0.97333},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":419.0,"contact_point_centroid":[0.51051,-0.03896,0.04538],"force_p95":49.01483,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.40816,"mean_force":14.01195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49825,-0.02811,0.02598]},{"body_a":"push_box","body_b":"link7","contact_count":197.0,"contact_point_centroid":[0.52789,-0.08782,0.05562],"force_p95":50.02845,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.33407,"mean_force":17.06475,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49518,-0.07185,0.02608]},{"body_a":"world","body_b":"push_box","contact_count":622.0,"contact_point_centroid":[0.51751,-0.07716,-0.00014],"force_p95":37.47173,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.81759,"mean_force":14.11795,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49848,-0.02526,0.02603]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52789,-0.14325,0.05521],"force_p95":35.24536,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.44694,"mean_force":18.4645,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49235,-0.12113,0.02679]},{"body_a":"attachment","body_b":"push_box","contact_count":58.0,"contact_point_centroid":[0.50746,-0.13368,0.05864],"force_p95":11.83157,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.64055,"mean_force":2.10094,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4917,-0.12445,0.04086]},{"body_a":"world","body_b":"push_box","contact_count":1635.0,"contact_point_centroid":[0.50503,-0.15798,-5e-05],"force_p95":0.53799,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.47344,"mean_force":0.32347,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49684,-0.13889,0.10544]},{"body_a":"world","body_b":"push_box","contact_count":2148.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50437,0.05671,0.18882]},{"body_a":"world","body_b":"push_box","contact_count":3144.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50865,0.09708,0.0465]}],"total_contact_groups":8},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50262,-0.15459,0.02499],"final_tcp_position":[0.5026,-0.15257,0.1659],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5104,0.1161,0.0756],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3144.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50982,0.08465,0.02993],"tcp_start":[0.5104,0.1161,0.0756],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,-0.15643,0.03058],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.01082,"object_to_goal_dist_start":0.19823,"object_z_max":0.03057,"peak_contact_force":39.40537,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1238.0,"raw_peak_contact_force":60.40816,"subtask_id":"push","tcp_end":[0.49257,-0.12065,0.02684],"tcp_start":[0.50982,0.08465,0.02993],"tcp_to_object_dist_end":0.03865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.50262,-0.15459,0.02499],"object_pos_start":[0.50668,-0.15643,0.03058],"object_to_goal_dist_end":0.00529,"object_to_goal_dist_start":0.01082,"object_z_max":0.03058,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1699.0,"raw_peak_contact_force":37.44694,"tcp_end":[0.5026,-0.15257,0.1659],"tcp_start":[0.49257,-0.12065,0.02684],"tcp_to_object_dist_end":0.14093,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16045,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04866,"approach_1.speed":0.08715,"contact_1.contact_force":12.47347,"contact_1.speed":0.02584,"push_1.push_depth":0.23683,"push_1.speed":0.04035,"retract_1.retract_height":0.0961,"retract_1.speed":0.06606},"optimized_scores":{"best_composite_score":0.58201,"best_fitness_score":0.79201,"best_task_score":0.93206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":437.0,"contact_point_centroid":[0.49689,-0.03155,0.0458],"force_p95":57.21663,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.75548,"mean_force":16.32849,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48426,-0.02255,0.03002]},{"body_a":"push_box","body_b":"link7","contact_count":198.0,"contact_point_centroid":[0.52754,-0.09606,0.05869],"force_p95":56.39434,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.03151,"mean_force":30.43496,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49157,-0.08726,0.03036]},{"body_a":"world","body_b":"push_box","contact_count":714.0,"contact_point_centroid":[0.50972,-0.0658,-0.00011],"force_p95":47.42007,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.66695,"mean_force":16.41934,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48392,-0.01983,0.03001]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53804,-0.12925,0.05658],"force_p95":36.71853,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.44302,"mean_force":19.771,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49533,-0.12128,0.03072]},{"body_a":"attachment","body_b":"push_box","contact_count":57.0,"contact_point_centroid":[0.51132,-0.12986,0.04872],"force_p95":15.71764,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.53792,"mean_force":2.65428,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49819,-0.12574,0.04499]},{"body_a":"world","body_b":"push_box","contact_count":767.0,"contact_point_centroid":[0.52377,-0.15131,-0.00012],"force_p95":0.93913,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.22368,"mean_force":0.47029,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50689,-0.13531,0.07723]},{"body_a":"world","body_b":"push_box","contact_count":1992.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48849,0.06166,0.19474]},{"body_a":"world","body_b":"push_box","contact_count":1736.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47493,0.11046,0.05931]}],"total_contact_groups":8},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51383,-0.14665,0.02499],"final_tcp_position":[0.51637,-0.14512,0.11037],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":70.75548,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47793,0.12576,0.08848],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":15.38848,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47493,0.09542,0.03354],"tcp_start":[0.47793,0.12576,0.08848],"tcp_to_object_dist_end":0.03817,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.52326,-0.14955,0.03222],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.02436,"object_to_goal_dist_start":0.2095,"object_z_max":0.03226,"peak_contact_force":51.42128,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1349.0,"raw_peak_contact_force":70.75548,"subtask_id":"push","tcp_end":[0.49555,-0.12076,0.03067],"tcp_start":[0.47493,0.09542,0.03354],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":990.0,"object_pos_end":[0.51383,-0.14665,0.02499],"object_pos_start":[0.52326,-0.14955,0.03222],"object_to_goal_dist_end":0.01423,"object_to_goal_dist_start":0.02436,"object_z_max":0.0335,"peak_contact_force":0.24519,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":832.0,"raw_peak_contact_force":40.44302,"tcp_end":[0.51637,-0.14512,0.11037],"tcp_start":[0.49555,-0.12076,0.03067],"tcp_to_object_dist_end":0.08544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```