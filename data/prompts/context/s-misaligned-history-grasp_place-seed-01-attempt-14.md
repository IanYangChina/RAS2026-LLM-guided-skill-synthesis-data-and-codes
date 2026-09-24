## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.1125 | 0.41 | ❌ rejected |
| 13 | approach → align → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7  | -0.0337 | 0.27 | ❌ rejected |
| 12 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0818 | 0.17 | ❌ rejected |
| 11 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.3114 | 0.18 | ❌ rejected |
| 10 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12  | -0.1335 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=-0.134) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: align_grasp
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: close
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_dropped_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_goal
- id: descend_place
  type: descend
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
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
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_grasp** (`align`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_dropped_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.134
- **task_score** (E): 0.281
- **fitness_score**: 0.436  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0824 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 1.00 | 1.00 | 0.0637 |
| approach_goal | 0.00 | 1.00 | 0.0001 |
| descend_place | 0.33 | 1.00 | 0.1454 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.480, -0.002, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.480, -0.002, 0.057)→(0.473, -0.002, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.279 | 1.00 / 40.000 | 0.157 | 0.187 |
| lift | lift | 1.00 / step_budget | (0.473, -0.002, 0.049)→(0.469, -0.002, 0.113) | (0.479, -0.001, 0.025)→(0.470, -0.001, 0.082) | 0.279→0.267 | 1.00 / 23.333 | 0.108 | 0.369 |
| approach_goal | approach | 0.00 / guard_failure | (0.502, 0.077, 0.187)→(0.502, 0.077, 0.187) | (0.470, -0.001, 0.082)→(0.515, 0.090, 0.023) | 0.267→0.216 | 1.00 / 12.667 | 0.120 | 1.309 |
| descend_place | descend | 0.33 / step_budget | (0.502, 0.077, 0.187)→(0.560, 0.153, 0.111) | (0.515, 0.090, 0.023)→(0.530, 0.114, 0.016) | 0.216→0.198 | 1.00 / 8.000 | 0.123 | 0.321 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.221
- phase_score: 0.187
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.622
- grasp_place_fitness: 0.572

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.572
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.417
- **Median Q (composite search score)**: -0.147
- **K-run variance**: 0.0111
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.346


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54894,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00668,"align_grasp.lateral_offset_y":0.00183,"approach_goal.arc_height":0.08978,"approach_goal.transport_speed":0.06772,"approach_object.approach_speed":0.06095,"descend_place.descend_speed":0.07295,"descend_place.place_z_offset":-0.02179,"lift.lift_height":0.13334,"lift.lift_speed":0.04028},"optimized_scores":{"best_composite_score":-0.14655,"best_fitness_score":0.42345,"best_task_score":0.41745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.56125,0.25255,-0.00278],"force_p95":0.36822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03967,"mean_force":0.16289,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54733,0.2096,0.25322]},{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.49642,0.04512,-0.00119],"force_p95":0.26619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37472,"mean_force":0.07486,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.493,0.04513,0.0494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":24612.0,"contact_point_centroid":[0.49257,0.06364,0.09278],"force_p95":0.09179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28548,"mean_force":0.05525,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49265,0.04486,0.09295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6415.0,"contact_point_centroid":[0.50126,0.05957,0.20463],"force_p95":0.15052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26202,"mean_force":0.10666,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50043,0.07788,0.20784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20539.0,"contact_point_centroid":[0.49167,0.02582,0.09208],"force_p95":0.10656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25151,"mean_force":0.06584,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49257,0.04486,0.09219]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7296.0,"contact_point_centroid":[0.50381,0.09927,0.20556],"force_p95":0.13521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2271,"mean_force":0.09568,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50168,0.08117,0.2095]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04511,-0.00203],"force_p95":0.13224,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14776,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49577,0.04541,0.04904]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49756,0.02008,0.219]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49836,0.04352,0.09449]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.5611,0.25283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55176,0.22346,0.19089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4131.0,"contact_point_centroid":[0.49558,0.06451,0.0489],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10321,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49463,0.0453,0.04777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.49473,0.02624,0.04901],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09289,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49463,0.0453,0.04777]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1495.0,"contact_point_centroid":[0.54778,0.20951,0.25508],"force_p95":0.01178,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54723,0.20948,0.25288]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1670.0,"contact_point_centroid":[0.55239,0.22345,0.19335],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55173,0.2234,0.19108]}],"total_contact_groups":14},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5611,0.25283,0.01602],"final_tcp_position":[0.55862,0.23934,0.13078],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":2.03967,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49725,0.04111,0.13825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50241,0.04603,0.05644],"tcp_start":[0.49725,0.04111,0.13825],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04534,0.02586],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24175,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13155,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10791.0,"raw_peak_contact_force":0.14776,"tcp_end":[0.4946,0.0453,0.04773],"tcp_start":[0.50241,0.04603,0.05644],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49054,0.04472,0.08898],"object_pos_start":[0.50109,0.04534,0.02586],"object_to_goal_dist_end":0.22103,"object_to_goal_dist_start":0.24175,"object_z_max":0.09724,"peak_contact_force":0.11363,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":45352.0,"raw_peak_contact_force":0.37472,"tcp_end":[0.49099,0.04456,0.11951],"tcp_start":[0.4946,0.0453,0.04773],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.5611,0.25283,0.01602],"object_pos_start":[0.49054,0.04472,0.08898],"object_to_goal_dist_end":0.13104,"object_to_goal_dist_start":0.22103,"object_z_max":0.23326,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16762.0,"raw_peak_contact_force":2.03967,"subtask_id":"place_goal","tcp_end":[0.54711,0.20937,0.25252],"tcp_start":[0.54713,0.20938,0.25257],"tcp_to_object_dist_end":0.24086,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.5611,0.25283,0.01602],"object_pos_start":[0.5611,0.25283,0.01602],"object_to_goal_dist_end":0.13104,"object_to_goal_dist_start":0.13104,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3230.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55862,0.23934,0.13078],"tcp_start":[0.54711,0.20937,0.25252],"tcp_to_object_dist_end":0.11557,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1745,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00399,"align_grasp.lateral_offset_y":-0.00056,"approach_goal.arc_height":0.19517,"approach_goal.transport_speed":0.14774,"approach_object.approach_speed":0.04201,"descend_place.descend_speed":0.11242,"descend_place.place_z_offset":-0.04063,"lift.lift_height":0.06161,"lift.lift_speed":0.05806},"optimized_scores":{"best_composite_score":-0.25576,"best_fitness_score":0.31424,"best_task_score":0.20493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":930.0,"contact_point_centroid":[0.50896,0.05049,-0.00238],"force_p95":0.46303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71881,"mean_force":0.15794,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52337,0.04946,0.09464]},{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.4734,-0.02005,-0.00117],"force_p95":0.24841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33117,"mean_force":0.05636,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46681,-0.02018,0.05097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7856.0,"contact_point_centroid":[0.48724,0.02979,0.07493],"force_p95":0.1269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30853,"mean_force":0.08414,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48721,0.01122,0.07852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11424.0,"contact_point_centroid":[0.46835,-0.00096,0.06892],"force_p95":0.10545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24625,"mean_force":0.06535,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46775,-0.01999,0.06936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13614.0,"contact_point_centroid":[0.46741,-0.03875,0.0692],"force_p95":0.09249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24323,"mean_force":0.05468,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46767,-0.01998,0.06937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8466.0,"contact_point_centroid":[0.48698,-0.00771,0.07438],"force_p95":0.11765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23345,"mean_force":0.0788,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48677,0.01073,0.07834]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02012,-0.00202],"force_p95":0.12811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14274,"mean_force":0.1246,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4689,-0.02026,0.05053]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48645,-0.00892,0.22004]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47339,-0.01937,0.09555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4514.0,"contact_point_centroid":[0.4631,-0.00106,0.06724],"force_p95":0.10516,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11603,"mean_force":0.08101,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46259,-0.01977,0.07014]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4977.0,"contact_point_centroid":[0.46231,-0.03828,0.06702],"force_p95":0.09724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0999,"mean_force":0.07406,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46259,-0.01977,0.07013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4132.0,"contact_point_centroid":[0.46872,-0.00102,0.05008],"force_p95":0.07547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09928,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4678,-0.02024,0.0494]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4860.0,"contact_point_centroid":[0.46788,-0.03929,0.05005],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08545,"mean_force":0.04446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4678,-0.02024,0.0494]},{"body_a":"left_finger","body_b":"right_finger","contact_count":607.0,"contact_point_centroid":[0.52677,0.05255,0.09843],"force_p95":0.01351,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01074,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52632,0.05255,0.09597]}],"total_contact_groups":14},"final_pose_error":0.15244,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50884,0.05322,0.01602],"final_tcp_position":[0.53062,0.05708,0.0979],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.71881,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47442,-0.01833,0.13947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47528,-0.02042,0.05714],"tcp_start":[0.47442,-0.01833,0.13947],"tcp_to_object_dist_end":0.03113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.02009,0.0259],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12809,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10792.0,"raw_peak_contact_force":0.14274,"tcp_end":[0.46777,-0.02023,0.04937],"tcp_start":[0.47528,-0.02042,0.05714],"tcp_to_object_dist_end":0.02489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":358.0,"n_steps_budget":600.0,"object_pos_end":[0.46881,-0.02012,0.04509],"object_pos_start":[0.47608,-0.02009,0.0259],"object_to_goal_dist_end":0.28213,"object_to_goal_dist_start":0.28846,"object_z_max":0.05329,"peak_contact_force":0.10541,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25232.0,"raw_peak_contact_force":0.33117,"tcp_end":[0.46651,-0.01987,0.07425],"tcp_start":[0.46777,-0.02023,0.04937],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.46266,-0.0197,0.03775],"object_pos_start":[0.46881,-0.02012,0.04509],"object_to_goal_dist_end":0.28925,"object_to_goal_dist_start":0.28213,"object_z_max":0.04509,"peak_contact_force":0.11603,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9491.0,"raw_peak_contact_force":0.11603,"subtask_id":"place_goal","tcp_end":[0.462,-0.01976,0.06951],"tcp_start":[0.46203,-0.01976,0.06955],"tcp_to_object_dist_end":0.03176,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50884,0.05322,0.01602],"object_pos_start":[0.46262,-0.0197,0.03765],"object_to_goal_dist_end":0.23776,"object_to_goal_dist_start":0.28933,"object_z_max":0.05247,"peak_contact_force":0.12264,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17859.0,"raw_peak_contact_force":0.71881,"subtask_id":"place_goal","tcp_end":[0.53062,0.05708,0.0979],"tcp_start":[0.462,-0.01976,0.06951],"tcp_to_object_dist_end":0.08482,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00997,"align_grasp.lateral_offset_y":-0.00578,"approach_goal.arc_height":0.0884,"approach_goal.transport_speed":0.07596,"approach_object.approach_speed":0.09727,"descend_place.descend_speed":0.11273,"descend_place.place_z_offset":-0.04964,"lift.lift_height":0.13465,"lift.lift_speed":0.09051},"optimized_scores":{"best_composite_score":0.00178,"best_fitness_score":0.57178,"best_task_score":0.22133},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1558.0,"contact_point_centroid":[0.52054,0.03632,-0.00274],"force_p95":0.33128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77166,"mean_force":0.15319,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49835,0.0408,0.23886]},{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.45594,-0.03227,-0.00152],"force_p95":0.22491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40197,"mean_force":0.0526,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45449,-0.03085,0.0525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12693.0,"contact_point_centroid":[0.45103,-0.04876,0.11215],"force_p95":0.11656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32422,"mean_force":0.08161,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45256,-0.02984,0.11461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18042.0,"contact_point_centroid":[0.45237,-0.01141,0.10902],"force_p95":0.09573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29041,"mean_force":0.0599,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45272,-0.02992,0.10992]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02659,-0.00236],"force_p95":0.22121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27063,"mean_force":0.14749,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4572,-0.03103,0.05105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2702.0,"contact_point_centroid":[0.46567,0.00918,0.18119],"force_p95":0.15972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26373,"mean_force":0.11607,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46323,-0.00889,0.18559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2903.0,"contact_point_centroid":[0.46473,-0.02638,0.18183],"force_p95":0.15686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23395,"mean_force":0.10597,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46357,-0.00844,0.18598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3071.0,"contact_point_centroid":[0.4565,-0.0501,0.04823],"force_p95":0.11002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14294,"mean_force":0.06654,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45613,-0.03098,0.04997]},{"body_a":"world","body_b":"grasp_target","contact_count":1964.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4788,-0.01168,0.22002]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45949,-0.02763,0.09615]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52058,0.03632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54552,0.10486,0.16446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5240.0,"contact_point_centroid":[0.45621,-0.01199,0.05054],"force_p95":0.08148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0853,"mean_force":0.04242,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45614,-0.03098,0.04999]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1464.0,"contact_point_centroid":[0.49859,0.04074,0.24079],"force_p95":0.01228,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01585,"mean_force":0.01063,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49815,0.04074,0.23851]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4257.0,"contact_point_centroid":[0.54574,0.10465,0.16694],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54535,0.10465,0.16469]}],"total_contact_groups":14},"final_pose_error":0.0726,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52058,0.03632,0.01602],"final_tcp_position":[0.58991,0.16187,0.10327],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.70925,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45846,-0.02398,0.13948],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46345,-0.03132,0.05735],"tcp_start":[0.45846,-0.02398,0.13948],"tcp_to_object_dist_end":0.0321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.0296,0.02473],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30663,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.21136,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10111.0,"raw_peak_contact_force":0.27063,"tcp_end":[0.4561,-0.03098,0.04994],"tcp_start":[0.46345,-0.03132,0.05735],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":692.0,"n_steps_budget":780.0,"object_pos_end":[0.4505,-0.02837,0.11063],"object_pos_start":[0.45845,-0.0296,0.02473],"object_to_goal_dist_end":0.29707,"object_to_goal_dist_start":0.30663,"object_z_max":0.11899,"peak_contact_force":0.10376,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30912.0,"raw_peak_contact_force":0.40197,"tcp_end":[0.45066,-0.02929,0.14421],"tcp_start":[0.4561,-0.03098,0.04994],"tcp_to_object_dist_end":0.03359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.52058,0.03632,0.01602],"object_pos_start":[0.4505,-0.02837,0.11063],"object_to_goal_dist_end":0.22621,"object_to_goal_dist_start":0.29707,"object_z_max":0.19087,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8627.0,"raw_peak_contact_force":1.77166,"subtask_id":"place_goal","tcp_end":[0.49797,0.04069,0.23819],"tcp_start":[0.498,0.04069,0.23824],"tcp_to_object_dist_end":0.22336,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52058,0.03632,0.01602],"object_pos_start":[0.52058,0.03632,0.01602],"object_to_goal_dist_end":0.22621,"object_to_goal_dist_start":0.22621,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8257.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58991,0.16187,0.10327],"tcp_start":[0.49797,0.04069,0.23819],"tcp_to_object_dist_end":0.16787,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```