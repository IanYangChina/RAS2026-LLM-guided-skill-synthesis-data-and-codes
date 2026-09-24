## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1741 | 0.44 | ✅ accepted |
| 4 | approach → push → retract | arc_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1091 | 0.01 | ✅ accepted |
| 3 | approach → push → retract | arc_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1586 | 0.00 | ✅ accepted |
| 2 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ❌ rejected |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.4792366731926673, 0.05847322120055107, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.4792366731926673, 0.05847322120055107, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.174) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: backend_approach
  anchor: object
  offset:
  - 0.0
  - -0.08
  - 0.0
  weight: 0.2
- id: establish_contact
  anchor: object
  metric: contact
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_behind
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - -0.08
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: backend_approach
- id: make_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: probe_contact
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: establish_contact
- id: push_to_goal
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
      distance: 0.25
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 22.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - -0.005
    - 0.0
  subtask_id: push_to_goal
- id: retract_away
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, -0.08, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **make_contact** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=replace_offset_projection, sign=negative}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=probe_contact, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=22.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, -0.005, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.174
- **task_score** (E): 0.442
- **fitness_score**: 0.390  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.194
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2884 |
| make_contact | 0.67 | 1.00 | 0.0306 |
| push_to_goal | 0.33 | 1.00 | 0.0855 |
| retract_away | 1.00 | 1.00 | 0.1015 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.527, -0.061, 0.024) | (0.526, -0.001, 0.025)→(0.530, -0.074, 0.030) | 0.156→0.102 | 1.00 / 2.000 | 15.419 | 138.720 |
| make_contact | contact | 0.67 / force_exceeded | (0.527, -0.061, 0.024)→(0.554, -0.052, 0.021) | (0.530, -0.074, 0.030)→(0.528, -0.076, 0.029) | 0.102→0.100 | 1.00 / 3.000 | 29.427 | 17.571 |
| push_to_goal | push | 0.33 / guard_failure | (0.554, -0.052, 0.021)→(0.538, -0.118, 0.014) | (0.528, -0.076, 0.029)→(0.528, -0.083, 0.026) | 0.100→0.094 | 1.00 / 2.667 | 7.758 | 30.210 |
| retract_away | retract | 1.00 / step_budget | (0.501, -0.191, 0.020)→(0.497, -0.150, 0.113) | (0.479, 0.020, 0.025)→(0.479, 0.020, 0.025) | 0.171→0.171 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.770
- lateral_force_integral: None
- approach_alignment: 0.611
- goal_progress: 0.528
- terminal_score: 0.528
- phase_score: 0.353
- phase_breakdown.establish_contact_score: 1.000
- phase_breakdown.backend_approach_score: 0.634
- phase_breakdown.push_to_goal_score: 0.043

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.442
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.617
- **Median Q (composite search score)**: 0.144
- **K-run variance**: 0.0169
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.337


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.05038,"approach_behind.arc_height":0.1005,"make_contact.contact_force_threshold":15.14124,"make_contact.contact_speed":0.05572,"push_to_goal.push_distance":0.21677,"push_to_goal.push_speed":0.06589,"retract_away.retract_height":0.1072},"optimized_scores":{"best_composite_score":0.144,"best_fitness_score":0.304,"best_task_score":0.18158},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":114.0,"contact_point_centroid":[0.48899,0.0255,0.04543],"force_p95":205.86992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":216.98795,"mean_force":154.65993,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48329,0.01673,0.04517]},{"body_a":"world","body_b":"push_box","contact_count":2674.0,"contact_point_centroid":[0.47932,0.05643,-6e-05],"force_p95":49.05263,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.29365,"mean_force":6.87119,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48869,0.05681,0.17207]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.48542,0.00444,0.03597],"force_p95":19.52077,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.1356,"mean_force":4.47502,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.48409,-0.00708,0.0359]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.48253,0.00735,0.0338],"force_p95":16.98673,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.35693,"mean_force":4.42021,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48197,-0.00453,0.03385]},{"body_a":"world","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.47553,0.04377,-0.00018],"force_p95":8.52952,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.18406,"mean_force":1.70382,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.4829,-0.00569,0.03479]},{"body_a":"world","body_b":"push_box","contact_count":1166.0,"contact_point_centroid":[0.47869,0.02125,-0.0001],"force_p95":0.49505,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.96186,"mean_force":0.31836,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49142,-0.10609,0.02494]},{"body_a":"world","body_b":"push_box","contact_count":1244.0,"contact_point_centroid":[0.47875,0.02014,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49754,-0.16467,0.06317]}],"total_contact_groups":7},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47875,0.02014,0.02499],"final_tcp_position":[0.49702,-0.14998,0.11267],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":216.98795,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.48072,0.03499,0.03489],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.18626,"object_to_goal_dist_start":0.2095,"object_z_max":0.0348,"peak_contact_force":42.30495,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2788.0,"raw_peak_contact_force":216.98795,"subtask_id":"backend_approach","tcp_end":[0.48477,-0.00642,0.0366],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.47807,0.03593,0.03378],"object_pos_start":[0.48072,0.03499,0.03489],"object_to_goal_dist_end":0.18743,"object_to_goal_dist_start":0.18626,"object_z_max":0.03552,"peak_contact_force":65.57998,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":62.0,"raw_peak_contact_force":28.1356,"subtask_id":"establish_contact","tcp_end":[0.48211,-0.00445,0.03411],"tcp_start":[0.48477,-0.00642,0.0366],"tcp_to_object_dist_end":0.04059,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.47875,0.02014,0.02499],"object_pos_start":[0.47807,0.03593,0.03378],"object_to_goal_dist_end":0.17146,"object_to_goal_dist_start":0.18743,"object_z_max":0.03383,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1175.0,"raw_peak_contact_force":19.35693,"subtask_id":"push_to_goal","tcp_end":[0.50111,-0.1909,0.01992],"tcp_start":[0.48211,-0.00445,0.03411],"tcp_to_object_dist_end":0.21228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":750.0,"object_pos_end":[0.47875,0.02014,0.02499],"object_pos_start":[0.47875,0.02014,0.02499],"object_to_goal_dist_end":0.17146,"object_to_goal_dist_start":0.17146,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49702,-0.14998,0.11267],"tcp_start":[0.50111,-0.1909,0.01992],"tcp_to_object_dist_end":0.19226,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18367,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.18662,"approach_behind.arc_height":0.14935,"make_contact.contact_force_threshold":11.60813,"make_contact.contact_speed":0.04639,"push_to_goal.push_distance":0.32989,"push_to_goal.push_speed":0.02465,"retract_away.retract_height":0.09479},"optimized_scores":{"best_composite_score":0.34624,"best_fitness_score":0.42291,"best_task_score":0.52817},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2630.0,"contact_point_centroid":[0.54648,-0.03014,-2e-05],"force_p95":31.97137,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.71348,"mean_force":3.8237,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52085,0.0522,0.152]},{"body_a":"attachment","body_b":"push_box","contact_count":173.0,"contact_point_centroid":[0.55319,-0.04925,0.04939],"force_p95":72.49827,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.90779,"mean_force":33.01846,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54308,-0.03888,0.01748]},{"body_a":"push_box","body_b":"link7","contact_count":135.0,"contact_point_centroid":[0.57251,-0.06876,0.05148],"force_p95":73.71195,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.19248,"mean_force":37.3705,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54391,-0.0512,0.01574]},{"body_a":"world","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.59117,-0.12044,-0.0001],"force_p95":22.45453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.45453,"mean_force":22.45453,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.54389,-0.08446,0.01866]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.57355,-0.10426,0.05281],"force_p95":21.9438,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.27371,"mean_force":10.58911,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54247,-0.08491,0.01793]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.55881,-0.09208,0.05589],"force_p95":17.53519,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.69476,"mean_force":4.73376,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.5439,-0.08412,0.01873]},{"body_a":"world","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.58857,-0.12515,-0.00018],"force_p95":13.12885,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.71712,"mean_force":3.88983,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54289,-0.08481,0.0181]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.55906,-0.09302,0.05538],"force_p95":14.18759,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.10023,"mean_force":4.37656,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54345,-0.08468,0.01827]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.57566,-0.10164,0.05357],"force_p95":1.2013,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.24312,"mean_force":0.82739,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.54391,-0.08393,0.01876]}],"total_contact_groups":9},"final_pose_error":0.32671,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55766,-0.12641,0.02699],"final_tcp_position":[0.54083,-0.08534,0.01755],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":102.71348,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":801.0,"n_steps_budget":990.0,"object_pos_end":[0.55864,-0.11974,0.02824],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.06607,"object_to_goal_dist_start":0.13211,"object_z_max":0.03027,"peak_contact_force":1.43731,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2938.0,"raw_peak_contact_force":102.71348,"subtask_id":"backend_approach","tcp_end":[0.5439,-0.08366,0.01875],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.5587,-0.12192,0.02837],"object_pos_start":[0.55864,-0.11974,0.02824],"object_to_goal_dist_end":0.06516,"object_to_goal_dist_start":0.06607,"object_z_max":0.02841,"peak_contact_force":22.45453,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":22.45453,"subtask_id":"establish_contact","tcp_end":[0.54391,-0.08452,0.01859],"tcp_start":[0.5439,-0.08366,0.01875],"tcp_to_object_dist_end":0.04139,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.55766,-0.12641,0.02699],"object_pos_start":[0.5587,-0.12192,0.02837],"object_to_goal_dist_end":0.06233,"object_to_goal_dist_start":0.06516,"object_z_max":0.02837,"peak_contact_force":22.27371,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":29.0,"raw_peak_contact_force":22.27371,"subtask_id":"push_to_goal","tcp_end":[0.54083,-0.08534,0.01755],"tcp_start":[0.54391,-0.08452,0.01859],"tcp_to_object_dist_end":0.04538,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55472,-0.03508,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79412,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.21155,"approach_behind.arc_height":0.1498,"make_contact.contact_force_threshold":10.4372,"make_contact.contact_speed":0.0559,"push_to_goal.push_distance":0.32588,"push_to_goal.push_speed":0.024,"retract_away.retract_height":0.08092},"optimized_scores":{"best_composite_score":0.03203,"best_fitness_score":0.44203,"best_task_score":0.61671},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2512.0,"contact_point_centroid":[0.55549,-0.03886,-2e-05],"force_p95":2.09156,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.45831,"mean_force":2.42893,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52629,0.04993,0.15153]},{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.56214,-0.05724,0.04621],"force_p95":71.29944,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.57097,"mean_force":24.8947,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.55332,-0.04623,0.0158]},{"body_a":"push_box","body_b":"link7","contact_count":106.0,"contact_point_centroid":[0.57427,-0.07573,0.05124],"force_p95":65.0432,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.07966,"mean_force":24.01767,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.55405,-0.0541,0.01404]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56226,-0.10912,0.04989],"force_p95":48.99891,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.99891,"mean_force":48.99891,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.57299,-0.07905,0.00492]},{"body_a":"world","body_b":"push_box","contact_count":412.0,"contact_point_centroid":[0.54812,-0.14149,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.82474,"mean_force":0.36371,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.60659,-0.07306,0.00687]},{"body_a":"world","body_b":"push_box","contact_count":3950.0,"contact_point_centroid":[0.54812,-0.14148,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12299,"mean_force":0.24938,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.59249,-0.08055,0.01134]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.56254,-0.10559,0.05112],"force_p95":0.35353,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44558,"mean_force":0.12383,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.55308,-0.0939,0.01669]}],"total_contact_groups":7},"final_pose_error":0.2611,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54804,-0.14151,0.02504],"final_tcp_position":[0.57236,-0.07916,0.00494],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":96.45831,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":766.0,"n_steps_budget":900.0,"object_pos_end":[0.55038,-0.13627,0.02613],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.05223,"object_to_goal_dist_start":0.12728,"object_z_max":0.02834,"peak_contact_force":2.51621,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2765.0,"raw_peak_contact_force":96.45831,"subtask_id":"backend_approach","tcp_end":[0.55315,-0.09291,0.01684],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54812,-0.14149,0.02499],"object_pos_start":[0.55038,-0.13627,0.02613],"object_to_goal_dist_end":0.04887,"object_to_goal_dist_start":0.05223,"object_z_max":0.02617,"peak_contact_force":0.24525,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3957.0,"raw_peak_contact_force":2.12299,"subtask_id":"establish_contact","tcp_end":[0.63635,-0.0685,0.0111],"tcp_start":[0.55315,-0.09291,0.01684],"tcp_to_object_dist_end":0.11535,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.54804,-0.14151,0.02504],"object_pos_start":[0.54812,-0.14149,0.02499],"object_to_goal_dist_end":0.04879,"object_to_goal_dist_start":0.04887,"object_z_max":0.02499,"peak_contact_force":0.75512,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":413.0,"raw_peak_contact_force":48.99891,"subtask_id":"push_to_goal","tcp_end":[0.57236,-0.07916,0.00494],"tcp_start":[0.63635,-0.0685,0.0111],"tcp_to_object_dist_end":0.06988,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```