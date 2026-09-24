## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3013 | 0.84 | ✅ accepted |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1158 | 0.72 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3150 | 0.34 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 9 | 0.3745 | 0.38 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.2476 | 0.84 | ✅ accepted |

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

## Current Skill (Q=0.301) — your mutation base

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

- **Composite score**: 0.301
- **task_score** (E): 0.842
- **fitness_score**: 0.731  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2144 |
| establish_contact | 1.00 | 1.00 | 0.0849 |
| push_to_goal | 1.00 | 1.00 | 0.1648 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.546, 0.102, 0.134) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| establish_contact | contact | 1.00 / step_budget | (0.549, 0.077, 0.106)→(0.531, 0.033, 0.037) | (0.526, -0.001, 0.025)→(0.526, -0.003, 0.025) | 0.156→0.154 | 1.00 / 4.000 | 9.443 | 59.383 |
| push_to_goal | push | 1.00 / time_limit | (0.531, 0.033, 0.037)→(0.502, -0.124, 0.023) | (0.526, -0.004, 0.025)→(0.501, -0.133, 0.026) | 0.153→0.029 | 1.00 / 3.000 | 3.632 | 27.030 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.696
- goal_progress: 0.857
- terminal_score: 0.857
- phase_score: 0.712
- phase_breakdown.approach_score: 0.146
- phase_breakdown.contact_score: 0.711
- phase_breakdown.push_score: 0.938

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.770
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.984
- **Median Q (composite search score)**: 0.321
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56818,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1021,"approach_object.offset_behind":0.11905,"establish_contact.contact_face_offset":0.02526,"establish_contact.contact_tolerance":0.00605,"establish_contact.contact_z":0.0182,"push_to_goal.push_distance":0.23921,"push_to_goal.push_speed":0.13635,"push_to_goal.push_time":2.37387},"optimized_scores":{"best_composite_score":0.24357,"best_fitness_score":0.67357,"best_task_score":0.68642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":114.0,"contact_point_centroid":[0.47645,0.07937,0.04879],"force_p95":127.43021,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.58699,"mean_force":46.8571,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.47341,0.09065,0.04594]},{"body_a":"world","body_b":"push_box","contact_count":3112.0,"contact_point_centroid":[0.47968,0.05762,-3e-05],"force_p95":13.82401,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.89588,"mean_force":1.96858,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.46832,0.12477,0.08235]},{"body_a":"attachment","body_b":"push_box","contact_count":717.0,"contact_point_centroid":[0.49285,-0.0248,0.04907],"force_p95":20.09136,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.92482,"mean_force":5.53609,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48149,-0.01792,0.03073]},{"body_a":"world","body_b":"push_box","contact_count":1385.0,"contact_point_centroid":[0.52226,-0.04241,-7e-05],"force_p95":12.25551,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.61022,"mean_force":3.41377,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48181,-0.02032,0.03065]},{"body_a":"world","body_b":"push_box","contact_count":3460.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48196,0.08417,0.21326]}],"total_contact_groups":5},"final_pose_error":0.06138,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51948,-0.0873,0.02723],"final_tcp_position":[0.49325,-0.12809,0.02358],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":157.58699,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3460.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.4659,0.16781,0.13047],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":780.0,"object_pos_end":[0.47993,0.05458,0.02541],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20556,"object_to_goal_dist_start":0.2095,"object_z_max":0.02541,"peak_contact_force":5.66599,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3226.0,"raw_peak_contact_force":157.58699,"subtask_id":"contact","tcp_end":[0.47354,0.08628,0.04087],"tcp_start":[0.47471,0.09146,0.04669],"tcp_to_object_dist_end":0.03585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51948,-0.0873,0.02723],"object_pos_start":[0.48077,0.04956,0.02493],"object_to_goal_dist_end":0.0657,"object_to_goal_dist_start":0.20049,"object_z_max":0.02987,"peak_contact_force":1.72333,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2102.0,"raw_peak_contact_force":38.92482,"subtask_id":"push","tcp_end":[0.49325,-0.12809,0.02358],"tcp_start":[0.47354,0.08628,0.04087],"tcp_to_object_dist_end":0.04863,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08897,"approach_object.offset_behind":0.08605,"establish_contact.contact_face_offset":0.0359,"establish_contact.contact_tolerance":0.00774,"establish_contact.contact_z":0.00783,"push_to_goal.push_distance":0.22245,"push_to_goal.push_speed":0.09013,"push_to_goal.push_time":1.92013},"optimized_scores":{"best_composite_score":0.33977,"best_fitness_score":0.76977,"best_task_score":0.8571},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":695.0,"contact_point_centroid":[0.5241,-0.06662,0.02704],"force_p95":16.54514,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.18977,"mean_force":5.32446,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52632,-0.05492,0.02645]},{"body_a":"world","body_b":"push_box","contact_count":2023.0,"contact_point_centroid":[0.51381,-0.0939,-7e-05],"force_p95":6.03662,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.9623,"mean_force":2.14073,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52606,-0.0558,0.02646]},{"body_a":"world","body_b":"push_box","contact_count":2800.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53177,0.02576,0.20834]},{"body_a":"world","body_b":"push_box","contact_count":1848.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55782,0.03167,0.07417]}],"total_contact_groups":4},"final_pose_error":0.11225,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48467,-0.16102,0.02504],"final_tcp_position":[0.50163,-0.12749,0.02383],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":23.18977,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2800.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.56558,0.05186,0.11882],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":462.0,"n_steps_budget":630.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":17.42769,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.55282,0.01141,0.03373],"tcp_start":[0.56558,0.05186,0.11882],"tcp_to_object_dist_end":0.03893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48467,-0.16102,0.02504],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01888,"object_to_goal_dist_start":0.13211,"object_z_max":0.02544,"peak_contact_force":0.67799,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2718.0,"raw_peak_contact_force":23.18977,"subtask_id":"push","tcp_end":[0.50163,-0.12749,0.02383],"tcp_start":[0.55282,0.01141,0.03373],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90991,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12916,"approach_object.offset_behind":0.14106,"establish_contact.contact_face_offset":0.034,"establish_contact.contact_tolerance":0.00573,"establish_contact.contact_z":0.01238,"push_to_goal.push_distance":0.13312,"push_to_goal.push_speed":0.07822,"push_to_goal.push_time":1.44172},"optimized_scores":{"best_composite_score":0.32052,"best_fitness_score":0.75052,"best_task_score":0.98357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":18.0,"contact_point_centroid":[0.5673,-0.01102,0.03931],"force_p95":19.07122,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.31812,"mean_force":8.87159,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.56713,0.00089,0.03801]},{"body_a":"attachment","body_b":"push_box","contact_count":752.0,"contact_point_centroid":[0.53429,-0.07009,0.02767],"force_p95":14.59805,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.97557,"mean_force":4.71586,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53639,-0.05834,0.02712]},{"body_a":"world","body_b":"push_box","contact_count":2977.0,"contact_point_centroid":[0.55471,-0.03517,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.32333,"mean_force":0.2995,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.58509,0.04321,0.09208]},{"body_a":"world","body_b":"push_box","contact_count":2063.0,"contact_point_centroid":[0.52678,-0.09627,-6e-05],"force_p95":5.55277,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.74083,"mean_force":2.01757,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53741,-0.05626,0.02739]},{"body_a":"world","body_b":"push_box","contact_count":3292.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5532,0.04429,0.22444]}],"total_contact_groups":5},"final_pose_error":0.04261,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49881,-0.15172,0.02495],"final_tcp_position":[0.51028,-0.11641,0.02288],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":20.31812,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":823.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3292.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.60669,0.08746,0.15397],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":753.0,"n_steps_budget":960.0,"object_pos_end":[0.55429,-0.03671,0.02511],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12563,"object_to_goal_dist_start":0.12728,"object_z_max":0.02508,"peak_contact_force":5.23669,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2995.0,"raw_peak_contact_force":20.31812,"subtask_id":"contact","tcp_end":[0.56671,-6e-05,0.03669],"tcp_start":[0.60669,0.08746,0.15397],"tcp_to_object_dist_end":0.04039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49881,-0.15172,0.02495],"object_pos_start":[0.55429,-0.03671,0.02511],"object_to_goal_dist_end":0.00209,"object_to_goal_dist_start":0.12563,"object_z_max":0.02524,"peak_contact_force":8.49409,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2815.0,"raw_peak_contact_force":18.97557,"subtask_id":"push","tcp_end":[0.51028,-0.11641,0.02288],"tcp_start":[0.56671,-6e-05,0.03669],"tcp_to_object_dist_end":0.03719,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```