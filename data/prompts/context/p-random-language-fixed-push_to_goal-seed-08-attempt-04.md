## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 3 | 0.2713 | 0.38 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3559 | 0.09 | ❌ rejected |
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

## Current Skill (Q=0.271) — your mutation base

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

- **Composite score**: 0.271
- **task_score** (E): 0.384
- **fitness_score**: 0.451  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1759 |
| contact_object | 1.00 | 1.00 | 0.0840 |
| push_to_goal | 0.33 | 1.00 | 0.1522 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.001, 0.134) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | descend | 1.00 / step_budget | (0.521, -0.001, 0.134)→(0.524, -0.001, 0.050) | (0.526, -0.001, 0.025)→(0.527, -0.001, 0.024) | 0.156→0.157 | 1.00 / 5.000 | 114.672 | 124.429 |
| push_to_goal | push | 0.33 / step_budget | (0.524, -0.001, 0.050)→(0.494, -0.143, 0.028) | (0.527, -0.001, 0.024)→(0.516, -0.057, 0.025) | 0.157→0.099 | 1.00 / 4.000 | 0.245 | 119.685 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.470
- lateral_force_integral: None
- approach_alignment: 0.721
- goal_progress: 0.461
- terminal_score: 0.461
- phase_score: 0.467
- phase_breakdown.approach_score: 0.094
- phase_breakdown.contact_score: 0.497
- phase_breakdown.push_score: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.465
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.461
- **Median Q (composite search score)**: 0.275
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.428


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13462,"push_to_goal.push_distance":0.07543,"push_to_goal.push_speed":0.09805},"optimized_scores":{"best_composite_score":0.27468,"best_fitness_score":0.45468,"best_task_score":0.26862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":416.0,"contact_point_centroid":[0.4915,0.02928,0.04756],"force_p95":121.68957,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.72484,"mean_force":88.48142,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48331,0.02248,0.04819]},{"body_a":"attachment","body_b":"push_box","contact_count":27.0,"contact_point_centroid":[0.48805,0.05779,0.04904],"force_p95":113.06767,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.12479,"mean_force":89.10451,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.47631,0.05765,0.05088]},{"body_a":"world","body_b":"push_box","contact_count":3059.0,"contact_point_centroid":[0.48085,0.01167,-0.00014],"force_p95":89.81088,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.30359,"mean_force":12.3618,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48661,-0.04871,0.03774]},{"body_a":"world","body_b":"push_box","contact_count":2500.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.99732,"mean_force":1.21233,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.47569,0.0552,0.10614]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48861,0.02578,0.23397]}],"total_contact_groups":5},"final_pose_error":0.09941,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48028,0.00195,0.02499],"final_tcp_position":[0.49303,-0.12676,0.02883],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":127.72484,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":960.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47827,0.05295,0.16771],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":625.0,"n_steps_budget":780.0,"object_pos_end":[0.47983,0.05856,0.02445],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20953,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":114.12479,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2527.0,"raw_peak_contact_force":114.12479,"subtask_id":"contact","tcp_end":[0.4774,0.05782,0.04986],"tcp_start":[0.47827,0.05295,0.16771],"tcp_to_object_dist_end":0.02554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48028,0.00195,0.02499],"object_pos_start":[0.47983,0.05856,0.02445],"object_to_goal_dist_end":0.15323,"object_to_goal_dist_start":0.20953,"object_z_max":0.03526,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3475.0,"raw_peak_contact_force":127.72484,"tcp_end":[0.49303,-0.12676,0.02883],"tcp_start":[0.4774,0.05782,0.04986],"tcp_to_object_dist_end":0.1294,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08687,"push_to_goal.push_distance":0.05289,"push_to_goal.push_speed":0.04355},"optimized_scores":{"best_composite_score":0.25422,"best_fitness_score":0.43422,"best_task_score":0.42103},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.5525,-0.0253,0.04888],"force_p95":115.25703,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.08355,"mean_force":94.47577,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.54075,-0.0253,0.05066]},{"body_a":"attachment","body_b":"push_box","contact_count":704.0,"contact_point_centroid":[0.54443,-0.05266,0.04747],"force_p95":115.90406,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.56811,"mean_force":92.50247,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53483,-0.05749,0.04829]},{"body_a":"world","body_b":"push_box","contact_count":2709.0,"contact_point_centroid":[0.53976,-0.05836,-0.00027],"force_p95":63.63334,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.1844,"mean_force":24.43869,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52338,-0.08182,0.04173]},{"body_a":"world","body_b":"push_box","contact_count":1575.0,"contact_point_centroid":[0.54454,-0.0256,-2e-05],"force_p95":11.82167,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.83325,"mean_force":2.65928,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.53766,-0.02456,0.08076]},{"body_a":"world","body_b":"push_box","contact_count":2464.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51789,-0.0117,0.20941]}],"total_contact_groups":5},"final_pose_error":0.04736,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53056,-0.07988,0.02499],"final_tcp_position":[0.49346,-0.15378,0.02649],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":128.08355,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2464.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53801,-0.0238,0.11906],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":395.0,"n_steps_budget":600.0,"object_pos_end":[0.54559,-0.02565,0.0244],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13244,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":115.33792,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1615.0,"raw_peak_contact_force":128.08355,"subtask_id":"contact","tcp_end":[0.54266,-0.02542,0.04964],"tcp_start":[0.53801,-0.0238,0.11906],"tcp_to_object_dist_end":0.02541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53056,-0.07988,0.02499],"object_pos_start":[0.54559,-0.02565,0.0244],"object_to_goal_dist_end":0.07649,"object_to_goal_dist_start":0.13244,"object_z_max":0.03537,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3413.0,"raw_peak_contact_force":116.56811,"tcp_end":[0.49346,-0.15378,0.02649],"tcp_start":[0.54266,-0.02542,0.04964],"tcp_to_object_dist_end":0.0827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34211,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.0821,"push_to_goal.push_distance":0.05744,"push_to_goal.push_speed":0.02855},"optimized_scores":{"best_composite_score":0.28489,"best_fitness_score":0.46489,"best_task_score":0.46131},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.56266,-0.03466,0.04891],"force_p95":114.48638,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.07739,"mean_force":92.58388,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.55091,-0.03464,0.05072]},{"body_a":"attachment","body_b":"push_box","contact_count":786.0,"contact_point_centroid":[0.55076,-0.06286,0.0475],"force_p95":114.3188,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.76111,"mean_force":90.55817,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54099,-0.06757,0.04809]},{"body_a":"world","body_b":"push_box","contact_count":2674.0,"contact_point_centroid":[0.54919,-0.06393,-0.00028],"force_p95":74.54723,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.5297,"mean_force":27.03693,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53262,-0.08064,0.04383]},{"body_a":"world","body_b":"push_box","contact_count":1496.0,"contact_point_centroid":[0.55482,-0.03512,-2e-05],"force_p95":20.14584,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.16737,"mean_force":2.92269,"phase_index":1.0,"phase_name":"contact_object","phase_type":"descend","tcp_position_centroid":[0.54761,-0.03371,0.07777]},{"body_a":"world","body_b":"push_box","contact_count":2620.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52275,-0.01617,0.20641]}],"total_contact_groups":5},"final_pose_error":0.05542,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53692,-0.09222,0.02499],"final_tcp_position":[0.49464,-0.14993,0.02766],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":131.07739,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2620.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54773,-0.03274,0.11374],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.5559,-0.03518,0.02442],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12771,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":114.55443,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1539.0,"raw_peak_contact_force":131.07739,"subtask_id":"contact","tcp_end":[0.55298,-0.03482,0.04966],"tcp_start":[0.54773,-0.03274,0.11374],"tcp_to_object_dist_end":0.02541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53692,-0.09222,0.02499],"object_pos_start":[0.5559,-0.03518,0.02442],"object_to_goal_dist_end":0.06857,"object_to_goal_dist_start":0.12771,"object_z_max":0.03527,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3460.0,"raw_peak_contact_force":114.76111,"tcp_end":[0.49464,-0.14993,0.02766],"tcp_start":[0.55298,-0.03482,0.04966],"tcp_to_object_dist_end":0.07159,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```