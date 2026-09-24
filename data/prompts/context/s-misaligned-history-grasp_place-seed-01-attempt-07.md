## Search State

- **Seed**: 1
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0147 | 0.30 | ❌ rejected |
| 6 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0115 | 0.36 | ✅ accepted |
| 5 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0517 | 0.23 | ❌ rejected |
| 4 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0330 | 0.33 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.0758 | 0.39 | ✅ accepted |

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

## Current Skill (Q=0.076) — your mutation base

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
  generator: linear_cartesian
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
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
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
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=repeat
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

- **Composite score**: 0.076
- **task_score** (E): 0.387
- **fitness_score**: 0.656  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0823 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 0.67 | 1.00 | 0.1150 |
| approach_goal | 1.00 | 1.00 | 0.0020 |
| descend_place | 1.00 | 1.00 | 0.0686 |
| release | 1.00 | 1.00 | 0.0198 |
| retract | 1.00 | 1.00 | 0.0850 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.480, -0.002, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.480, -0.002, 0.057)→(0.473, -0.003, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.002, 0.025) | 0.278→0.279 | 1.00 / 40.667 | 0.173 | 0.226 |
| lift | lift | 0.67 / step_budget | (0.473, -0.003, 0.049)→(0.474, -0.002, 0.164) | (0.479, -0.002, 0.025)→(0.479, -0.001, 0.133) | 0.279→0.251 | 1.00 / 25.333 | 0.128 | 0.399 |
| approach_goal | approach | 1.00 / step_budget | (0.599, 0.192, 0.238)→(0.600, 0.194, 0.237) | (0.479, -0.001, 0.133)→(0.573, 0.173, 0.014) | 0.251→0.147 | 1.00 / 8.000 | 3249.679 | 1.738 |
| descend_place | descend | 1.00 / step_budget | (0.600, 0.194, 0.237)→(0.603, 0.200, 0.169) | (0.573, 0.173, 0.016)→(0.573, 0.173, 0.016) | 0.145→0.145 | 1.00 / 8.667 | 182005.364 | 0.124 |
| release | release | 1.00 / step_budget | (0.603, 0.200, 0.169)→(0.597, 0.198, 0.187) | (0.573, 0.173, 0.016)→(0.573, 0.173, 0.016) | 0.145→0.145 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.597, 0.198, 0.187)→(0.594, 0.197, 0.272) | (0.573, 0.173, 0.016)→(0.573, 0.173, 0.016) | 0.145→0.145 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.455
- phase_score: 0.662
- phase_breakdown.place_goal_score: 0.675
- phase_breakdown.reach_object_score: 0.633
- grasp_place_fitness: 0.689

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.689
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.455
- **Median Q (composite search score)**: 0.092
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41748,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00985,"align_grasp.lateral_offset_y":-0.00052,"approach_goal.transport_speed":0.25499,"approach_object.approach_speed":0.0551,"descend_place.descend_speed":0.1982,"lift.lift_height":0.18758,"lift.lift_speed":0.06788,"release.release_duration":1.3863},"optimized_scores":{"best_composite_score":0.09243,"best_fitness_score":0.67243,"best_task_score":0.41449},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":236.0,"contact_point_centroid":[0.54554,0.24188,-0.00688],"force_p95":1.18154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69368,"mean_force":0.33163,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55614,0.22743,0.23197]},{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.49801,0.04229,-0.00131],"force_p95":0.24127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43053,"mean_force":0.05843,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49578,0.043,0.04954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.49476,0.06176,0.10353],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31435,"mean_force":0.05011,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49468,0.04298,0.10286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15832.0,"contact_point_centroid":[0.49377,0.02383,0.09932],"force_p95":0.11078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29006,"mean_force":0.06292,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49459,0.04297,0.09915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4647.0,"contact_point_centroid":[0.51597,0.09619,0.18203],"force_p95":0.13299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24227,"mean_force":0.08539,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51801,0.11499,0.18524]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50119,0.0449,-0.00217],"force_p95":0.16609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22081,"mean_force":0.1346,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49868,0.04326,0.04891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5762.0,"contact_point_centroid":[0.51627,0.13059,0.1819],"force_p95":0.11123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19148,"mean_force":0.07075,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51713,0.11208,0.18417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.49678,0.02395,0.04871],"force_p95":0.08117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15098,"mean_force":0.05211,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49752,0.04316,0.04762]},{"body_a":"world","body_b":"grasp_target","contact_count":2236.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49758,0.0201,0.21895]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.5456,0.2437,-0.00192],"force_p95":0.12477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12527,"mean_force":0.11864,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55823,0.23644,0.20111]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49982,0.04241,0.0947]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5456,0.2437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55502,0.23813,0.16541]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5456,0.2437,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55082,0.23613,0.22638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5030.0,"contact_point_centroid":[0.49765,0.0623,0.04882],"force_p95":0.07473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07617,"mean_force":0.04399,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49753,0.04316,0.04763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":13.0,"contact_point_centroid":[0.55849,0.23305,0.23584],"force_p95":0.01579,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01579,"mean_force":0.01511,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55747,0.23302,0.2332]},{"body_a":"left_finger","body_b":"right_finger","contact_count":534.0,"contact_point_centroid":[0.55867,0.23645,0.20359],"force_p95":0.01302,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01503,"mean_force":0.01082,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55822,0.23642,0.2014]}],"total_contact_groups":17},"final_pose_error":0.01437,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5456,0.2437,0.01602],"final_tcp_position":[0.55107,0.23618,0.27132],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273009.92846,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49728,0.04113,0.13822],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50534,0.04386,0.05638],"tcp_start":[0.49728,0.04113,0.13822],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04369,0.02539],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24334,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16128,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10911.0,"raw_peak_contact_force":0.22081,"tcp_end":[0.4975,0.04316,0.04759],"tcp_start":[0.50534,0.04386,0.05638],"tcp_to_object_dist_end":0.02249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,0.04429,0.13109],"object_pos_start":[0.50109,0.04369,0.02539],"object_to_goal_dist_end":0.21122,"object_to_goal_dist_start":0.24334,"object_z_max":0.13099,"peak_contact_force":0.15083,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36018.0,"raw_peak_contact_force":0.43053,"tcp_end":[0.49608,0.04319,0.15895],"tcp_start":[0.4975,0.04316,0.04759],"tcp_to_object_dist_end":0.02817,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.54613,0.24369,0.00907],"object_pos_start":[0.50009,0.04429,0.13109],"object_to_goal_dist_end":0.13892,"object_to_goal_dist_start":0.21122,"object_z_max":0.17858,"peak_contact_force":0.08297,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10658.0,"raw_peak_contact_force":1.69368,"subtask_id":"place_goal","tcp_end":[0.5576,0.23334,0.23331],"tcp_start":[0.55759,0.23136,0.23387],"tcp_to_object_dist_end":0.22478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,0.2437,0.01602],"object_pos_start":[0.54576,0.2438,0.01548],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13262,"object_z_max":0.01663,"peak_contact_force":273009.92846,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1034.0,"raw_peak_contact_force":0.12527,"subtask_id":"place_goal","tcp_end":[0.55952,0.24007,0.16543],"tcp_start":[0.5576,0.23334,0.23331],"tcp_to_object_dist_end":0.1501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5456,0.2437,0.01602],"object_pos_start":[0.5456,0.2437,0.01602],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55355,0.2374,0.18542],"tcp_start":[0.55952,0.24007,0.16543],"tcp_to_object_dist_end":0.1697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.5456,0.2437,0.01602],"object_pos_start":[0.5456,0.2437,0.01602],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55107,0.23618,0.27132],"tcp_start":[0.55355,0.2374,0.18542],"tcp_to_object_dist_end":0.25547,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64615,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00395,"align_grasp.lateral_offset_y":-0.00278,"approach_goal.transport_speed":0.20549,"approach_object.approach_speed":0.06831,"descend_place.descend_speed":0.15658,"lift.lift_height":0.12611,"lift.lift_speed":0.065,"release.release_duration":1.13782},"optimized_scores":{"best_composite_score":0.0264,"best_fitness_score":0.6064,"best_task_score":0.29113},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.57998,0.12258,-0.00287],"force_p95":0.45694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72943,"mean_force":0.16756,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59724,0.12271,0.25289]},{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.47325,-0.02351,-0.0013],"force_p95":0.2307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38723,"mean_force":0.05346,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46639,-0.02219,0.05149]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11210.0,"contact_point_centroid":[0.46749,-0.04089,0.08922],"force_p95":0.11602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31766,"mean_force":0.07663,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46757,-0.02184,0.09097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16413.0,"contact_point_centroid":[0.46745,-0.00327,0.0935],"force_p95":0.08916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27504,"mean_force":0.05393,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46772,-0.02182,0.09342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3491.0,"contact_point_centroid":[0.51108,0.0032,0.16842],"force_p95":0.14618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2401,"mean_force":0.09872,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50739,0.02143,0.17264]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47622,-0.02023,-0.00219],"force_p95":0.17527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22864,"mean_force":0.1364,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46887,-0.02229,0.05053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3590.0,"contact_point_centroid":[0.51011,0.03918,0.16886],"force_p95":0.13824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20991,"mean_force":0.09647,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50705,0.02094,0.17237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.46724,-0.04155,0.04965],"force_p95":0.09066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15284,"mean_force":0.05446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46777,-0.02226,0.0494]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48653,-0.00894,0.21993]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47342,-0.02042,0.09555]},{"body_a":"world","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.57983,0.12278,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62408,0.15373,0.24367]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57983,0.12278,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62198,0.1549,0.20761]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.57983,0.12278,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61828,0.15372,0.26705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.46784,-0.00324,0.05014],"force_p95":0.07364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07585,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46778,-0.02226,0.04941]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1027.0,"contact_point_centroid":[0.60275,0.12843,0.2597],"force_p95":0.01262,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01495,"mean_force":0.01069,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60235,0.12842,0.25742]},{"body_a":"left_finger","body_b":"right_finger","contact_count":503.0,"contact_point_centroid":[0.62462,0.15375,0.24596],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62408,0.15374,0.2436]}],"total_contact_groups":17},"final_pose_error":0.01554,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.57983,0.12278,0.01602],"final_tcp_position":[0.61864,0.15377,0.31168],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273010.45309,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47451,-0.01834,0.13947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47524,-0.02247,0.05714],"tcp_start":[0.47451,-0.01834,0.13947],"tcp_to_object_dist_end":0.03122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47614,-0.0216,0.02525],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28974,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.17531,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10967.0,"raw_peak_contact_force":0.22864,"tcp_end":[0.46774,-0.02226,0.04937],"tcp_start":[0.47524,-0.02247,0.05714],"tcp_to_object_dist_end":0.02555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":873.0,"n_steps_budget":990.0,"object_pos_end":[0.47667,-0.02007,0.11074],"object_pos_start":[0.47614,-0.0216,0.02525],"object_to_goal_dist_end":0.24974,"object_to_goal_dist_start":0.28974,"object_z_max":0.11066,"peak_contact_force":0.10609,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27801.0,"raw_peak_contact_force":0.38723,"tcp_end":[0.4718,-0.02151,0.14189],"tcp_start":[0.46774,-0.02226,0.04937],"tcp_to_object_dist_end":0.03157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.57983,0.12278,0.01602],"object_pos_start":[0.47667,-0.02007,0.11074],"object_to_goal_dist_end":0.1851,"object_to_goal_dist_start":0.24974,"object_z_max":0.16975,"peak_contact_force":9748.83065,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9281.0,"raw_peak_contact_force":1.72943,"subtask_id":"place_goal","tcp_end":[0.62263,0.15174,0.27459],"tcp_start":[0.62199,0.15039,0.27488],"tcp_to_object_dist_end":0.26368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.57983,0.12278,0.01602],"object_pos_start":[0.57983,0.12278,0.01602],"object_to_goal_dist_end":0.1851,"object_to_goal_dist_start":0.1851,"object_z_max":0.01602,"peak_contact_force":273006.0395,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":971.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62612,0.15605,0.20893],"tcp_start":[0.62263,0.15174,0.27459],"tcp_to_object_dist_end":0.20115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57983,0.12278,0.01602],"object_pos_start":[0.57983,0.12278,0.01602],"object_to_goal_dist_end":0.1851,"object_to_goal_dist_start":0.1851,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62064,0.15446,0.22707],"tcp_start":[0.62612,0.15605,0.20893],"tcp_to_object_dist_end":0.21728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.57983,0.12278,0.01602],"object_pos_start":[0.57983,0.12278,0.01602],"object_to_goal_dist_end":0.1851,"object_to_goal_dist_start":0.1851,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61864,0.15377,0.31168],"tcp_start":[0.62064,0.15446,0.22707],"tcp_to_object_dist_end":0.2998,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45098,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00707,"align_grasp.lateral_offset_y":-0.00305,"approach_goal.transport_speed":0.11117,"approach_object.approach_speed":0.04224,"descend_place.descend_speed":0.22503,"lift.lift_height":0.17708,"lift.lift_speed":0.09631,"release.release_duration":0.99377},"optimized_scores":{"best_composite_score":0.10852,"best_fitness_score":0.68852,"best_task_score":0.45515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.59341,0.15251,-0.00365],"force_p95":0.9113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79187,"mean_force":0.21285,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60758,0.18092,0.20354]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.45628,-0.0299,-0.00138],"force_p95":0.25299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37903,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45206,-0.02842,0.05232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5012.0,"contact_point_centroid":[0.519,0.03805,0.1899],"force_p95":0.13286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37097,"mean_force":0.10445,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51463,0.05614,0.19388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10480.0,"contact_point_centroid":[0.45241,-0.04697,0.11281],"force_p95":0.12325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3361,"mean_force":0.08423,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45202,-0.02807,0.11526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4752.0,"contact_point_centroid":[0.51839,0.07338,0.18968],"force_p95":0.13756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29108,"mean_force":0.11,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51396,0.05524,0.19381]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15814.0,"contact_point_centroid":[0.45203,-0.00963,0.1131],"force_p95":0.10606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27934,"mean_force":0.05776,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4519,-0.02808,0.11326]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45855,-0.02639,-0.00221],"force_p95":0.18053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22898,"mean_force":0.13789,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45455,-0.02855,0.05118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3846.0,"contact_point_centroid":[0.45379,-0.04765,0.04972],"force_p95":0.10465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1532,"mean_force":0.05829,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45348,-0.0285,0.05011]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47867,-0.01167,0.21998]},{"body_a":"world","body_b":"grasp_target","contact_count":508.0,"contact_point_centroid":[0.59367,0.15356,-0.00199],"force_p95":0.12287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12318,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62073,0.20007,0.16934]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45819,-0.02639,0.09591]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59367,0.15356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61814,0.2019,0.13041]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.59367,0.15356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61315,0.20003,0.18963]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.45353,-0.00965,0.05066],"force_p95":0.07401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07572,"mean_force":0.04229,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45349,-0.0285,0.05012]},{"body_a":"left_finger","body_b":"right_finger","contact_count":339.0,"contact_point_centroid":[0.61387,0.18903,0.2063],"force_p95":0.01448,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01131,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61367,0.18903,0.20419]},{"body_a":"left_finger","body_b":"right_finger","contact_count":541.0,"contact_point_centroid":[0.621,0.20008,0.17183],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62073,0.20007,0.16941]}],"total_contact_groups":17},"final_pose_error":0.01588,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59367,0.15356,0.01602],"final_tcp_position":[0.6134,0.20007,0.23424],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.64877,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4585,-0.02398,0.1395],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":506.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46077,-0.0288,0.0574],"tcp_start":[0.4585,-0.02398,0.1395],"tcp_to_object_dist_end":0.03156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02794,0.0251],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30524,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.18119,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10714.0,"raw_peak_contact_force":0.22898,"tcp_end":[0.45346,-0.0285,0.05008],"tcp_start":[0.46077,-0.0288,0.0574],"tcp_to_object_dist_end":0.02548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.46161,-0.02665,0.15847],"object_pos_start":[0.45844,-0.02794,0.0251],"object_to_goal_dist_end":0.29245,"object_to_goal_dist_start":0.30524,"object_z_max":0.15837,"peak_contact_force":0.12605,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26444.0,"raw_peak_contact_force":0.37903,"tcp_end":[0.45478,-0.02779,0.19101],"tcp_start":[0.45346,-0.0285,0.05008],"tcp_to_object_dist_end":0.03327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":809.0,"n_steps_budget":1000.0,"object_pos_end":[0.59361,0.15357,0.01603],"object_pos_start":[0.46161,-0.02665,0.15847],"object_to_goal_dist_end":0.11807,"object_to_goal_dist_start":0.29245,"object_z_max":0.16177,"peak_contact_force":0.12321,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10667.0,"raw_peak_contact_force":1.79187,"subtask_id":"place_goal","tcp_end":[0.61896,0.19698,0.20334],"tcp_start":[0.61831,0.19503,0.20486],"tcp_to_object_dist_end":0.19394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.59367,0.15356,0.01602],"object_pos_start":[0.59365,0.15356,0.016],"object_to_goal_dist_end":0.11807,"object_to_goal_dist_start":0.11809,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1049.0,"raw_peak_contact_force":0.12318,"subtask_id":"place_goal","tcp_end":[0.62347,0.20369,0.13206],"tcp_start":[0.61896,0.19698,0.20334],"tcp_to_object_dist_end":0.12987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59367,0.15356,0.01602],"object_pos_start":[0.59367,0.15356,0.01602],"object_to_goal_dist_end":0.11807,"object_to_goal_dist_start":0.11807,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61636,0.20121,0.1498],"tcp_start":[0.62347,0.20369,0.13206],"tcp_to_object_dist_end":0.14382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.59367,0.15356,0.01602],"object_pos_start":[0.59367,0.15356,0.01602],"object_to_goal_dist_end":0.11807,"object_to_goal_dist_start":0.11807,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6134,0.20007,0.23424],"tcp_start":[0.61636,0.20121,0.1498],"tcp_to_object_dist_end":0.22399,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```