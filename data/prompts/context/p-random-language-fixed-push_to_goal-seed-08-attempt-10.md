## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2763 | 0.84 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3013 | 0.84 | ✅ accepted |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1158 | 0.72 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3150 | 0.34 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 9 | 0.3745 | 0.38 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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

## Current Skill (Q=0.276) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    offset_behind:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: approach
- id: establish_contact
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_face_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    contact_z:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - offset_behind: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **establish_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_face_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - contact_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.276
- **task_score** (E): 0.839
- **fitness_score**: 0.706  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1969 |
| establish_contact | 1.00 | 1.00 | 0.1177 |
| push_to_goal | 1.00 | 1.00 | 0.1549 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.546, 0.085, 0.140) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| establish_contact | contact | 1.00 / step_budget | (0.546, 0.085, 0.140)→(0.531, 0.031, 0.038) | (0.526, -0.001, 0.025)→(0.526, -0.006, 0.025) | 0.156→0.151 | 1.00 / 3.667 | 5.003 | 84.407 |
| push_to_goal | push | 1.00 / time_limit | (0.531, 0.031, 0.038)→(0.503, -0.116, 0.022) | (0.526, -0.006, 0.025)→(0.511, -0.127, 0.025) | 0.151→0.032 | 1.00 / 3.333 | 1.126 | 27.975 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.685
- goal_progress: 0.931
- terminal_score: 0.931
- phase_score: 0.673
- phase_breakdown.approach_score: 0.110
- phase_breakdown.contact_score: 0.722
- phase_breakdown.push_score: 0.870

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.776
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.994
- **Median Q (composite search score)**: 0.322
- **K-run variance**: 0.0068
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.297


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06061,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1152,"approach_object.offset_behind":0.07354,"establish_contact.contact_face_offset":0.02777,"establish_contact.contact_tolerance":0.00788,"establish_contact.contact_z":0.00957,"push_to_goal.push_distance":0.17246,"push_to_goal.push_speed":0.14269,"push_to_goal.push_time":1.29124},"optimized_scores":{"best_composite_score":0.16023,"best_fitness_score":0.59023,"best_task_score":0.5922},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":76.0,"contact_point_centroid":[0.48089,0.08315,0.04813],"force_p95":162.25283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":206.15193,"mean_force":114.02712,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.47445,0.0925,0.04857]},{"body_a":"world","body_b":"push_box","contact_count":2393.0,"contact_point_centroid":[0.47977,0.05893,-4e-05],"force_p95":28.41807,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.9939,"mean_force":3.88741,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.47053,0.10592,0.09103]},{"body_a":"attachment","body_b":"push_box","contact_count":418.0,"contact_point_centroid":[0.48929,0.00358,0.04936],"force_p95":27.09614,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.85245,"mean_force":8.73724,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47994,0.01315,0.0306]},{"body_a":"world","body_b":"push_box","contact_count":1675.0,"contact_point_centroid":[0.51857,-0.03796,-0.0001],"force_p95":12.84999,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.74067,"mean_force":2.61089,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48339,-0.02066,0.02809]},{"body_a":"world","body_b":"push_box","contact_count":2748.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48457,0.06117,0.22141]}],"total_contact_groups":5},"final_pose_error":0.01168,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53988,-0.07444,0.02499],"final_tcp_position":[0.49211,-0.11099,0.0208],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":206.15193,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2748.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47069,0.12323,0.14512],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":622.0,"n_steps_budget":750.0,"object_pos_end":[0.47925,0.05076,0.02424],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20183,"object_to_goal_dist_start":0.2095,"object_z_max":0.02579,"peak_contact_force":0.77702,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2469.0,"raw_peak_contact_force":206.15193,"subtask_id":"contact","tcp_end":[0.47556,0.09047,0.04027],"tcp_start":[0.47069,0.12323,0.14512],"tcp_to_object_dist_end":0.04299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":899.0,"n_steps_budget":930.0,"object_pos_end":[0.53988,-0.07444,0.02499],"object_pos_start":[0.47925,0.05076,0.02424],"object_to_goal_dist_end":0.08544,"object_to_goal_dist_start":0.20183,"object_z_max":0.02752,"peak_contact_force":0.24526,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2093.0,"raw_peak_contact_force":42.85245,"subtask_id":"push","tcp_end":[0.49211,-0.11099,0.0208],"tcp_start":[0.47556,0.09047,0.04027],"tcp_to_object_dist_end":0.0603,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91346,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10185,"approach_object.offset_behind":0.10907,"establish_contact.contact_face_offset":0.03175,"establish_contact.contact_tolerance":0.00871,"establish_contact.contact_z":0.01146,"push_to_goal.push_distance":0.14199,"push_to_goal.push_speed":0.08513,"push_to_goal.push_time":1.50183},"optimized_scores":{"best_composite_score":0.34639,"best_fitness_score":0.77639,"best_task_score":0.93083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":733.0,"contact_point_centroid":[0.52512,-0.06673,0.02748],"force_p95":16.36903,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.78453,"mean_force":5.71494,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5269,-0.05494,0.02707]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.55219,-0.00213,0.0383],"force_p95":20.29891,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.52693,"mean_force":13.16837,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55231,0.00978,0.03826]},{"body_a":"world","body_b":"push_box","contact_count":2391.0,"contact_point_centroid":[0.54438,-0.02562,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.93128,"mean_force":0.37156,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.56098,0.03998,0.08046]},{"body_a":"world","body_b":"push_box","contact_count":2098.0,"contact_point_centroid":[0.5202,-0.09409,-7e-05],"force_p95":6.12649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.41198,"mean_force":2.28748,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52715,-0.05437,0.02718]},{"body_a":"world","body_b":"push_box","contact_count":2900.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53567,0.03608,0.21373]}],"total_contact_groups":5},"final_pose_error":0.04204,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49296,-0.15583,0.02508],"final_tcp_position":[0.50497,-0.12074,0.02266],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":21.78453,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2900.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.57318,0.07239,0.13024],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":607.0,"n_steps_budget":750.0,"object_pos_end":[0.54421,-0.02823,0.02512],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12955,"object_to_goal_dist_start":0.13211,"object_z_max":0.02509,"peak_contact_force":0.32178,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2414.0,"raw_peak_contact_force":21.52693,"subtask_id":"contact","tcp_end":[0.552,0.00851,0.03624],"tcp_start":[0.57318,0.07239,0.13024],"tcp_to_object_dist_end":0.03917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49296,-0.15583,0.02508],"object_pos_start":[0.54421,-0.02823,0.02512],"object_to_goal_dist_end":0.00914,"object_to_goal_dist_start":0.12955,"object_z_max":0.02537,"peak_contact_force":1.13406,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2831.0,"raw_peak_contact_force":21.78453,"subtask_id":"push","tcp_end":[0.50497,-0.12074,0.02266],"tcp_start":[0.552,0.00851,0.03624],"tcp_to_object_dist_end":0.03717,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90385,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11813,"approach_object.offset_behind":0.1097,"establish_contact.contact_face_offset":0.02877,"establish_contact.contact_tolerance":0.00592,"establish_contact.contact_z":0.01406,"push_to_goal.push_distance":0.10108,"push_to_goal.push_speed":0.07401,"push_to_goal.push_time":2.44223},"optimized_scores":{"best_composite_score":0.32214,"best_fitness_score":0.75214,"best_task_score":0.99373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.56564,-0.01301,0.04508],"force_p95":22.81316,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.54199,"mean_force":12.97797,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.56584,-0.00105,0.04502]},{"body_a":"attachment","body_b":"push_box","contact_count":751.0,"contact_point_centroid":[0.53439,-0.07104,0.02824],"force_p95":14.45919,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.28865,"mean_force":5.0408,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53632,-0.05926,0.0278]},{"body_a":"world","body_b":"push_box","contact_count":2350.0,"contact_point_centroid":[0.55447,-0.0357,-1e-05],"force_p95":0.46703,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.81874,"mean_force":0.50171,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.57745,0.0281,0.09052]},{"body_a":"world","body_b":"push_box","contact_count":2133.0,"contact_point_centroid":[0.52653,-0.09881,-5e-05],"force_p95":5.54861,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.6722,"mean_force":2.06796,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53648,-0.05898,0.02787]},{"body_a":"world","body_b":"push_box","contact_count":2912.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.54582,0.03012,0.2207]}],"total_contact_groups":5},"final_pose_error":0.01765,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50071,-0.15037,0.02501],"final_tcp_position":[0.51171,-0.11504,0.02162],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":25.54199,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.59298,0.06009,0.14507],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":614.0,"n_steps_budget":810.0,"object_pos_end":[0.55324,-0.04135,0.02477],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.121,"object_to_goal_dist_start":0.12728,"object_z_max":0.02509,"peak_contact_force":13.90916,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2396.0,"raw_peak_contact_force":25.54199,"subtask_id":"contact","tcp_end":[0.56435,-0.00484,0.03896],"tcp_start":[0.59298,0.06009,0.14507],"tcp_to_object_dist_end":0.04072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50071,-0.15037,0.02501],"object_pos_start":[0.55324,-0.04135,0.02477],"object_to_goal_dist_end":0.0008,"object_to_goal_dist_start":0.121,"object_z_max":0.02531,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2884.0,"raw_peak_contact_force":19.28865,"subtask_id":"push","tcp_end":[0.51171,-0.11504,0.02162],"tcp_start":[0.56435,-0.00484,0.03896],"tcp_to_object_dist_end":0.03716,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```