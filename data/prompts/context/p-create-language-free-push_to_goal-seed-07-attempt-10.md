## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.0675 | 0.29 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0023 | 0.34 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2636 | 0.41 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3769 | 0.42 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3774 | 0.42 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
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

## Current Skill (Q=0.068) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object_side
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_side
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
    - 0.025
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_object_side
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_side
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: abort
  subtask_id: reach_object_side
- id: push_to_goal
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
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
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
  guards:
  - id: maintain_contact
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
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
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_side** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_side, when=after_phase, predicate=contact_detected, on_failure=abort, threshold=1.0
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=maintain_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.068
- **task_score** (E): 0.292
- **fitness_score**: 0.278  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_side | 1.00 | 1.00 | 0.1835 |
| descend_to_contact | 1.00 | 1.00 | 0.0895 |
| push_to_goal | 1.00 | 1.00 | 0.1709 |
| retract_1 | 1.00 | 1.00 | 0.0992 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.054, 0.132) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.509, 0.054, 0.132)→(0.524, 0.055, 0.044) | (0.513, 0.027, 0.025)→(0.517, 0.028, 0.024) | 0.180→0.182 | 1.00 / 4.000 | 242.795 | 245.707 |
| push_to_goal | push | 1.00 / step_budget | (0.524, 0.055, 0.044)→(0.498, -0.111, 0.023) | (0.517, 0.028, 0.024)→(0.525, -0.023, 0.025) | 0.182→0.131 | 1.00 / 4.000 | 0.245 | 175.448 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.111, 0.023)→(0.497, -0.147, 0.114) | (0.525, -0.023, 0.025)→(0.525, -0.023, 0.025) | 0.131→0.131 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.415
- lateral_force_integral: None
- approach_alignment: 0.794
- goal_progress: 0.411
- terminal_score: 0.411
- phase_score: 0.355
- phase_breakdown.push_to_goal_score: 0.423
- phase_breakdown.reach_object_side_score: 0.197

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.378
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.411
- **Median Q (composite search score)**: 0.095
- **K-run variance**: 0.0090
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.532


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90698,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_y_offset":0.03968,"push_to_goal.push_lateral_offset":0.00789,"push_to_goal.push_speed":0.09954},"optimized_scores":{"best_composite_score":0.09515,"best_fitness_score":0.30515,"best_task_score":0.32704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.52825,0.07203,0.04666],"force_p95":243.75683,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.10493,"mean_force":174.85342,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51715,0.07574,0.04727]},{"body_a":"world","body_b":"push_box","contact_count":2057.0,"contact_point_centroid":[0.51718,0.0494,-0.00012],"force_p95":116.9867,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":219.1239,"mean_force":13.51891,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51093,0.07733,0.08078]},{"body_a":"attachment","body_b":"push_box","contact_count":688.0,"contact_point_centroid":[0.53567,0.02668,0.04627],"force_p95":174.4822,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":178.56435,"mean_force":141.37956,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5259,0.02294,0.04576]},{"body_a":"world","body_b":"push_box","contact_count":3028.0,"contact_point_centroid":[0.51583,0.01167,-0.00036],"force_p95":143.87893,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.59641,"mean_force":32.62966,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51789,-0.01187,0.03856]},{"body_a":"world","body_b":"push_box","contact_count":2512.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.50453,0.04009,0.21502]},{"body_a":"world","body_b":"push_box","contact_count":2648.0,"contact_point_centroid":[0.50647,-0.01675,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49649,-0.12671,0.06574]}],"total_contact_groups":6},"final_pose_error":0.01192,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50647,-0.01675,0.02499],"final_tcp_position":[0.49667,-0.14671,0.11404],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":244.10493,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2512.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object_side","tcp_end":[0.51085,0.08116,0.13138],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":690.0,"object_pos_end":[0.51944,0.04876,0.02432],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19971,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":240.89998,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":244.10493,"subtask_id":"reach_object_side","tcp_end":[0.52573,0.07653,0.04377],"tcp_start":[0.51085,0.08116,0.13138],"tcp_to_object_dist_end":0.03448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,-0.01675,0.02499],"object_pos_start":[0.51944,0.04876,0.02432],"object_to_goal_dist_end":0.1334,"object_to_goal_dist_start":0.19971,"object_z_max":0.03532,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3716.0,"raw_peak_contact_force":178.56435,"subtask_id":"push_to_goal","tcp_end":[0.49995,-0.10788,0.02299],"tcp_start":[0.52573,0.07653,0.04377],"tcp_to_object_dist_end":0.09139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.50647,-0.01675,0.02499],"object_pos_start":[0.50647,-0.01675,0.02499],"object_to_goal_dist_end":0.1334,"object_to_goal_dist_start":0.1334,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2648.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49667,-0.14671,0.11404],"tcp_start":[0.49995,-0.10788,0.02299],"tcp_to_object_dist_end":0.15785,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90698,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_y_offset":0.03277,"push_to_goal.push_lateral_offset":0.01871,"push_to_goal.push_speed":0.09989},"optimized_scores":{"best_composite_score":-0.06021,"best_fitness_score":0.14979,"best_task_score":0.13808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":150.0,"contact_point_centroid":[0.4932,0.08134,0.04652],"force_p95":256.0056,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":256.05627,"mean_force":186.28027,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48216,0.08497,0.04701]},{"body_a":"world","body_b":"push_box","contact_count":2106.0,"contact_point_centroid":[0.48131,0.06019,-0.00013],"force_p95":117.92836,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.72868,"mean_force":13.59945,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47666,0.08401,0.08179]},{"body_a":"attachment","body_b":"push_box","contact_count":641.0,"contact_point_centroid":[0.50703,0.04391,0.04658],"force_p95":170.22786,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.25662,"mean_force":153.54904,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50085,0.03715,0.04586]},{"body_a":"world","body_b":"push_box","contact_count":2479.0,"contact_point_centroid":[0.52101,0.03372,-0.00044],"force_p95":151.81371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.56317,"mean_force":40.22829,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49706,-0.01355,0.03591]},{"body_a":"world","body_b":"push_box","contact_count":2464.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.48808,0.04172,0.2156]},{"body_a":"world","body_b":"push_box","contact_count":2768.0,"contact_point_centroid":[0.53592,0.02697,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49363,-0.11955,0.06614]}],"total_contact_groups":6},"final_pose_error":0.01195,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53592,0.02697,0.02499],"final_tcp_position":[0.49637,-0.14606,0.11431],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":256.05627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2464.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object_side","tcp_end":[0.4776,0.08463,0.13226],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":690.0,"object_pos_end":[0.48367,0.06006,0.0243],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.21069,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":255.46867,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2256.0,"raw_peak_contact_force":256.05627,"subtask_id":"reach_object_side","tcp_end":[0.49089,0.08673,0.04333],"tcp_start":[0.4776,0.08463,0.13226],"tcp_to_object_dist_end":0.03356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53592,0.02697,0.02499],"object_pos_start":[0.48367,0.06006,0.0243],"object_to_goal_dist_end":0.18058,"object_to_goal_dist_start":0.21069,"object_z_max":0.03449,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3120.0,"raw_peak_contact_force":174.25662,"subtask_id":"push_to_goal","tcp_end":[0.49455,-0.09431,0.02333],"tcp_start":[0.49089,0.08673,0.04333],"tcp_to_object_dist_end":0.12815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.53592,0.02697,0.02499],"object_pos_start":[0.53592,0.02697,0.02499],"object_to_goal_dist_end":0.18058,"object_to_goal_dist_start":0.18058,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49637,-0.14606,0.11431],"tcp_start":[0.49455,-0.09431,0.02333],"tcp_to_object_dist_end":0.1987,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89655,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_y_offset":0.02228,"push_to_goal.push_lateral_offset":0.01098,"push_to_goal.push_speed":0.09999},"optimized_scores":{"best_composite_score":0.16758,"best_fitness_score":0.37758,"best_task_score":0.41129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":157.0,"contact_point_centroid":[0.55745,-0.00342,0.04687],"force_p95":236.43235,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":236.96106,"mean_force":171.23444,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54613,-0.0004,0.04756]},{"body_a":"world","body_b":"push_box","contact_count":2078.0,"contact_point_centroid":[0.54667,-0.02381,-0.00012],"force_p95":111.31576,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":206.01424,"mean_force":13.2664,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53893,-0.00187,0.08079]},{"body_a":"attachment","body_b":"push_box","contact_count":640.0,"contact_point_centroid":[0.55545,-0.04195,0.04684],"force_p95":169.08701,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.52241,"mean_force":143.92977,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54572,-0.04589,0.04623]},{"body_a":"world","body_b":"push_box","contact_count":2300.0,"contact_point_centroid":[0.54485,-0.04691,-0.00043],"force_p95":108.74182,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.98301,"mean_force":40.50839,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54005,-0.05301,0.04275]},{"body_a":"world","body_b":"push_box","contact_count":2272.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.51781,-0.00153,0.21606]},{"body_a":"world","body_b":"push_box","contact_count":2528.0,"contact_point_centroid":[0.53166,-0.07896,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49644,-0.13828,0.0648]}],"total_contact_groups":6},"final_pose_error":0.01198,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53166,-0.07896,0.02499],"final_tcp_position":[0.49666,-0.14792,0.11369],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":236.96106,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object_side","tcp_end":[0.53789,-0.00311,0.13228],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":690.0,"object_pos_end":[0.54909,-0.02445,0.02429],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.1348,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":232.01522,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2235.0,"raw_peak_contact_force":236.96106,"subtask_id":"reach_object_side","tcp_end":[0.55493,0.00039,0.04434],"tcp_start":[0.53789,-0.00311,0.13228],"tcp_to_object_dist_end":0.03246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":779.0,"n_steps_budget":960.0,"object_pos_end":[0.53166,-0.07896,0.02499],"object_pos_start":[0.54909,-0.02445,0.02429],"object_to_goal_dist_end":0.07777,"object_to_goal_dist_start":0.1348,"object_z_max":0.03575,"peak_contact_force":0.24526,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2940.0,"raw_peak_contact_force":173.52241,"subtask_id":"push_to_goal","tcp_end":[0.49985,-0.12963,0.02157],"tcp_start":[0.55493,0.00039,0.04434],"tcp_to_object_dist_end":0.05993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.53166,-0.07896,0.02499],"object_pos_start":[0.53166,-0.07896,0.02499],"object_to_goal_dist_end":0.07778,"object_to_goal_dist_start":0.07777,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2528.0,"raw_peak_contact_force":0.24526,"tcp_end":[0.49666,-0.14792,0.11369],"tcp_start":[0.49985,-0.12963,0.02157],"tcp_to_object_dist_end":0.11768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```