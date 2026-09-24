## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12  | -0.0511 | 0.31 | ❌ rejected |
| 9 | approach → align → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.1265 | 0.41 | ✅ accepted |
| 8 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0758 | 0.39 | ✅ accepted |
| 7 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0147 | 0.30 | ❌ rejected |
| 6 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.3114 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.311) — your mutation base

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

- **Composite score**: -0.311
- **task_score** (E): 0.181
- **fitness_score**: 0.469  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1667 |
| align_grasp | 1.00 | 1.00 | 0.0822 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift | 1.00 | 1.00 | 0.0893 |
| approach_goal | 1.00 | 1.00 | 0.2261 |
| descend_place | 1.00 | 1.00 | 0.0921 |
| release | 1.00 | 1.00 | 0.0194 |
| retract | 1.00 | 1.00 | 0.0848 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.479, -0.002, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.479, -0.002, 0.057)→(0.471, -0.002, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.002, 0.025) | 0.278→0.279 | 1.00 / 40.667 | 0.170 | 0.216 |
| lift | lift | 1.00 / step_budget | (0.471, -0.001, 0.274)→(0.478, 0.024, 0.189) | (0.479, -0.002, 0.025)→(0.474, -0.001, 0.118) | 0.279→0.256 | 1.00 / 8.333 | 94251.977 | 1.624 |
| approach_goal | approach | 1.00 / step_budget | (0.478, 0.024, 0.189)→(0.599, 0.192, 0.259) | (0.484, 0.028, 0.016)→(0.484, 0.028, 0.016) | 0.259→0.259 | 1.00 / 8.667 | 0.123 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.599, 0.192, 0.259)→(0.609, 0.204, 0.169) | (0.484, 0.028, 0.016)→(0.484, 0.028, 0.016) | 0.259→0.259 | 1.00 / 8.000 | 3249.665 | 0.123 |
| release | release | 1.00 / step_budget | (0.609, 0.204, 0.169)→(0.603, 0.201, 0.187) | (0.484, 0.028, 0.016)→(0.484, 0.028, 0.016) | 0.259→0.259 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.603, 0.201, 0.187)→(0.601, 0.200, 0.272) | (0.484, 0.028, 0.016)→(0.484, 0.028, 0.016) | 0.259→0.259 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.228
- phase_score: 0.186
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.619
- grasp_place_fitness: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.578
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.228
- **Median Q (composite search score)**: -0.243
- **K-run variance**: 0.0162
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70042,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00901,"align_grasp.lateral_offset_y":-0.002,"approach_goal.arc_height":0.12394,"approach_goal.transport_speed":0.13423,"approach_object.approach_speed":0.05435,"descend_place.descend_speed":0.14203,"descend_place.lateral_place_x":0.01656,"descend_place.lateral_place_y":0.00483,"descend_place.placement_z_offset":-0.00643,"lift.lift_height":0.15125,"lift.lift_speed":0.06924,"release.release_duration":1.17649},"optimized_scores":{"best_composite_score":-0.20161,"best_fitness_score":0.57839,"best_task_score":0.22804},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2534.0,"contact_point_centroid":[0.49266,0.07755,-0.00237],"force_p95":0.15979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86169,"mean_force":0.13993,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49001,0.05018,0.2344]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":24268.0,"contact_point_centroid":[0.49255,0.02311,0.12537],"force_p95":0.11865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34446,"mean_force":0.0752,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49327,0.04202,0.12709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":31487.0,"contact_point_centroid":[0.4935,0.06063,0.12633],"force_p95":0.11212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3183,"mean_force":0.05912,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49363,0.04203,0.12674]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50121,0.04485,-0.00227],"force_p95":0.19329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24911,"mean_force":0.14168,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49792,0.04191,0.04895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4068.0,"contact_point_centroid":[0.49598,0.02259,0.04843],"force_p95":0.08343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15202,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49677,0.04181,0.04768]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49759,0.0201,0.21897]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49946,0.04171,0.09465]},{"body_a":"world","body_b":"grasp_target","contact_count":2348.0,"contact_point_centroid":[0.4922,0.08099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51298,0.13368,0.25985]},{"body_a":"world","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.4922,0.08099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56332,0.23638,0.20688]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4922,0.08099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.56802,0.24196,0.15659]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.4922,0.08099,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56368,0.23988,0.21705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5132.0,"contact_point_centroid":[0.49689,0.06106,0.04882],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08195,"mean_force":0.04371,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49678,0.04181,0.04769]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2266.0,"contact_point_centroid":[0.49004,0.05156,0.25289],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01656,"mean_force":0.01071,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48955,0.05154,0.25069]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2496.0,"contact_point_centroid":[0.51356,0.1339,0.26219],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51307,0.13388,0.2599]},{"body_a":"left_finger","body_b":"right_finger","contact_count":766.0,"contact_point_centroid":[0.56383,0.23638,0.20935],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56328,0.23635,0.20712]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.57098,0.24325,0.15453],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01014,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57055,0.2432,0.15232]}],"total_contact_groups":16},"final_pose_error":0.01471,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.4922,0.08099,0.01602],"final_tcp_position":[0.56395,0.23993,0.26197],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273007.34544,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49729,0.04111,0.13828],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50457,0.0425,0.0564],"tcp_start":[0.49729,0.04111,0.13828],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04287,0.02503],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2442,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.18594,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11000.0,"raw_peak_contact_force":0.24911,"tcp_end":[0.49674,0.04181,0.04764],"tcp_start":[0.50457,0.0425,0.0564],"tcp_to_object_dist_end":0.02306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2189.0,"n_steps_budget":1000.0,"object_pos_end":[0.4932,0.04371,0.12189],"object_pos_start":[0.50111,0.04287,0.02503],"object_to_goal_dist_end":0.21483,"object_to_goal_dist_start":0.2442,"object_z_max":0.18653,"peak_contact_force":273007.34544,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":60555.0,"raw_peak_contact_force":1.86169,"tcp_end":[0.48869,0.07538,0.19468],"tcp_start":[0.49056,0.0434,0.28253],"tcp_to_object_dist_end":0.07951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.4922,0.08099,0.01602],"object_pos_start":[0.4922,0.08099,0.01602],"object_to_goal_dist_end":0.22174,"object_to_goal_dist_start":0.22174,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4844.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55598,0.22957,0.25587],"tcp_start":[0.48869,0.07538,0.19468],"tcp_to_object_dist_end":0.28926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.4922,0.08099,0.01602],"object_pos_start":[0.4922,0.08099,0.01602],"object_to_goal_dist_end":0.22174,"object_to_goal_dist_start":0.22174,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1486.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57263,0.24398,0.15705],"tcp_start":[0.55598,0.22957,0.25587],"tcp_to_object_dist_end":0.23005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4922,0.08099,0.01602],"object_pos_start":[0.4922,0.08099,0.01602],"object_to_goal_dist_end":0.22174,"object_to_goal_dist_start":0.22174,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56649,0.2412,0.1764],"tcp_start":[0.57263,0.24398,0.15705],"tcp_to_object_dist_end":0.23856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.4922,0.08099,0.01602],"object_pos_start":[0.4922,0.08099,0.01602],"object_to_goal_dist_end":0.22174,"object_to_goal_dist_start":0.22174,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56395,0.23993,0.26197],"tcp_start":[0.56649,0.2412,0.1764],"tcp_to_object_dist_end":0.3015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04306,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00224,"align_grasp.lateral_offset_y":-0.00148,"approach_goal.arc_height":0.08219,"approach_goal.transport_speed":0.15014,"approach_object.approach_speed":0.08339,"descend_place.descend_speed":0.08846,"descend_place.lateral_place_x":-0.00974,"descend_place.lateral_place_y":0.01111,"descend_place.placement_z_offset":0.00039,"lift.lift_height":0.11411,"lift.lift_speed":0.08052,"release.release_duration":1.01093},"optimized_scores":{"best_composite_score":-0.48958,"best_fitness_score":0.29042,"best_task_score":0.16091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1698.0,"contact_point_centroid":[0.48803,-0.0006,-0.00249],"force_p95":0.27961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5356,"mean_force":0.14564,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47095,-0.01511,0.17797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16195.0,"contact_point_centroid":[0.46889,-0.03938,0.10424],"force_p95":0.13019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32161,"mean_force":0.08299,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4666,-0.02069,0.10624]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18838.0,"contact_point_centroid":[0.46892,-0.00229,0.10497],"force_p95":0.12316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28326,"mean_force":0.07119,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46676,-0.0207,0.10618]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02019,-0.00209],"force_p95":0.15295,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19209,"mean_force":0.12981,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4673,-0.0211,0.05092]},{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48667,-0.00892,0.22012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.46567,-0.04024,0.05018],"force_p95":0.08804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1367,"mean_force":0.05603,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4662,-0.02106,0.04979]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47266,-0.01978,0.09614]},{"body_a":"world","body_b":"grasp_target","contact_count":3116.0,"contact_point_centroid":[0.48962,0.00199,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52689,0.04847,0.25807]},{"body_a":"world","body_b":"grasp_target","contact_count":588.0,"contact_point_centroid":[0.48962,0.00199,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61742,0.15341,0.25073]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48962,0.00199,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61383,0.16184,0.20744]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.48962,0.00199,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61017,0.16059,0.26704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4931.0,"contact_point_centroid":[0.46626,-0.0021,0.0504],"force_p95":0.07011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07098,"mean_force":0.0436,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46621,-0.02106,0.0498]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1380.0,"contact_point_centroid":[0.4725,-0.0137,0.19331],"force_p95":0.01227,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01084,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47223,-0.01369,0.191]},{"body_a":"left_finger","body_b":"right_finger","contact_count":616.0,"contact_point_centroid":[0.61783,0.15338,0.25305],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01061,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61742,0.15337,0.2509]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3281.0,"contact_point_centroid":[0.52735,0.04851,0.26058],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01057,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52693,0.04851,0.25831]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.6165,0.16267,0.20561],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61607,0.16266,0.2036]}],"total_contact_groups":16},"final_pose_error":0.01541,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48962,0.00199,0.01602],"final_tcp_position":[0.61053,0.16064,0.31168],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.46308,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1960.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4746,-0.01833,0.13956],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47366,-0.02126,0.05749],"tcp_start":[0.4746,-0.01833,0.13956],"tcp_to_object_dist_end":0.03159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47613,-0.02087,0.02555],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28911,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15519,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.19209,"tcp_end":[0.46618,-0.02107,0.04976],"tcp_start":[0.47366,-0.02126,0.05749],"tcp_to_object_dist_end":0.02618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1477.0,"n_steps_budget":720.0,"object_pos_end":[0.47183,-0.01962,0.0897],"object_pos_start":[0.47613,-0.02087,0.02555],"object_to_goal_dist_end":0.25982,"object_to_goal_dist_start":0.28911,"object_z_max":0.13835,"peak_contact_force":9748.46308,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38111.0,"raw_peak_contact_force":1.5356,"tcp_end":[0.48229,-0.00171,0.15568],"tcp_start":[0.4683,-0.01958,0.21314],"tcp_to_object_dist_end":0.06916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.48962,0.00199,0.01602],"object_pos_start":[0.48962,0.00199,0.01602],"object_to_goal_dist_end":0.27403,"object_to_goal_dist_start":0.27403,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6397.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6175,0.14512,0.291],"tcp_start":[0.48229,-0.00171,0.15568],"tcp_to_object_dist_end":0.33534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.48962,0.00199,0.01602],"object_pos_start":[0.48962,0.00199,0.01602],"object_to_goal_dist_end":0.27403,"object_to_goal_dist_start":0.27403,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61796,0.16283,0.20846],"tcp_start":[0.6175,0.14512,0.291],"tcp_to_object_dist_end":0.28173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48962,0.00199,0.01602],"object_pos_start":[0.48962,0.00199,0.01602],"object_to_goal_dist_end":0.27403,"object_to_goal_dist_start":0.27403,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61251,0.16136,0.22695],"tcp_start":[0.61796,0.16283,0.20846],"tcp_to_object_dist_end":0.29153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.48962,0.00199,0.01602],"object_pos_start":[0.48962,0.00199,0.01602],"object_to_goal_dist_end":0.27403,"object_to_goal_dist_start":0.27403,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61053,0.16064,0.31168],"tcp_start":[0.61251,0.16136,0.22695],"tcp_to_object_dist_end":0.35666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15385,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00459,"align_grasp.lateral_offset_y":-0.00209,"approach_goal.arc_height":0.11706,"approach_goal.transport_speed":0.13776,"approach_object.approach_speed":0.08079,"descend_place.descend_speed":0.2434,"descend_place.lateral_place_x":0.01717,"descend_place.lateral_place_y":-0.00165,"descend_place.placement_z_offset":0.00998,"lift.lift_height":0.17157,"lift.lift_speed":0.08693,"release.release_duration":1.55707},"optimized_scores":{"best_composite_score":-0.24307,"best_fitness_score":0.53693,"best_task_score":0.15367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4362.0,"contact_point_centroid":[0.46836,-0.00091,-0.0022],"force_p95":0.12411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47608,"mean_force":0.12964,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45319,-0.0229,0.26167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14983.0,"contact_point_centroid":[0.45314,-0.04584,0.12967],"force_p95":0.12482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32931,"mean_force":0.0919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45077,-0.02725,0.1327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19449.0,"contact_point_centroid":[0.45225,-0.00892,0.12417],"force_p95":0.12043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28318,"mean_force":0.07286,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45052,-0.02727,0.12569]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02634,-0.00214],"force_p95":0.1658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20796,"mean_force":0.13321,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45228,-0.02766,0.05143]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4133.0,"contact_point_centroid":[0.4509,-0.04678,0.05042],"force_p95":0.09996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14144,"mean_force":0.05545,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45121,-0.02761,0.05038]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47879,-0.01167,0.22009]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45706,-0.02591,0.09635]},{"body_a":"world","body_b":"grasp_target","contact_count":3284.0,"contact_point_centroid":[0.46884,0.00015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53168,0.08496,0.2878]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.46884,0.00015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62905,0.20197,0.18587]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46884,0.00015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63259,0.20198,0.13871]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.46884,0.00015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62776,0.20017,0.19735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4971.0,"contact_point_centroid":[0.45125,-0.00876,0.05083],"force_p95":0.07147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0723,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45122,-0.02761,0.05038]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4204.0,"contact_point_centroid":[0.45388,-0.02251,0.27451],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01064,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45355,-0.02251,0.27222]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3484.0,"contact_point_centroid":[0.53229,0.08528,0.29011],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.0105,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53192,0.08528,0.28784]},{"body_a":"left_finger","body_b":"right_finger","contact_count":668.0,"contact_point_centroid":[0.62941,0.20197,0.18847],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62898,0.20196,0.18623]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.63581,0.20303,0.13755],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63542,0.20301,0.13529]}],"total_contact_groups":16},"final_pose_error":0.01624,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.46884,0.00015,0.01602],"final_tcp_position":[0.62805,0.20021,0.24193],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.75121,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45855,-0.02395,0.13967],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":485.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45847,-0.02791,0.0576],"tcp_start":[0.45855,-0.02395,0.13967],"tcp_to_object_dist_end":0.03162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02737,0.0253],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30473,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16822,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10904.0,"raw_peak_contact_force":0.20796,"tcp_end":[0.45119,-0.02761,0.05035],"tcp_start":[0.45847,-0.02791,0.0576],"tcp_to_object_dist_end":0.02608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2210.0,"n_steps_budget":1000.0,"object_pos_end":[0.4557,-0.02653,0.14367],"object_pos_start":[0.45845,-0.02737,0.0253],"object_to_goal_dist_end":0.29395,"object_to_goal_dist_start":0.30473,"object_z_max":0.15804,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42998.0,"raw_peak_contact_force":1.47608,"tcp_end":[0.46398,-0.0028,0.21555],"tcp_start":[0.45335,-0.02645,0.32508],"tcp_to_object_dist_end":0.07615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.46884,0.00015,0.01602],"object_pos_start":[0.46884,0.00015,0.01602],"object_to_goal_dist_end":0.28094,"object_to_goal_dist_start":0.28094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6768.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6223,0.20042,0.23019],"tcp_start":[0.46398,-0.0028,0.21555],"tcp_to_object_dist_end":0.33095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.46884,0.00015,0.01602],"object_pos_start":[0.46884,0.00015,0.01602],"object_to_goal_dist_end":0.28094,"object_to_goal_dist_start":0.28094,"object_z_max":0.01602,"peak_contact_force":9748.75121,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.63776,0.20383,0.14093],"tcp_start":[0.6223,0.20042,0.23019],"tcp_to_object_dist_end":0.29261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46884,0.00015,0.01602],"object_pos_start":[0.46884,0.00015,0.01602],"object_to_goal_dist_end":0.28094,"object_to_goal_dist_start":0.28094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63085,0.20132,0.15788],"tcp_start":[0.63776,0.20383,0.14093],"tcp_to_object_dist_end":0.29469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.46884,0.00015,0.01602],"object_pos_start":[0.46884,0.00015,0.01602],"object_to_goal_dist_end":0.28094,"object_to_goal_dist_start":0.28094,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62805,0.20021,0.24193],"tcp_start":[0.63085,0.20132,0.15788],"tcp_to_object_dist_end":0.34119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```