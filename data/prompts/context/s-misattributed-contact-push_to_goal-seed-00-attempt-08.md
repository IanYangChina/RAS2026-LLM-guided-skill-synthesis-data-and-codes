## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1453 | 0.51 | ❌ rejected |
| 7 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3607 | 0.83 | ✅ accepted |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2398 | 0.81 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1205 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0128 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.51 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.830, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.145) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_push_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_object
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
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: pre_push_approach
- id: push_object_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
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
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_contact_ok
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal
- id: retract_from_object
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=reduce_speed
- **push_object_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_contact_ok, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **retract_from_object** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.145
- **task_score** (E): 0.514
- **fitness_score**: 0.525  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_object | 1.00 | 1.00 | 0.2527 |
| push_object_to_goal | 0.67 | 1.00 | 0.1767 |
| retract_from_object | 1.00 | 1.00 | 0.0751 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.022, 0.053) | (0.496, 0.001, 0.025)→(0.498, 0.001, 0.025) | 0.152→0.153 | 1.00 / 3.333 | 1.536 | 174.362 |
| push_object_to_goal | push | 0.67 / step_budget | (0.500, 0.022, 0.053)→(0.495, -0.149, 0.027) | (0.498, 0.001, 0.025)→(0.506, -0.069, 0.028) | 0.153→0.082 | 1.00 / 4.000 | 0.245 | 16.420 |
| retract_from_object | retract | 1.00 / step_budget | (0.495, -0.149, 0.027)→(0.492, -0.149, 0.102) | (0.506, -0.069, 0.028)→(0.510, -0.073, 0.025) | 0.082→0.079 | 1.00 / 4.000 | 76.654 | 80.784 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.812
- lateral_force_integral: None
- approach_alignment: 0.806
- goal_progress: 0.665
- terminal_score: 0.665
- phase_score: 0.604
- phase_breakdown.pre_push_approach_score: 0.602
- phase_breakdown.push_to_goal_score: 0.605

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.629
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.665
- **Median Q (composite search score)**: 0.184
- **K-run variance**: 0.0108
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.331


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05702,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.03038,"approach_behind_object.approach_tolerance":0.01321,"push_object_to_goal.push_distance":0.20101,"push_object_to_goal.push_speed":0.05296,"push_object_to_goal.push_tolerance":0.03057,"retract_from_object.retract_speed":0.14409,"retract_from_object.retract_tolerance":0.03271},"optimized_scores":{"best_composite_score":0.18417,"best_fitness_score":0.56417,"best_task_score":0.57025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":178.0,"contact_point_centroid":[0.53603,-0.00359,0.04501],"force_p95":240.81078,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":241.86217,"mean_force":219.10347,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.52501,-0.00133,0.04731]},{"body_a":"world","body_b":"push_box","contact_count":3320.0,"contact_point_centroid":[0.51802,-0.02646,-0.00012],"force_p95":115.57009,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":227.35157,"mean_force":12.086,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.50883,-0.00127,0.15693]},{"body_a":"attachment","body_b":"push_box","contact_count":337.0,"contact_point_centroid":[0.54064,-0.04853,0.04619],"force_p95":198.06468,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.31699,"mean_force":168.98514,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.53057,-0.05192,0.04812]},{"body_a":"world","body_b":"push_box","contact_count":1055.0,"contact_point_centroid":[0.52024,-0.06932,-0.00065],"force_p95":182.77495,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.19787,"mean_force":54.56581,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.51933,-0.09108,0.04096]},{"body_a":"world","body_b":"push_box","contact_count":500.0,"contact_point_centroid":[0.5062,-0.0973,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24519,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.48739,-0.1952,0.05419]}],"total_contact_groups":5},"final_pose_error":0.03246,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5062,-0.0973,0.02499],"final_tcp_position":[0.48751,-0.19451,0.09074],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":241.86217,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.52091,-0.02716,0.02465],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.1246,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24487,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1392.0,"raw_peak_contact_force":200.31699,"subtask_id":"pre_push_approach","tcp_end":[0.53348,-0.00099,0.04522],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,-0.0973,0.02497],"object_pos_start":[0.52091,-0.02716,0.02465],"object_to_goal_dist_end":0.05307,"object_to_goal_dist_start":0.1246,"object_z_max":0.03486,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":500.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49036,-0.19527,0.02307],"tcp_start":[0.53348,-0.00099,0.04522],"tcp_to_object_dist_end":0.09926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":600.0,"object_pos_end":[0.5062,-0.0973,0.02499],"object_pos_start":[0.5062,-0.0973,0.02497],"object_to_goal_dist_end":0.05306,"object_to_goal_dist_start":0.05307,"object_z_max":0.02499,"peak_contact_force":229.47226,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3498.0,"raw_peak_contact_force":241.86217,"tcp_end":[0.48751,-0.19451,0.09074],"tcp_start":[0.49036,-0.19527,0.02307],"tcp_to_object_dist_end":0.11884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75796,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.07298,"approach_behind_object.approach_tolerance":0.03356,"push_object_to_goal.push_distance":0.2443,"push_object_to_goal.push_speed":0.06269,"push_object_to_goal.push_tolerance":0.01011,"retract_from_object.retract_speed":0.09813,"retract_from_object.retract_tolerance":0.01843},"optimized_scores":{"best_composite_score":0.00316,"best_fitness_score":0.38316,"best_task_score":0.30706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":677.0,"contact_point_centroid":[0.50958,0.02942,0.04801],"force_p95":117.17517,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.17942,"mean_force":81.29478,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49996,0.02596,0.05136]},{"body_a":"world","body_b":"push_box","contact_count":2780.0,"contact_point_centroid":[0.50264,0.01531,-0.00021],"force_p95":79.24329,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.05334,"mean_force":20.14915,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49793,-0.00678,0.04519]},{"body_a":"world","body_b":"push_box","contact_count":1336.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.49918,0.03293,0.18117]},{"body_a":"world","body_b":"push_box","contact_count":1124.0,"contact_point_centroid":[0.49946,-0.0086,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49207,-0.08917,0.07214]}],"total_contact_groups":4},"final_pose_error":0.01837,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49946,-0.0086,0.02499],"final_tcp_position":[0.49188,-0.08904,0.11403],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":121.17942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3457.0,"raw_peak_contact_force":121.17942,"subtask_id":"pre_push_approach","tcp_end":[0.49888,0.06834,0.05612],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49946,-0.0086,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.1414,"object_to_goal_dist_start":0.20406,"object_z_max":0.03536,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49522,-0.08948,0.03209],"tcp_start":[0.49888,0.06834,0.05612],"tcp_to_object_dist_end":0.08131,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":660.0,"object_pos_end":[0.49946,-0.0086,0.02499],"object_pos_start":[0.49946,-0.0086,0.02499],"object_to_goal_dist_end":0.1414,"object_to_goal_dist_start":0.1414,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49188,-0.08904,0.11403],"tcp_start":[0.49522,-0.08948,0.03209],"tcp_to_object_dist_end":0.12024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3432,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.13701,"approach_behind_object.approach_tolerance":0.03159,"push_object_to_goal.push_distance":0.16687,"push_object_to_goal.push_speed":0.03872,"push_object_to_goal.push_tolerance":0.0244,"retract_from_object.retract_speed":0.08569,"retract_from_object.retract_tolerance":0.02501},"optimized_scores":{"best_composite_score":0.24871,"best_fitness_score":0.62871,"best_task_score":0.66504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":827.0,"contact_point_centroid":[0.48666,-0.05209,-0.0006],"force_p95":193.71805,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":201.59005,"mean_force":66.35033,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.48176,-0.04839,0.04906]},{"body_a":"attachment","body_b":"push_box","contact_count":341.0,"contact_point_centroid":[0.49292,-0.04524,0.04693],"force_p95":196.36787,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.41856,"mean_force":156.71847,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.48355,-0.04849,0.0507]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.51381,-0.13401,0.06489],"force_p95":43.52759,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.76851,"mean_force":16.99719,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.50065,-0.16419,0.02462]},{"body_a":"world","body_b":"push_box","contact_count":555.0,"contact_point_centroid":[0.52504,-0.11418,-0.00025],"force_p95":0.97416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.60181,"mean_force":0.5044,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49774,-0.16317,0.06952]},{"body_a":"push_box","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.513,-0.10604,0.07054],"force_p95":26.54908,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.65175,"mean_force":12.43254,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49715,-0.13665,0.0322]},{"body_a":"world","body_b":"push_box","contact_count":1300.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.48407,5e-05,0.18033]}],"total_contact_groups":6},"final_pose_error":0.02482,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52453,-0.11441,0.02499],"final_tcp_position":[0.49761,-0.1629,0.10008],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":201.59005,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":4.11796,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":201.59005,"subtask_id":"pre_push_approach","tcp_end":[0.46782,0.0001,0.05638],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.51306,-0.10193,0.03552],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.05091,"object_to_goal_dist_start":0.12903,"object_z_max":0.04279,"peak_contact_force":0.24524,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":560.0,"raw_peak_contact_force":48.76851,"subtask_id":"push_to_goal","tcp_end":[0.50089,-0.16371,0.02467],"tcp_start":[0.46782,0.0001,0.05638],"tcp_to_object_dist_end":0.0639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":750.0,"object_pos_end":[0.52453,-0.11441,0.02499],"object_pos_start":[0.51306,-0.10193,0.03552],"object_to_goal_dist_end":0.04322,"object_to_goal_dist_start":0.05091,"object_z_max":0.03552,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49761,-0.1629,0.10008],"tcp_start":[0.50089,-0.16371,0.02467],"tcp_to_object_dist_end":0.09335,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```