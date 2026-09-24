## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5565 | 0.39 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5559 | 0.39 | ✅ accepted |
| 1 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.2100 | 0.00 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.2100 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.557) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_progress
  target_entity: object
  metric: goal_progress
  weight: 0.7
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
    - 0.0
    - 0.15
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: no_obstacle
    when: before_phase
    predicate: force_below
    threshold: 5.0
    on_failure: abort
  subtask_id: approach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    tolerance: 0.02
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 1.5
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_obtained
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: approach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.03
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: abort
  subtask_id: push_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=no_obstacle, when=before_phase, predicate=force_below, on_failure=abort, threshold=5.0
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], tolerance=0.02
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_obtained, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=0.0

## Design Metrics

- **Composite score**: 0.557
- **task_score** (E): 0.391
- **fitness_score**: 0.337  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1177 |
| descend_1 | 1.00 | 1.00 | 0.1374 |
| push_1 | 1.00 | 1.00 | 0.1522 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.002, 0.192) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / force_exceeded | (0.509, 0.002, 0.192)→(0.509, 0.002, 0.055) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 50612.789 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.509, 0.002, 0.055)→(0.496, -0.139, 0.022) | (0.513, 0.002, 0.025)→(0.527, -0.054, 0.025) | 0.160→0.100 | 1.00 / 4.000 | 0.260 | 170.122 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.675
- lateral_force_integral: None
- approach_alignment: 0.705
- goal_progress: 0.537
- terminal_score: 0.537
- phase_score: 0.404
- phase_breakdown.push_progress_score: 0.537
- phase_breakdown.approach_object_score: 0.093

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.457
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.537
- **Median Q (composite search score)**: 0.522
- **K-run variance**: 0.0078
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.383


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29508,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.48719,"descend_1.descend_force_threshold":3.35881,"descend_1.descend_speed":0.16321,"push_1.push_speed":0.1397,"push_1.push_timeout":9.99624},"optimized_scores":{"best_composite_score":0.67746,"best_fitness_score":0.45746,"best_task_score":0.53749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1073.0,"contact_point_centroid":[0.47916,-0.05688,-0.00054],"force_p95":166.81504,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.68501,"mean_force":51.35828,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4675,-0.07512,0.04467]},{"body_a":"attachment","body_b":"push_box","contact_count":433.0,"contact_point_centroid":[0.47412,-0.06162,0.04557],"force_p95":172.49394,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":210.53163,"mean_force":114.09845,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46583,-0.06623,0.04911]},{"body_a":"push_box","body_b":"link7","contact_count":148.0,"contact_point_centroid":[0.51906,-0.09068,0.06437],"force_p95":59.47503,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.85642,"mean_force":33.63123,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48464,-0.12056,0.03179]},{"body_a":"world","body_b":"push_box","contact_count":868.0,"contact_point_centroid":[0.45028,-0.03158,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47895,-0.01238,0.24781]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45095,-0.0284,0.1248]}],"total_contact_groups":5},"final_pose_error":0.01135,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51254,-0.09194,0.02428],"final_tcp_position":[0.49264,-0.14171,0.02256],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.45693,-0.02593,0.19298],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":547.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.447,-0.03104,0.05622],"tcp_start":[0.45693,-0.02593,0.19298],"tcp_to_object_dist_end":0.0314,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":600.0,"n_steps_budget":630.0,"object_pos_end":[0.51254,-0.09194,0.02428],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0594,"object_to_goal_dist_start":0.12843,"object_z_max":0.03941,"peak_contact_force":0.28986,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1654.0,"raw_peak_contact_force":212.68501,"subtask_id":"push_progress","tcp_end":[0.49264,-0.14171,0.02256],"tcp_start":[0.447,-0.03104,0.05622],"tcp_to_object_dist_end":0.05363,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07692,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1893,"descend_1.descend_force_threshold":3.18939,"descend_1.descend_speed":0.0278,"push_1.push_speed":0.16559,"push_1.push_timeout":3.76928},"optimized_scores":{"best_composite_score":0.52197,"best_fitness_score":0.30197,"best_task_score":0.34887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":323.0,"contact_point_centroid":[0.55012,-0.0237,0.04838],"force_p95":142.3654,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.18591,"mean_force":93.38246,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54142,-0.02922,0.05066]},{"body_a":"world","body_b":"push_box","contact_count":1607.0,"contact_point_centroid":[0.54458,-0.03822,-0.00025],"force_p95":77.33486,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.17372,"mean_force":19.28397,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52326,-0.07365,0.03777]},{"body_a":"push_box","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.55941,-0.06087,0.06473],"force_p95":10.3327,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.35907,"mean_force":6.06388,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52181,-0.07874,0.03654]},{"body_a":"world","body_b":"push_box","contact_count":916.0,"contact_point_centroid":[0.55317,0.00136,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51979,0.00052,0.24665]},{"body_a":"world","body_b":"push_box","contact_count":3340.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54371,0.00112,0.11859]}],"total_contact_groups":5},"final_pose_error":0.01088,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53996,-0.05349,0.02499],"final_tcp_position":[0.49879,-0.13974,0.02157],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":147.18591,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":916.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54178,0.00107,0.19109],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":51.29305,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3340.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.54816,0.00123,0.05377],"tcp_start":[0.54178,0.00107,0.19109],"tcp_to_object_dist_end":0.02921,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.53996,-0.05349,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.10446,"object_to_goal_dist_start":0.16043,"object_z_max":0.03484,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1965.0,"raw_peak_contact_force":147.18591,"subtask_id":"push_progress","tcp_end":[0.49879,-0.13974,0.02157],"tcp_start":[0.54816,0.00123,0.05377],"tcp_to_object_dist_end":0.09564,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.225,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31075,"descend_1.descend_force_threshold":2.03368,"descend_1.descend_speed":0.07336,"push_1.push_speed":0.23432,"push_1.push_timeout":1.98842},"optimized_scores":{"best_composite_score":0.4702,"best_fitness_score":0.2502,"best_task_score":0.28558},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":272.0,"contact_point_centroid":[0.53674,0.00972,0.04888],"force_p95":145.3565,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.49547,"mean_force":86.63401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52849,0.00355,0.05081]},{"body_a":"world","body_b":"push_box","contact_count":1663.0,"contact_point_centroid":[0.53173,-0.00634,-0.00016],"force_p95":68.33757,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.64995,"mean_force":14.49507,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51384,-0.05882,0.03662]},{"body_a":"world","body_b":"push_box","contact_count":904.0,"contact_point_centroid":[0.5366,0.03695,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51312,0.01458,0.24686]},{"body_a":"world","body_b":"push_box","contact_count":2864.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5287,0.03325,0.11972]}],"total_contact_groups":4},"final_pose_error":0.0136,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52968,-0.01718,0.02499],"final_tcp_position":[0.49796,-0.13696,0.02171],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.52803,0.03041,0.19142],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2864.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.53191,0.03617,0.05414],"tcp_start":[0.52803,0.03041,0.19142],"tcp_to_object_dist_end":0.02954,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.52968,-0.01718,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1361,"object_to_goal_dist_start":0.1905,"object_z_max":0.03497,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1935.0,"raw_peak_contact_force":150.49547,"subtask_id":"push_progress","tcp_end":[0.49796,-0.13696,0.02171],"tcp_start":[0.53191,0.03617,0.05414],"tcp_to_object_dist_end":0.12395,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```