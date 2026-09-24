## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2935 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2928 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2936 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0598 | 0.39 | ✅ accepted |
| 8 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0087 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=0.294) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_object
  weight: 0.5
phases:
- id: approach_object
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    descend_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_bilateral
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: pull_up
  type: pull
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
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    pull_up_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: pull_object_follows
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
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
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_object_lost
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_clearance
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_retained
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: place_object
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_x_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_y_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_x_offset: status=consumed; consumers=target.offset.x (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **pull_up** (`pull`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - pull_up_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=pull_object_follows, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_object_lost, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_retained, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_x_offset: status=consumed; consumers=target.offset.x (add)
    - place_y_offset: status=consumed; consumers=target.offset.y (add)

## Design Metrics

- **Composite score**: 0.294
- **task_score** (E): 1.000
- **fitness_score**: 0.994  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1202 |
| descend_to_grasp | 1.00 | 1.00 | 0.1491 |
| grasp | 1.00 | 1.00 | 0.0131 |
| pull_up | 1.00 | 1.00 | 0.0217 |
| lift | 1.00 | 1.00 | 0.1000 |
| approach_goal | 1.00 | 1.00 | 0.0018 |
| descend_place | 1.00 | 1.00 | 0.1266 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.001, 0.186) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.001, 0.186)→(0.524, -0.015, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 44.000 | 0.169 | 0.253 |
| grasp | grasp | 1.00 / step_budget | (0.524, -0.015, 0.039)→(0.516, -0.015, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 40.000 | 0.072 | 0.583 |
| pull_up | pull | 1.00 / step_budget | (0.511, -0.015, 0.050)→(0.506, -0.015, 0.071) | (0.515, -0.015, 0.025)→(0.510, -0.015, 0.045) | 0.269→0.261 | 1.00 / 38.667 | 0.083 | 0.112 |
| lift | lift | 1.00 / step_budget | (0.500, -0.015, 0.252)→(0.498, -0.015, 0.352) | (0.506, -0.015, 0.065)→(0.502, -0.015, 0.145) | 0.254→0.237 | 1.00 / 35.333 | 55983.986 | 0.259 |
| approach_goal | approach | 1.00 / step_budget | (0.610, 0.172, 0.314)→(0.610, 0.173, 0.314) | (0.512, -0.014, 0.341)→(0.614, 0.167, 0.293) | 0.291→0.126 | 1.00 / 41.667 | 0.078 | 0.213 |
| descend_place | descend | 1.00 / step_budget | (0.610, 0.173, 0.314)→(0.617, 0.180, 0.188) | (0.617, 0.173, 0.295)→(0.615, 0.179, 0.168) | 0.127→0.006 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.600
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.376
- phase_breakdown.reach_object_score: 0.159
- phase_breakdown.lift_clearance_score: 0.017
- phase_breakdown.place_object_score: 0.677
- grasp_place_fitness: 0.996

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.996
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.295
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2697,"average_solve_count":330.0,"average_success_count":330.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14037,"approach_object.approach_arc_height":0.10502,"approach_object.approach_speed":0.0799,"descend_place.place_speed":0.05633,"descend_place.place_x_offset":0.00643,"descend_place.place_y_offset":-0.00094,"descend_to_grasp.descend_speed":0.06276,"descend_to_grasp.descend_x_offset":0.01796,"lift.lift_height":0.08594,"lift.lift_speed":0.05843,"pull_up.pull_up_speed":0.0359},"optimized_scores":{"best_composite_score":0.29503,"best_fitness_score":0.99503,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":323.0,"contact_point_centroid":[0.53029,-0.01784,-0.00141],"force_p95":0.42039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61037,"mean_force":0.10741,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53571,-0.01912,0.03012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14240.0,"contact_point_centroid":[0.53192,-0.0382,0.05081],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27507,"mean_force":0.04974,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53166,-0.01905,0.04895]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53697,-0.02098,-0.00224],"force_p95":0.18212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25627,"mean_force":0.14052,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53967,-0.01919,0.02921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14240.0,"contact_point_centroid":[0.53189,0.0001,0.05085],"force_p95":0.07333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24756,"mean_force":0.04886,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53166,-0.01905,0.04895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15312.0,"contact_point_centroid":[0.56376,0.12441,0.32871],"force_p95":0.0778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20225,"mean_force":0.04882,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56384,0.10538,0.32701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13187.0,"contact_point_centroid":[0.56441,0.08802,0.32962],"force_p95":0.08245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16439,"mean_force":0.05573,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56454,0.10725,0.32737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.60912,0.24138,0.29262],"force_p95":0.07435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.161,"mean_force":0.04872,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60886,0.22217,0.29028]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4617.0,"contact_point_centroid":[0.60874,0.20298,0.29338],"force_p95":0.075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14859,"mean_force":0.04991,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60885,0.22216,0.29058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4740.0,"contact_point_centroid":[0.53861,2e-05,0.02967],"force_p95":0.07618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1435,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53842,-0.01917,0.02774]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51436,0.01514,0.2425]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53716,-0.01156,0.11203]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16234.0,"contact_point_centroid":[0.52217,-0.03801,0.18834],"force_p95":0.07126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10093,"mean_force":0.04936,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52187,-0.01887,0.18653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16238.0,"contact_point_centroid":[0.52213,0.00026,0.18846],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09897,"mean_force":0.04912,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52187,-0.01887,0.18656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5081.0,"contact_point_centroid":[0.53866,-0.03851,0.02965],"force_p95":0.07704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08762,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53843,-0.01917,0.02776]}],"total_contact_groups":14},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61409,0.22441,0.20521],"final_tcp_position":[0.61229,0.22443,0.22653],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52992,-0.00403,0.18587],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.17027,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11621.0,"raw_peak_contact_force":0.25627,"subtask_id":"reach_object","tcp_end":[0.54732,-0.01923,0.03838],"tcp_start":[0.52992,-0.00403,0.18587],"tcp_to_object_dist_end":0.01622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53684,-0.01936,0.02513],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31573,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07167,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":28803.0,"raw_peak_contact_force":0.61037,"tcp_end":[0.53839,-0.01916,0.02771],"tcp_start":[0.54732,-0.01923,0.03838],"tcp_to_object_dist_end":0.00301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":712.0,"n_steps_budget":600.0,"object_pos_end":[0.53225,-0.01917,0.04519],"object_pos_start":[0.53684,-0.01936,0.02513],"object_to_goal_dist_end":0.30559,"object_to_goal_dist_start":0.31573,"object_z_max":0.0651,"peak_contact_force":0.06787,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":32472.0,"raw_peak_contact_force":0.10093,"tcp_end":[0.52859,-0.01899,0.07031],"tcp_start":[0.53339,-0.01908,0.04906],"tcp_to_object_dist_end":0.02539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":809.0,"n_steps_budget":930.0,"object_pos_end":[0.52389,-0.01896,0.13063],"object_pos_start":[0.52753,-0.01905,0.06514],"object_to_goal_dist_end":0.27245,"object_to_goal_dist_start":0.29666,"object_z_max":0.30004,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28499.0,"raw_peak_contact_force":0.20225,"subtask_id":"lift_clearance","tcp_end":[0.5193,-0.01883,0.30906],"tcp_start":[0.5215,-0.01886,0.22294],"tcp_to_object_dist_end":0.17849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.60535,0.21229,0.32377],"object_pos_start":[0.53057,-0.01885,0.3003],"object_to_goal_dist_end":0.11749,"object_to_goal_dist_start":0.27532,"object_z_max":0.32969,"peak_contact_force":0.07286,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9428.0,"raw_peak_contact_force":0.161,"subtask_id":"place_object","tcp_end":[0.60614,0.22031,0.35018],"tcp_start":[0.60599,0.21899,0.35018],"tcp_to_object_dist_end":0.02761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.61409,0.22441,0.20521],"object_pos_start":[0.60812,0.22045,0.32987],"object_to_goal_dist_end":0.0055,"object_to_goal_dist_start":0.12269,"object_z_max":0.32989,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.61229,0.22443,0.22653],"tcp_start":[0.60614,0.22031,0.35018],"tcp_to_object_dist_end":0.02139,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3605,"average_solve_count":319.0,"average_success_count":319.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.16885,"approach_object.approach_arc_height":0.10553,"approach_object.approach_speed":0.05488,"descend_place.place_speed":0.13193,"descend_place.place_x_offset":0.00309,"descend_place.place_y_offset":-0.00018,"descend_to_grasp.descend_speed":0.06314,"descend_to_grasp.descend_x_offset":0.01669,"lift.lift_height":0.11051,"lift.lift_speed":0.05093,"pull_up.pull_up_speed":0.04432},"optimized_scores":{"best_composite_score":0.29573,"best_fitness_score":0.99573,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.53864,-0.02532,-0.00144],"force_p95":0.41355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61397,"mean_force":0.10852,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.54281,-0.02666,0.03003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15160.0,"contact_point_centroid":[0.53902,-0.04569,0.0507],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27933,"mean_force":0.04971,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53876,-0.02654,0.04884]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02885,-0.00228],"force_p95":0.19247,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2691,"mean_force":0.14338,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54691,-0.02678,0.02909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8013.0,"contact_point_centroid":[0.58013,0.04693,0.35048],"force_p95":0.11761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24721,"mean_force":0.06968,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57773,0.06579,0.34941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15160.0,"contact_point_centroid":[0.53899,-0.00739,0.05076],"force_p95":0.07397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24375,"mean_force":0.04866,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53876,-0.02654,0.04884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3909.0,"contact_point_centroid":[0.62896,0.13932,0.25897],"force_p95":0.098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23412,"mean_force":0.05933,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62833,0.15857,0.25681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8675.0,"contact_point_centroid":[0.58296,0.08968,0.34893],"force_p95":0.10122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21939,"mean_force":0.0605,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58061,0.07107,0.34773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4239.0,"contact_point_centroid":[0.62863,0.177,0.26522],"force_p95":0.08576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20671,"mean_force":0.05152,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62803,0.15821,0.26339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4726.0,"contact_point_centroid":[0.54584,-0.00755,0.02952],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15786,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54564,-0.02674,0.02758]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51884,0.01322,0.23988]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54503,-0.01884,0.11101]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21189.0,"contact_point_centroid":[0.52998,-0.04541,0.22333],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11623,"mean_force":0.04954,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52961,-0.02627,0.22151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20883.0,"contact_point_centroid":[0.52998,-0.00714,0.22159],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1113,"mean_force":0.04987,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52963,-0.02627,0.21956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5117.0,"contact_point_centroid":[0.54588,-0.04613,0.02948],"force_p95":0.07879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0871,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54565,-0.02674,0.0276]}],"total_contact_groups":14},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62557,0.16161,0.1765],"final_tcp_position":[0.63126,0.162,0.19612],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.61397,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53835,-0.011,0.1835],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17908,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11643.0,"raw_peak_contact_force":0.2691,"subtask_id":"reach_object","tcp_end":[0.55464,-0.0269,0.03854],"tcp_start":[0.53835,-0.011,0.1835],"tcp_to_object_dist_end":0.01561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54542,-0.02696,0.02499],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2599,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.07175,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":30664.0,"raw_peak_contact_force":0.61397,"tcp_end":[0.54562,-0.02674,0.02755],"tcp_start":[0.55464,-0.0269,0.03854],"tcp_to_object_dist_end":0.00258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":758.0,"n_steps_budget":600.0,"object_pos_end":[0.54072,-0.0267,0.04507],"object_pos_start":[0.54542,-0.02696,0.02499],"object_to_goal_dist_end":0.25018,"object_to_goal_dist_start":0.2599,"object_z_max":0.06491,"peak_contact_force":0.08452,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":42072.0,"raw_peak_contact_force":0.11623,"tcp_end":[0.53571,-0.02644,0.07014],"tcp_start":[0.54056,-0.02659,0.04889],"tcp_to_object_dist_end":0.02557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1054.0,"n_steps_budget":1000.0,"object_pos_end":[0.53131,-0.02636,0.15465],"object_pos_start":[0.53584,-0.02651,0.06495],"object_to_goal_dist_end":0.21771,"object_to_goal_dist_start":0.24206,"object_z_max":0.37143,"peak_contact_force":0.11828,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16688.0,"raw_peak_contact_force":0.24721,"subtask_id":"lift_clearance","tcp_end":[0.52808,-0.02625,0.38272],"tcp_start":[0.52935,-0.02626,0.27192],"tcp_to_object_dist_end":0.22809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.62977,0.14784,0.30227],"object_pos_start":[0.54326,-0.0262,0.37167],"object_to_goal_dist_end":0.12655,"object_to_goal_dist_start":0.2872,"object_z_max":0.37193,"peak_contact_force":0.08844,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8148.0,"raw_peak_contact_force":0.23412,"subtask_id":"place_object","tcp_end":[0.62572,0.15515,0.32222],"tcp_start":[0.62514,0.15328,0.32293],"tcp_to_object_dist_end":0.02163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.62557,0.16161,0.1765],"object_pos_start":[0.6329,0.15499,0.30301],"object_to_goal_dist_end":0.00801,"object_to_goal_dist_start":0.12648,"object_z_max":0.30301,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.63126,0.162,0.19612],"tcp_start":[0.62572,0.15515,0.32222],"tcp_to_object_dist_end":0.02044,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26331,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.10671,"approach_object.approach_arc_height":0.09282,"approach_object.approach_speed":0.06098,"descend_place.place_speed":0.1004,"descend_place.place_x_offset":0.00425,"descend_place.place_y_offset":0.00276,"descend_to_grasp.descend_speed":0.04692,"descend_to_grasp.descend_x_offset":0.01365,"lift.lift_height":0.10284,"lift.lift_speed":0.05439,"pull_up.pull_up_speed":0.02546},"optimized_scores":{"best_composite_score":0.28974,"best_fitness_score":0.98974,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":223.0,"contact_point_centroid":[0.45754,0.0023,-0.0014],"force_p95":0.38778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52535,"mean_force":0.10557,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46121,0.00156,0.03361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8480.0,"contact_point_centroid":[0.52492,0.05338,0.31571],"force_p95":0.11669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32766,"mean_force":0.07176,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52194,0.0721,0.31488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8761.0,"contact_point_centroid":[0.52516,0.09096,0.31553],"force_p95":0.11321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32675,"mean_force":0.06807,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52215,0.0723,0.31475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9060.0,"contact_point_centroid":[0.45782,-0.01762,0.05389],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25442,"mean_force":0.05043,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45756,0.00152,0.05198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.60418,0.12948,0.20183],"force_p95":0.1056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24307,"mean_force":0.06266,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60312,0.14863,0.20008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9060.0,"contact_point_centroid":[0.45774,0.02067,0.05384],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24264,"mean_force":0.04983,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45756,0.00152,0.05198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4415.0,"contact_point_centroid":[0.60383,0.16736,0.20249],"force_p95":0.09388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2369,"mean_force":0.0553,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60303,0.14856,0.20117]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46282,0.00015,-0.00217],"force_p95":0.16664,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23502,"mean_force":0.13541,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46421,0.00161,0.03275]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48328,0.02624,0.24878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4774.0,"contact_point_centroid":[0.46326,0.02078,0.03356],"force_p95":0.0735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13669,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46311,0.00159,0.03167]},{"body_a":"world","body_b":"grasp_target","contact_count":1592.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46649,0.00942,0.11499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17839.0,"contact_point_centroid":[0.44924,-0.01769,0.21698],"force_p95":0.0725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11809,"mean_force":0.05002,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44885,0.00143,0.21509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17465.0,"contact_point_centroid":[0.44919,0.02058,0.21441],"force_p95":0.07251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11418,"mean_force":0.05076,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44889,0.00143,0.21244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.46336,-0.01769,0.0336],"force_p95":0.07405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08451,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46312,0.00159,0.03168]}],"total_contact_groups":14},"final_pose_error":0.01961,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60652,0.15197,0.12264],"final_tcp_position":[0.60791,0.15257,0.14044],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.52535,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1592.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46453,0.01696,0.18991],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.15879,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11599.0,"raw_peak_contact_force":0.23502,"subtask_id":"reach_object","tcp_end":[0.47098,0.00177,0.03958],"tcp_start":[0.46453,0.01696,0.18991],"tcp_to_object_dist_end":0.01591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,0.00135,0.02538],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23253,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07178,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18343.0,"raw_peak_contact_force":0.52535,"tcp_end":[0.46309,0.00159,0.03165],"tcp_start":[0.47098,0.00177,0.03958],"tcp_to_object_dist_end":0.00629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":453.0,"n_steps_budget":750.0,"object_pos_end":[0.45849,0.0014,0.04577],"object_pos_start":[0.46271,0.00135,0.02538],"object_to_goal_dist_end":0.22756,"object_to_goal_dist_start":0.23253,"object_z_max":0.06586,"peak_contact_force":0.09596,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":35304.0,"raw_peak_contact_force":0.11809,"tcp_end":[0.45449,0.00149,0.07369],"tcp_start":[0.45871,0.00154,0.05273],"tcp_to_object_dist_end":0.0282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.45121,0.00138,0.14831],"object_pos_start":[0.45413,0.00138,0.06594],"object_to_goal_dist_end":0.22112,"object_to_goal_dist_start":0.22462,"object_z_max":0.35023,"peak_contact_force":0.10923,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17241.0,"raw_peak_contact_force":0.32766,"subtask_id":"lift_clearance","tcp_end":[0.44698,0.00139,0.36309],"tcp_start":[0.44856,0.00143,0.26009],"tcp_to_object_dist_end":0.21483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.60612,0.13987,0.25411],"object_pos_start":[0.46229,0.00161,0.3505],"object_to_goal_dist_end":0.13262,"object_to_goal_dist_start":0.31124,"object_z_max":0.35072,"peak_contact_force":0.07211,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8581.0,"raw_peak_contact_force":0.24307,"subtask_id":"place_object","tcp_end":[0.59868,0.14457,0.26943],"tcp_start":[0.59754,0.14314,0.27028],"tcp_to_object_dist_end":0.01766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.60652,0.15197,0.12264],"object_pos_start":[0.60992,0.14441,0.25268],"object_to_goal_dist_end":0.00377,"object_to_goal_dist_start":0.13077,"object_z_max":0.25268,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.60791,0.15257,0.14044],"tcp_start":[0.59868,0.14457,0.26943],"tcp_to_object_dist_end":0.01786,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```