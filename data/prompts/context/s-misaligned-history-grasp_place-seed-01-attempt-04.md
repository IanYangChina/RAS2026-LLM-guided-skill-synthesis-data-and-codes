## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0330 | 0.33 | ✅ accepted |
| 3 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0552 | 0.29 | ✅ accepted |
| 2 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.3662 | 0.14 | ❌ rejected |
| 1 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.0465 | 0.16 | ✅ accepted |
| 0 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.0517 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.052) — your mutation base

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
      default: 0.12
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    placement_offset_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
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
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - placement_offset_z: status=consumed; consumers=target.offset.z (add)
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

- **Composite score**: -0.052
- **task_score** (E): 0.230
- **fitness_score**: 0.578  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0823 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 0.67 | 1.00 | 0.0966 |
| approach_goal | 0.00 | 1.00 | 0.1052 |
| descend_place | 0.00 | 1.00 | 0.0854 |
| release | 1.00 | 1.00 | 0.0242 |
| retract | 1.00 | 1.00 | 0.0873 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 7.055 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.481, -0.001, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.481, -0.001, 0.057)→(0.473, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.279 | 1.00 / 40.667 | 0.148 | 0.176 |
| lift | lift | 0.67 / step_budget | (0.473, -0.001, 0.049)→(0.473, -0.001, 0.146) | (0.479, -0.001, 0.026)→(0.479, -0.001, 0.116) | 0.279→0.250 | 1.00 / 28.667 | 0.103 | 0.383 |
| approach_goal | approach | 0.00 / step_budget | (0.473, -0.001, 0.146)→(0.485, 0.024, 0.246) | (0.479, -0.001, 0.116)→(0.489, 0.050, 0.068) | 0.250→0.234 | 1.00 / 10.000 | 0.167 | 1.192 |
| descend_place | descend | 0.00 / step_budget | (0.485, 0.024, 0.246)→(0.524, 0.086, 0.205) | (0.489, 0.050, 0.068)→(0.495, 0.073, 0.016) | 0.234→0.227 | 1.00 / 8.000 | 0.123 | 0.624 |
| release | release | 1.00 / step_budget | (0.524, 0.086, 0.205)→(0.519, 0.086, 0.229) | (0.495, 0.073, 0.016)→(0.495, 0.073, 0.016) | 0.227→0.227 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.519, 0.086, 0.229)→(0.516, 0.085, 0.316) | (0.495, 0.073, 0.016)→(0.495, 0.073, 0.016) | 0.227→0.227 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.329
- phase_score: 0.273
- phase_breakdown.place_goal_score: 0.123
- phase_breakdown.reach_object_score: 0.623
- grasp_place_fitness: 0.629

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.629
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.329
- **Median Q (composite search score)**: -0.069
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38208,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00673,"align_grasp.lateral_offset_y":0.00151,"approach_goal.arc_height":0.05059,"approach_goal.transport_speed":0.06196,"approach_object.approach_speed":0.03659,"descend_place.placement_offset_z":-0.01747,"lift.lift_height":0.12588,"lift.lift_speed":0.09604,"release.release_duration":1.31001},"optimized_scores":{"best_composite_score":-0.00055,"best_fitness_score":0.62945,"best_task_score":0.32929},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1682.0,"contact_point_centroid":[0.52612,0.14887,-0.00259],"force_p95":0.26302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50118,"mean_force":0.14786,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52211,0.13594,0.18118]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.49941,0.04479,-0.00111],"force_p95":0.27166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39515,"mean_force":0.04615,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49332,0.04485,0.04953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11863.0,"contact_point_centroid":[0.49396,0.06358,0.09331],"force_p95":0.07572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28971,"mean_force":0.05243,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49366,0.04455,0.09229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10624.0,"contact_point_centroid":[0.49323,0.02543,0.09504],"force_p95":0.08384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28873,"mean_force":0.05737,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49376,0.04455,0.09397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4377.0,"contact_point_centroid":[0.51387,0.08065,0.19806],"force_p95":0.13084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26178,"mean_force":0.10264,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50932,0.09901,0.20223]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13431.0,"contact_point_centroid":[0.50045,0.07612,0.17319],"force_p95":0.12299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2094,"mean_force":0.07124,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49772,0.05747,0.17411]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.51421,0.1173,0.19765],"force_p95":0.11544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20917,"mean_force":0.09256,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50935,0.09916,0.20211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13233.0,"contact_point_centroid":[0.49969,0.03862,0.17248],"force_p95":0.12327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20193,"mean_force":0.0724,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49766,0.0573,0.17372]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49749,0.0201,0.21891]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50117,0.04498,-0.00202],"force_p95":0.12882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12927,"mean_force":0.12473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49582,0.04512,0.04902]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49836,0.04339,0.09439]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52607,0.14897,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52328,0.14933,0.17597]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.52607,0.14897,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51901,0.14807,0.23864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4131.0,"contact_point_centroid":[0.49396,0.0258,0.04922],"force_p95":0.07621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09887,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49467,0.04501,0.04775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.49478,0.06408,0.04888],"force_p95":0.06821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08768,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49467,0.04501,0.04775]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1495.0,"contact_point_centroid":[0.52347,0.13822,0.1821],"force_p95":0.01175,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01074,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52292,0.1382,0.17993]}],"total_contact_groups":17},"final_pose_error":0.01314,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52607,0.14897,0.01602],"final_tcp_position":[0.51922,0.1481,0.28365],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":20.91865,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":20.91865,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49721,0.04116,0.13806],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50245,0.04574,0.05642],"tcp_start":[0.49721,0.04116,0.13806],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04485,0.02589],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24214,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12826,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10795.0,"raw_peak_contact_force":0.12927,"tcp_end":[0.49464,0.04501,0.04772],"tcp_start":[0.50245,0.04574,0.05642],"tcp_to_object_dist_end":0.02276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50572,0.04464,0.11448],"object_pos_start":[0.50108,0.04485,0.02589],"object_to_goal_dist_end":0.21113,"object_to_goal_dist_start":0.24214,"object_z_max":0.11436,"peak_contact_force":0.07796,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22633.0,"raw_peak_contact_force":0.39515,"tcp_end":[0.49671,0.04449,0.13998],"tcp_start":[0.49464,0.04501,0.04772],"tcp_to_object_dist_end":0.02705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51105,0.08114,0.18312],"object_pos_start":[0.50572,0.04464,0.11448],"object_to_goal_dist_end":0.176,"object_to_goal_dist_start":0.21113,"object_z_max":0.18306,"peak_contact_force":0.11469,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26664.0,"raw_peak_contact_force":0.2094,"subtask_id":"place_goal","tcp_end":[0.5058,0.08094,0.21769],"tcp_start":[0.49671,0.04449,0.13998],"tcp_to_object_dist_end":0.03496,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52607,0.14897,0.01602],"object_pos_start":[0.51105,0.08114,0.18312],"object_to_goal_dist_end":0.16662,"object_to_goal_dist_start":0.176,"object_z_max":0.18312,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12398.0,"raw_peak_contact_force":1.50118,"subtask_id":"place_goal","tcp_end":[0.52722,0.15039,0.17317],"tcp_start":[0.5058,0.08094,0.21769],"tcp_to_object_dist_end":0.15716,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52607,0.14897,0.01602],"object_pos_start":[0.52607,0.14897,0.01602],"object_to_goal_dist_end":0.16662,"object_to_goal_dist_start":0.16662,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52178,0.14887,0.19652],"tcp_start":[0.52722,0.15039,0.17317],"tcp_to_object_dist_end":0.18055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.52607,0.14897,0.01602],"object_pos_start":[0.52607,0.14897,0.01602],"object_to_goal_dist_end":0.16662,"object_to_goal_dist_start":0.16662,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51922,0.1481,0.28365],"tcp_start":[0.52178,0.14887,0.19652],"tcp_to_object_dist_end":0.26772,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37433,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00979,"align_grasp.lateral_offset_y":-0.00126,"approach_goal.arc_height":0.06824,"approach_goal.transport_speed":0.089,"approach_object.approach_speed":0.05662,"descend_place.placement_offset_z":0.0085,"lift.lift_height":0.15777,"lift.lift_speed":0.06013,"release.release_duration":1.03197},"optimized_scores":{"best_composite_score":-0.06942,"best_fitness_score":0.56058,"best_task_score":0.19376},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.50183,0.04088,-0.00922],"force_p95":1.67942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90416,"mean_force":0.63018,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49274,0.00681,0.24812]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.47239,-0.02129,-0.00122],"force_p95":0.23713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37726,"mean_force":0.05584,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47149,-0.02084,0.05089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14062.0,"contact_point_centroid":[0.4695,-0.03975,0.09244],"force_p95":0.11129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28551,"mean_force":0.07013,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47009,-0.02072,0.09327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18247.0,"contact_point_centroid":[0.47003,-0.00203,0.0952],"force_p95":0.0952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27692,"mean_force":0.05448,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47012,-0.02072,0.09522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8143.0,"contact_point_centroid":[0.4759,-0.03129,0.18631],"force_p95":0.15298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25342,"mean_force":0.09624,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47479,-0.01301,0.18957]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50064,0.04424,-0.00204],"force_p95":0.12323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24735,"mean_force":0.12138,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51854,0.03826,0.23322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8445.0,"contact_point_centroid":[0.4778,0.00596,0.18869],"force_p95":0.12568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21564,"mean_force":0.09426,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47553,-0.01224,0.19229]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02023,-0.00207],"force_p95":0.14195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18148,"mean_force":0.12794,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4742,-0.02091,0.05027]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48651,-0.00892,0.22002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.47232,-0.0401,0.04988],"force_p95":0.07734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13423,"mean_force":0.05209,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47309,-0.02088,0.04911]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47607,-0.01969,0.09583]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50063,0.04423,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54171,0.06731,0.22502]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.50063,0.04423,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53803,0.06677,0.28744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.47317,-0.00181,0.04992],"force_p95":0.06973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07814,"mean_force":0.04441,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4731,-0.02088,0.04911]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4245.0,"contact_point_centroid":[0.51928,0.03876,0.23526],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51895,0.03876,0.23297]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.5443,0.06768,0.22232],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.544,0.06767,0.22005]}],"total_contact_groups":16},"final_pose_error":0.01318,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50063,0.04423,0.01602],"final_tcp_position":[0.53832,0.06679,0.33246],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.90416,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47446,-0.01833,0.13947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48063,-0.02108,0.05702],"tcp_start":[0.47446,-0.01833,0.13947],"tcp_to_object_dist_end":0.03134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02076,0.02573],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28897,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14013,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10817.0,"raw_peak_contact_force":0.18148,"tcp_end":[0.47307,-0.02088,0.04908],"tcp_start":[0.48063,-0.02108,0.05702],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47548,-0.0201,0.1186],"object_pos_start":[0.47607,-0.02076,0.02573],"object_to_goal_dist_end":0.24812,"object_to_goal_dist_start":0.28897,"object_z_max":0.1185,"peak_contact_force":0.11163,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32489.0,"raw_peak_contact_force":0.37726,"tcp_end":[0.47136,-0.02066,0.14836],"tcp_start":[0.47307,-0.02088,0.04908],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49667,0.04174,0.0046],"object_pos_start":[0.47548,-0.0201,0.1186],"object_to_goal_dist_end":0.25755,"object_to_goal_dist_start":0.24812,"object_z_max":0.19846,"peak_contact_force":0.26452,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16712.0,"raw_peak_contact_force":1.90416,"subtask_id":"place_goal","tcp_end":[0.49339,0.00749,0.24943],"tcp_start":[0.47136,-0.02066,0.14836],"tcp_to_object_dist_end":0.24723,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50063,0.04423,0.01602],"object_pos_start":[0.49667,0.04174,0.0046],"object_to_goal_dist_end":0.24617,"object_to_goal_dist_start":0.25755,"object_z_max":0.0168,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8245.0,"raw_peak_contact_force":0.24735,"subtask_id":"place_goal","tcp_end":[0.5452,0.06773,0.22241],"tcp_start":[0.49339,0.00749,0.24943],"tcp_to_object_dist_end":0.21245,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50063,0.04423,0.01602],"object_pos_start":[0.50063,0.04423,0.01602],"object_to_goal_dist_end":0.24617,"object_to_goal_dist_start":0.24617,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54041,0.06711,0.24547],"tcp_start":[0.5452,0.06773,0.22241],"tcp_to_object_dist_end":0.23399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50063,0.04423,0.01602],"object_pos_start":[0.50063,0.04423,0.01602],"object_to_goal_dist_end":0.24617,"object_to_goal_dist_start":0.24617,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53832,0.06679,0.33246],"tcp_start":[0.54041,0.06711,0.24547],"tcp_to_object_dist_end":0.31947,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67059,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00627,"align_grasp.lateral_offset_y":-0.00258,"approach_goal.arc_height":0.14928,"approach_goal.transport_speed":0.07123,"approach_object.approach_speed":0.08411,"descend_place.placement_offset_z":-0.01289,"lift.lift_height":0.19,"lift.lift_speed":0.05872,"release.release_duration":0.92122},"optimized_scores":{"best_composite_score":-0.08525,"best_fitness_score":0.54475,"best_task_score":0.16793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1214.0,"contact_point_centroid":[0.45963,0.02664,-0.00291],"force_p95":0.46494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46255,"mean_force":0.16222,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45234,-0.02352,0.2534]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.45575,-0.03005,-0.00135],"force_p95":0.23597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37548,"mean_force":0.06341,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45116,-0.02799,0.05229]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11766.0,"contact_point_centroid":[0.45021,-0.04657,0.09497],"force_p95":0.11547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32475,"mean_force":0.0818,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45057,-0.02776,0.09717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5266.0,"contact_point_centroid":[0.44972,-0.0141,0.18155],"force_p95":0.14957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32264,"mean_force":0.10537,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44579,-0.03192,0.18575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4636.0,"contact_point_centroid":[0.44888,-0.04994,0.17911],"force_p95":0.15719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29981,"mean_force":0.11213,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44589,-0.03184,0.18315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15477.0,"contact_point_centroid":[0.45047,-0.00926,0.09217],"force_p95":0.10852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26837,"mean_force":0.06415,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4504,-0.02777,0.09305]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45855,-0.02637,-0.00218],"force_p95":0.17356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21713,"mean_force":0.13566,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45381,-0.02811,0.05122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.45259,-0.04723,0.05009],"force_p95":0.10198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14816,"mean_force":0.05627,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45275,-0.02807,0.05016]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47885,-0.01166,0.22016]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45782,-0.02616,0.09595]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45942,0.02694,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.47753,0.01302,0.24228]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45942,0.02694,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.4952,0.04069,0.22429]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.45942,0.02694,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49155,0.04036,0.28798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5024.0,"contact_point_centroid":[0.45279,-0.0092,0.05068],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07388,"mean_force":0.04253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45275,-0.02807,0.05016]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1163.0,"contact_point_centroid":[0.45294,-0.02304,0.25727],"force_p95":0.0125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01079,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45272,-0.02304,0.255]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4212.0,"contact_point_centroid":[0.47796,0.01306,0.24454],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.47757,0.01306,0.24224]}],"total_contact_groups":17},"final_pose_error":0.01261,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45942,0.02694,0.01602],"final_tcp_position":[0.49177,0.04036,0.33283],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.46255,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45851,-0.02397,0.13953],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":500.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46002,-0.02837,0.05742],"tcp_start":[0.45851,-0.02397,0.13953],"tcp_to_object_dist_end":0.03151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02766,0.02519],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30499,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.17539,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10876.0,"raw_peak_contact_force":0.21713,"tcp_end":[0.45272,-0.02807,0.05013],"tcp_start":[0.46002,-0.02837,0.05742],"tcp_to_object_dist_end":0.0256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45684,-0.02707,0.11553],"object_pos_start":[0.45845,-0.02766,0.02519],"object_to_goal_dist_end":0.29221,"object_to_goal_dist_start":0.30499,"object_z_max":0.11543,"peak_contact_force":0.12007,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27435.0,"raw_peak_contact_force":0.37548,"tcp_end":[0.45233,-0.02763,0.14846],"tcp_start":[0.45272,-0.02807,0.05013],"tcp_to_object_dist_end":0.03324,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45942,0.02694,0.01602],"object_pos_start":[0.45684,-0.02707,0.11553],"object_to_goal_dist_end":0.26763,"object_to_goal_dist_start":0.29221,"object_z_max":0.18219,"peak_contact_force":0.12262,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12279.0,"raw_peak_contact_force":1.46255,"subtask_id":"place_goal","tcp_end":[0.45716,-0.01732,0.27012],"tcp_start":[0.45233,-0.02763,0.14846],"tcp_to_object_dist_end":0.25794,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45942,0.02694,0.01602],"object_pos_start":[0.45942,0.02694,0.01602],"object_to_goal_dist_end":0.26763,"object_to_goal_dist_start":0.26763,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8212.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.49864,0.04094,0.2206],"tcp_start":[0.45716,-0.01732,0.27012],"tcp_to_object_dist_end":0.20878,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45942,0.02694,0.01602],"object_pos_start":[0.45942,0.02694,0.01602],"object_to_goal_dist_end":0.26763,"object_to_goal_dist_start":0.26763,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49392,0.04056,0.24525],"tcp_start":[0.49864,0.04094,0.2206],"tcp_to_object_dist_end":0.23221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.45942,0.02694,0.01602],"object_pos_start":[0.45942,0.02694,0.01602],"object_to_goal_dist_end":0.26763,"object_to_goal_dist_start":0.26763,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49177,0.04036,0.33283],"tcp_start":[0.49392,0.04056,0.24525],"tcp_to_object_dist_end":0.31874,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```