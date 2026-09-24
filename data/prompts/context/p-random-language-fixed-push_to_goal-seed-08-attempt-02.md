## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 3 | 0.2800 | 0.38 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 3 | 0.2792 | 0.38 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.280) — your mutation base

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
  subtask_id: approach
- id: contact_object
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  subtask_id: contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
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
      default: 0.15
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **contact_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.280
- **task_score** (E): 0.382
- **fitness_score**: 0.460  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1862 |
| contact_object | 1.00 | 1.00 | 0.0730 |
| push_to_goal | 0.33 | 1.00 | 0.1497 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.001, 0.123) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | descend | 1.00 / step_budget | (0.521, -0.001, 0.123)→(0.524, -0.001, 0.050) | (0.526, -0.001, 0.025)→(0.527, -0.001, 0.024) | 0.156→0.157 | 1.00 / 5.000 | 115.278 | 124.872 |
| push_to_goal | push | 0.33 / step_budget | (0.524, -0.001, 0.050)→(0.494, -0.141, 0.027) | (0.527, -0.001, 0.024)→(0.516, -0.057, 0.025) | 0.157→0.100 | 1.00 / 4.000 | 0.245 | 121.195 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.467
- lateral_force_integral: None
- approach_alignment: 0.716
- goal_progress: 0.458
- terminal_score: 0.458
- phase_score: 0.489
- phase_breakdown.approach_score: 0.097
- phase_breakdown.contact_score: 0.497
- phase_breakdown.push_score: 0.642

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.477
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.458
- **Median Q (composite search score)**: 0.281
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.10024,"push_to_goal.push_distance":0.05158,"push_to_goal.push_speed":0.0936},"optimized_scores":{"best_composite_score":0.28132,"best_fitness_score":0.46132,"best_task_score":0.26802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":427.0,"contact_point_centroid":[0.49184,0.02939,0.04751],"force_p95":123.81481,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.98938,"mean_force":90.9638,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4835,0.02275,0.04801]},{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.48802,0.05772,0.04899],"force_p95":115.16967,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.05944,"mean_force":92.71862,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.47627,0.05758,0.05078]},{"body_a":"world","body_b":"push_box","contact_count":3060.0,"contact_point_centroid":[0.48104,0.01225,-0.00015],"force_p95":92.29537,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.43441,"mean_force":13.02485,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4866,-0.04659,0.03715]},{"body_a":"world","body_b":"push_box","contact_count":1836.0,"contact_point_centroid":[0.47925,0.05848,-1e-05],"force_p95":8.18229,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.099,"mean_force":1.66672,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.47542,0.05557,0.08945]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48824,0.02636,0.21688]}],"total_contact_groups":5},"final_pose_error":0.07744,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48037,0.00209,0.02499],"final_tcp_position":[0.49297,-0.12487,0.02748],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":129.98938,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47776,0.05376,0.13393],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.47991,0.05858,0.02444],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20954,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":116.05944,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1864.0,"raw_peak_contact_force":116.05944,"subtask_id":"contact","tcp_end":[0.47744,0.05777,0.04978],"tcp_start":[0.47776,0.05376,0.13393],"tcp_to_object_dist_end":0.02548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48037,0.00209,0.02499],"object_pos_start":[0.47991,0.05858,0.02444],"object_to_goal_dist_end":0.15335,"object_to_goal_dist_start":0.20954,"object_z_max":0.03522,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3487.0,"raw_peak_contact_force":129.98938,"tcp_end":[0.49297,-0.12487,0.02748],"tcp_start":[0.47744,0.05777,0.04978],"tcp_to_object_dist_end":0.12761,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33117,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08993,"push_to_goal.push_distance":0.05018,"push_to_goal.push_speed":0.03133},"optimized_scores":{"best_composite_score":0.26192,"best_fitness_score":0.44192,"best_task_score":0.42108},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.55247,-0.02531,0.04889],"force_p95":114.89682,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.53607,"mean_force":94.04696,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.54072,-0.02531,0.05069]},{"body_a":"attachment","body_b":"push_box","contact_count":716.0,"contact_point_centroid":[0.54441,-0.05273,0.04749],"force_p95":116.29868,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.86898,"mean_force":92.76241,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53478,-0.05754,0.04824]},{"body_a":"world","body_b":"push_box","contact_count":2713.0,"contact_point_centroid":[0.54009,-0.0576,-0.00026],"force_p95":64.01805,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.16827,"mean_force":24.88157,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52409,-0.08005,0.042]},{"body_a":"world","body_b":"push_box","contact_count":1618.0,"contact_point_centroid":[0.54456,-0.02558,-2e-05],"force_p95":7.8219,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.5469,"mean_force":2.52577,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.53764,-0.02455,0.08233]},{"body_a":"world","body_b":"push_box","contact_count":2424.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51789,-0.0117,0.21088]}],"total_contact_groups":5},"final_pose_error":0.04708,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53062,-0.07991,0.02499],"final_tcp_position":[0.49428,-0.15149,0.02655],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":127.53607,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.538,-0.02378,0.1221],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.54559,-0.02565,0.02439],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13244,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":114.99005,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1657.0,"raw_peak_contact_force":127.53607,"subtask_id":"contact","tcp_end":[0.54258,-0.02542,0.04966],"tcp_start":[0.538,-0.02378,0.1221],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53062,-0.07991,0.02499],"object_pos_start":[0.54559,-0.02565,0.02439],"object_to_goal_dist_end":0.07648,"object_to_goal_dist_start":0.13244,"object_z_max":0.03536,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3429.0,"raw_peak_contact_force":116.86898,"tcp_end":[0.49428,-0.15149,0.02655],"tcp_start":[0.54258,-0.02542,0.04966],"tcp_to_object_dist_end":0.08029,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34416,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08011,"push_to_goal.push_distance":0.05014,"push_to_goal.push_speed":0.02937},"optimized_scores":{"best_composite_score":0.29667,"best_fitness_score":0.47667,"best_task_score":0.45774},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.56266,-0.03466,0.04889],"force_p95":114.77768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.02127,"mean_force":93.57002,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.55092,-0.03464,0.05069]},{"body_a":"attachment","body_b":"push_box","contact_count":804.0,"contact_point_centroid":[0.55097,-0.06291,0.04741],"force_p95":116.24341,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.7269,"mean_force":92.26264,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54118,-0.06757,0.04803]},{"body_a":"world","body_b":"push_box","contact_count":2661.0,"contact_point_centroid":[0.54981,-0.06287,-0.0003],"force_p95":74.49963,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.93374,"mean_force":28.2997,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53394,-0.07852,0.04415]},{"body_a":"world","body_b":"push_box","contact_count":1464.0,"contact_point_centroid":[0.55483,-0.03512,-2e-05],"force_p95":22.25987,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.15154,"mean_force":3.0106,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.54763,-0.03373,0.07673]},{"body_a":"world","body_b":"push_box","contact_count":2644.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52277,-0.01618,0.2054]}],"total_contact_groups":5},"final_pose_error":0.0517,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53722,-0.09187,0.02499],"final_tcp_position":[0.49624,-0.14674,0.02742],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":131.02127,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54777,-0.03278,0.11166],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.5559,-0.03518,0.02441],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12771,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":114.78303,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1507.0,"raw_peak_contact_force":131.02127,"subtask_id":"contact","tcp_end":[0.55299,-0.03482,0.04965],"tcp_start":[0.54777,-0.03278,0.11166],"tcp_to_object_dist_end":0.0254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53722,-0.09187,0.02499],"object_pos_start":[0.5559,-0.03518,0.02441],"object_to_goal_dist_end":0.06902,"object_to_goal_dist_start":0.12771,"object_z_max":0.03529,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3465.0,"raw_peak_contact_force":116.7269,"tcp_end":[0.49624,-0.14674,0.02742],"tcp_start":[0.55299,-0.03482,0.04965],"tcp_to_object_dist_end":0.06852,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```