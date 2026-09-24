## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0115 | 0.36 | ✅ accepted |
| 5 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0517 | 0.23 | ❌ rejected |
| 4 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0330 | 0.33 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0552 | 0.29 | ✅ accepted |
| 2 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0147 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.015) — your mutation base

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
  control: position_control
  termination: pose_tolerance
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
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
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
      - 0.1
      - 0.8
      default: 0.3
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

- **Composite score**: -0.015
- **task_score** (E): 0.305
- **fitness_score**: 0.615  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1667 |
| align_grasp | 1.00 | 1.00 | 0.0823 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 0.67 | 1.00 | 0.0958 |
| approach_goal | 1.00 | 1.00 | 0.2560 |
| descend_place | 1.00 | 1.00 | 0.0847 |
| release | 1.00 | 1.00 | 0.0198 |
| retract | 1.00 | 1.00 | 0.0850 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.481, -0.001, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.481, -0.001, 0.057)→(0.473, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 41.000 | 0.155 | 0.202 |
| lift | lift | 0.67 / step_budget | (0.473, -0.001, 0.049)→(0.474, -0.001, 0.145) | (0.479, -0.001, 0.026)→(0.477, -0.000, 0.115) | 0.278→0.252 | 1.00 / 27.667 | 79.533 | 0.381 |
| approach_goal | approach | 1.00 / step_budget | (0.474, -0.001, 0.145)→(0.598, 0.189, 0.252) | (0.477, -0.000, 0.115)→(0.542, 0.123, 0.013) | 0.252→0.190 | 1.00 / 7.000 | 91005.357 | 1.864 |
| descend_place | descend | 1.00 / step_budget | (0.598, 0.189, 0.252)→(0.603, 0.199, 0.168) | (0.542, 0.123, 0.013)→(0.544, 0.125, 0.019) | 0.190→0.183 | 1.00 / 8.667 | 182006.263 | 0.445 |
| release | release | 1.00 / step_budget | (0.603, 0.199, 0.168)→(0.597, 0.197, 0.187) | (0.544, 0.125, 0.019)→(0.544, 0.125, 0.019) | 0.183→0.183 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.597, 0.197, 0.187)→(0.594, 0.196, 0.272) | (0.544, 0.125, 0.019)→(0.544, 0.125, 0.019) | 0.183→0.183 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.417
- phase_score: 0.661
- phase_breakdown.place_goal_score: 0.677
- phase_breakdown.reach_object_score: 0.624
- grasp_place_fitness: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.672
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.417
- **Median Q (composite search score)**: -0.036
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70115,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00522,"align_grasp.lateral_offset_y":4e-05,"approach_goal.arc_height":0.05035,"approach_goal.transport_speed":0.32409,"approach_object.approach_speed":0.0647,"descend_place.descend_speed":0.23125,"lift.lift_height":0.12757,"lift.lift_speed":0.06163,"release.release_duration":1.5752},"optimized_scores":{"best_composite_score":0.04216,"best_fitness_score":0.67216,"best_task_score":0.41714},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.56119,0.24697,-0.00906],"force_p95":1.89586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90004,"mean_force":1.34799,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55578,0.22439,0.2439]},{"body_a":"world","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.56717,0.25512,-0.00374],"force_p95":0.46523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08917,"mean_force":0.1549,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55752,0.23263,0.2052]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.4978,0.04263,-0.00124],"force_p95":0.23207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39998,"mean_force":0.06038,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49179,0.04352,0.0497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19474.0,"contact_point_centroid":[0.49304,0.06226,0.09644],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29361,"mean_force":0.04985,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49306,0.04347,0.09581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15632.0,"contact_point_centroid":[0.49171,0.02431,0.09366],"force_p95":0.10567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27544,"mean_force":0.06221,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49288,0.04346,0.09344]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4491.0,"contact_point_centroid":[0.5147,0.07598,0.19871],"force_p95":0.14172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25788,"mean_force":0.09669,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51156,0.0944,0.202]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5012,0.04493,-0.00212],"force_p95":0.15576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21088,"mean_force":0.1316,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49444,0.04378,0.04911]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5321.0,"contact_point_centroid":[0.51367,0.10857,0.19604],"force_p95":0.13533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20975,"mean_force":0.0846,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5102,0.09027,0.19779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.49255,0.02446,0.04897],"force_p95":0.07978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14639,"mean_force":0.05207,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49329,0.04367,0.04785]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49755,0.02011,0.21889]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56688,0.25473,-0.00199],"force_p95":0.12283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12324,"mean_force":0.12261,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55505,0.23698,0.16474]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49769,0.04268,0.09437]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.56688,0.25473,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55083,0.23498,0.22574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4975.0,"contact_point_centroid":[0.49341,0.06278,0.04897],"force_p95":0.07296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07411,"mean_force":0.0442,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4933,0.04367,0.04785]},{"body_a":"left_finger","body_b":"right_finger","contact_count":451.0,"contact_point_centroid":[0.55825,0.23399,0.19741],"force_p95":0.01339,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01114,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55788,0.23397,0.19517]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.55801,0.23823,0.16244],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55751,0.2382,0.16024]}],"total_contact_groups":16},"final_pose_error":0.01435,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56688,0.25473,0.01602],"final_tcp_position":[0.55108,0.23503,0.27068],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273011.27139,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49723,0.0411,0.13829],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":510.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50106,0.04438,0.05647],"tcp_start":[0.49723,0.0411,0.13829],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50112,0.04402,0.02555],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24298,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15246,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.21088,"tcp_end":[0.49327,0.04367,0.04782],"tcp_start":[0.50106,0.04438,0.05647],"tcp_to_object_dist_end":0.02361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.50113,0.04488,0.11433],"object_pos_start":[0.50112,0.04402,0.02555],"object_to_goal_dist_end":0.21226,"object_to_goal_dist_start":0.24298,"object_z_max":0.11426,"peak_contact_force":0.10671,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35294.0,"raw_peak_contact_force":0.39998,"tcp_end":[0.49672,0.04364,0.14311],"tcp_start":[0.49327,0.04367,0.04782],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.56224,0.24891,-0.00427],"object_pos_start":[0.50113,0.04488,0.11433],"object_to_goal_dist_end":0.15112,"object_to_goal_dist_start":0.21226,"object_z_max":0.20966,"peak_contact_force":1.14879,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9845.0,"raw_peak_contact_force":1.90004,"subtask_id":"place_goal","tcp_end":[0.55647,0.22692,0.24324],"tcp_start":[0.49672,0.04364,0.14311],"tcp_to_object_dist_end":0.24855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.56689,0.25473,0.016],"object_pos_start":[0.56224,0.24891,-0.00427],"object_to_goal_dist_end":0.13117,"object_to_goal_dist_start":0.15112,"object_z_max":0.01698,"peak_contact_force":273011.27139,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":1.08917,"subtask_id":"place_goal","tcp_end":[0.55956,0.23887,0.1647],"tcp_start":[0.55647,0.22692,0.24324],"tcp_to_object_dist_end":0.14972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56688,0.25473,0.01602],"object_pos_start":[0.56689,0.25473,0.016],"object_to_goal_dist_end":0.13115,"object_to_goal_dist_start":0.13117,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12324,"tcp_end":[0.55357,0.23625,0.18476],"tcp_start":[0.55956,0.23887,0.1647],"tcp_to_object_dist_end":0.17027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.56688,0.25473,0.01602],"object_pos_start":[0.56688,0.25473,0.01602],"object_to_goal_dist_end":0.13115,"object_to_goal_dist_start":0.13115,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55108,0.23503,0.27068],"tcp_start":[0.55357,0.23625,0.18476],"tcp_to_object_dist_end":0.25591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82759,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00812,"align_grasp.lateral_offset_y":-0.00138,"approach_goal.arc_height":0.08586,"approach_goal.transport_speed":0.22316,"approach_object.approach_speed":0.07469,"descend_place.descend_speed":0.38106,"lift.lift_height":0.1352,"lift.lift_speed":0.05678,"release.release_duration":0.9401},"optimized_scores":{"best_composite_score":-0.05009,"best_fitness_score":0.57991,"best_task_score":0.23339},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1055.0,"contact_point_centroid":[0.52894,0.0615,-0.00331],"force_p95":0.65027,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80678,"mean_force":0.19307,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57669,0.09898,0.2999]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.47247,-0.02152,-0.00122],"force_p95":0.24724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37003,"mean_force":0.05856,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47,-0.02094,0.05095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3382.0,"contact_point_centroid":[0.47938,-0.02773,0.19956],"force_p95":0.15492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36226,"mean_force":0.09983,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47931,-0.00932,0.20274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13702.0,"contact_point_centroid":[0.46872,-0.03979,0.08976],"force_p95":0.10887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28006,"mean_force":0.07121,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46941,-0.02081,0.0908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16912.0,"contact_point_centroid":[0.46937,-0.00213,0.09035],"force_p95":0.09571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27221,"mean_force":0.0578,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46939,-0.02081,0.09081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3806.0,"contact_point_centroid":[0.48079,0.00937,0.19959],"force_p95":0.14361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25629,"mean_force":0.09133,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47975,-0.00884,0.20315]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02024,-0.00207],"force_p95":0.14384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18441,"mean_force":0.12843,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47267,-0.02102,0.05033]},{"body_a":"world","body_b":"grasp_target","contact_count":1976.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48648,-0.00891,0.22008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.47078,-0.0402,0.0499],"force_p95":0.07753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13515,"mean_force":0.05209,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47156,-0.02099,0.04918]},{"body_a":"world","body_b":"grasp_target","contact_count":568.0,"contact_point_centroid":[0.52886,0.05809,-0.00199],"force_p95":0.12313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12329,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62093,0.14954,0.24996]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52886,0.05809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62114,0.15352,0.20688]},{"body_a":"world","body_b":"grasp_target","contact_count":2064.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47527,-0.01975,0.09563]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.52886,0.05809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61742,0.15233,0.26637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4925.0,"contact_point_centroid":[0.47164,-0.00191,0.04997],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07036,"mean_force":0.04435,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47156,-0.02099,0.04918]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1165.0,"contact_point_centroid":[0.57768,0.09977,0.30271],"force_p95":0.01214,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01551,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5774,0.09977,0.30054]},{"body_a":"left_finger","body_b":"right_finger","contact_count":602.0,"contact_point_centroid":[0.62108,0.14954,0.25206],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62093,0.14954,0.24996]}],"total_contact_groups":17},"final_pose_error":0.0155,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52886,0.05809,0.02602],"final_tcp_position":[0.61778,0.15238,0.311],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273007.39575,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1976.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47438,-0.01833,0.1394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47909,-0.02119,0.05704],"tcp_start":[0.47438,-0.01833,0.1394],"tcp_to_object_dist_end":0.03118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02083,0.02571],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28903,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14193,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10829.0,"raw_peak_contact_force":0.18441,"tcp_end":[0.47153,-0.02099,0.04915],"tcp_start":[0.47909,-0.02119,0.05704],"tcp_to_object_dist_end":0.02387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47212,-0.02024,0.11253],"object_pos_start":[0.47607,-0.02083,0.02571],"object_to_goal_dist_end":0.25214,"object_to_goal_dist_start":0.28903,"object_z_max":0.11245,"peak_contact_force":238.40044,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30798.0,"raw_peak_contact_force":0.37003,"tcp_end":[0.47155,-0.02073,0.14249],"tcp_start":[0.47153,-0.02099,0.04915],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.52887,0.0581,0.02602],"object_pos_start":[0.47212,-0.02024,0.11253],"object_to_goal_dist_end":0.21825,"object_to_goal_dist_start":0.25214,"object_z_max":0.22791,"peak_contact_force":0.12323,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9408.0,"raw_peak_contact_force":1.80678,"subtask_id":"place_goal","tcp_end":[0.61759,0.14481,0.28964],"tcp_start":[0.47155,-0.02073,0.14249],"tcp_to_object_dist_end":0.29135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.52886,0.05809,0.02602],"object_pos_start":[0.52887,0.0581,0.02602],"object_to_goal_dist_end":0.21825,"object_to_goal_dist_start":0.21825,"object_z_max":0.02602,"peak_contact_force":273007.39575,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1170.0,"raw_peak_contact_force":0.12329,"subtask_id":"place_goal","tcp_end":[0.6253,0.15462,0.20812],"tcp_start":[0.61759,0.14481,0.28964],"tcp_to_object_dist_end":0.22755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52886,0.05809,0.02602],"object_pos_start":[0.52886,0.05809,0.02602],"object_to_goal_dist_end":0.21825,"object_to_goal_dist_start":0.21825,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.6198,0.15308,0.22636],"tcp_start":[0.6253,0.15462,0.20812],"tcp_to_object_dist_end":0.23964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.52886,0.05809,0.02602],"object_pos_start":[0.52886,0.05809,0.02602],"object_to_goal_dist_end":0.21825,"object_to_goal_dist_start":0.21825,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61778,0.15238,0.311],"tcp_start":[0.6198,0.15308,0.22636],"tcp_to_object_dist_end":0.31307,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45133,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00875,"align_grasp.lateral_offset_y":0.00086,"approach_goal.arc_height":0.19976,"approach_goal.transport_speed":0.48421,"approach_object.approach_speed":0.03404,"descend_place.descend_speed":0.51306,"lift.lift_height":0.17562,"lift.lift_speed":0.05792,"release.release_duration":1.68329},"optimized_scores":{"best_composite_score":-0.03621,"best_fitness_score":0.59379,"best_task_score":0.26442},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1343.0,"contact_point_centroid":[0.53491,0.06285,-0.00296],"force_p95":0.42964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88392,"mean_force":0.16154,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57096,0.13181,0.27094]},{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.4554,-0.02293,-0.00137],"force_p95":0.24238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37423,"mean_force":0.06097,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45336,-0.02487,0.0522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12022.0,"contact_point_centroid":[0.45303,-0.00602,0.09555],"force_p95":0.11238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31787,"mean_force":0.08017,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45227,-0.02489,0.0979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2878.0,"contact_point_centroid":[0.46897,0.01193,0.19999],"force_p95":0.14682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31694,"mean_force":0.09821,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46547,-0.00652,0.20366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15361.0,"contact_point_centroid":[0.45209,-0.04339,0.09277],"force_p95":0.1019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26992,"mean_force":0.06329,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45216,-0.02488,0.09397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3039.0,"contact_point_centroid":[0.47003,-0.02302,0.20277],"force_p95":0.13992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2655,"mean_force":0.09285,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46687,-0.00471,0.20653]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.0263,-0.00215],"force_p95":0.1688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20923,"mean_force":0.134,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45608,-0.02497,0.05112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4296.0,"contact_point_centroid":[0.45543,-0.00575,0.05028],"force_p95":0.09868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14806,"mean_force":0.05399,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45501,-0.02493,0.05005]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47865,-0.01164,0.22019]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45891,-0.02453,0.09608]},{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.53498,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62056,0.19929,0.1787]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53498,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61863,0.20203,0.1306]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.53498,0.06283,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61366,0.20015,0.18983]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4978.0,"contact_point_centroid":[0.45507,-0.04381,0.05055],"force_p95":0.07102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07486,"mean_force":0.04275,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45501,-0.02493,0.05006]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1290.0,"contact_point_centroid":[0.57691,0.13894,0.27173],"force_p95":0.01199,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57639,0.13893,0.26946]},{"body_a":"left_finger","body_b":"right_finger","contact_count":670.0,"contact_point_centroid":[0.62089,0.19925,0.18149],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62052,0.19924,0.17926]}],"total_contact_groups":17},"final_pose_error":0.01588,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53498,0.06283,0.01602],"final_tcp_position":[0.61391,0.20019,0.23444],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273014.79979,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45839,-0.02394,0.13969],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46232,-0.02519,0.05739],"tcp_start":[0.45839,-0.02394,0.13969],"tcp_to_object_dist_end":0.03161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02525,0.02524],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30311,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.17109,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11074.0,"raw_peak_contact_force":0.20923,"tcp_end":[0.45498,-0.02493,0.05003],"tcp_start":[0.46232,-0.02519,0.05739],"tcp_to_object_dist_end":0.02503,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45766,-0.02559,0.11732],"object_pos_start":[0.45845,-0.02525,0.02524],"object_to_goal_dist_end":0.29055,"object_to_goal_dist_start":0.30311,"object_z_max":0.11725,"peak_contact_force":0.09117,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27577.0,"raw_peak_contact_force":0.37423,"tcp_end":[0.45348,-0.02499,0.14885],"tcp_start":[0.45498,-0.02493,0.05003],"tcp_to_object_dist_end":0.03181,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.53498,0.06283,0.01602],"object_pos_start":[0.45766,-0.02559,0.11732],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.29055,"object_z_max":0.22159,"peak_contact_force":273014.79979,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8550.0,"raw_peak_contact_force":1.88392,"subtask_id":"place_goal","tcp_end":[0.6187,0.1953,0.22387],"tcp_start":[0.45348,-0.02499,0.14885],"tcp_to_object_dist_end":0.2603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.53498,0.06283,0.01602],"object_pos_start":[0.53498,0.06283,0.01602],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.19953,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1294.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62396,0.20382,0.13226],"tcp_start":[0.6187,0.1953,0.22387],"tcp_to_object_dist_end":0.20324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53498,0.06283,0.01602],"object_pos_start":[0.53498,0.06283,0.01602],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.19953,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61686,0.20134,0.14999],"tcp_start":[0.62396,0.20382,0.13226],"tcp_to_object_dist_end":0.20938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.53498,0.06283,0.01602],"object_pos_start":[0.53498,0.06283,0.01602],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.19953,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61391,0.20019,0.23444],"tcp_start":[0.61686,0.20134,0.14999],"tcp_to_object_dist_end":0.26982,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```