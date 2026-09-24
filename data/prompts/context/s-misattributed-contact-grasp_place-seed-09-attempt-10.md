## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2936 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0598 | 0.39 | ✅ accepted |
| 8 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0087 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0152 | 0.24 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.2526 | 0.17 | ✅ accepted |

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
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1188 |
| descend_to_grasp | 1.00 | 1.00 | 0.1500 |
| grasp | 1.00 | 1.00 | 0.0131 |
| pull_up | 1.00 | 1.00 | 0.0217 |
| lift | 1.00 | 1.00 | 0.0944 |
| approach_goal | 1.00 | 1.00 | 0.0016 |
| descend_place | 1.00 | 1.00 | 0.1273 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, -0.000, 0.188) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.512, -0.000, 0.188)→(0.524, -0.015, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 44.000 | 0.167 | 0.248 |
| grasp | grasp | 1.00 / step_budget | (0.524, -0.015, 0.039)→(0.515, -0.015, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 40.000 | 0.071 | 0.585 |
| pull_up | pull | 1.00 / step_budget | (0.510, -0.015, 0.050)→(0.506, -0.015, 0.072) | (0.515, -0.015, 0.025)→(0.510, -0.015, 0.045) | 0.269→0.261 | 1.00 / 27.333 | 0.100 | 0.135 |
| lift | lift | 1.00 / step_budget | (0.499, -0.015, 0.241)→(0.497, -0.015, 0.335) | (0.506, -0.015, 0.065)→(0.505, -0.015, 0.139) | 0.254→0.238 | 1.00 / 27.667 | 524.432 | 0.278 |
| approach_goal | approach | 1.00 / step_budget | (0.610, 0.173, 0.314)→(0.610, 0.174, 0.313) | (0.513, -0.014, 0.323)→(0.618, 0.168, 0.293) | 0.281→0.125 | 1.00 / 34.333 | 0.088 | 0.244 |
| descend_place | descend | 1.00 / step_budget | (0.610, 0.174, 0.313)→(0.616, 0.185, 0.187) | (0.621, 0.174, 0.296)→(0.621, 0.184, 0.168) | 0.128→0.013 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.258
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.374
- phase_breakdown.reach_object_score: 0.158
- phase_breakdown.lift_clearance_score: 0.111
- phase_breakdown.place_object_score: 0.617
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
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42229,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.10524,"approach_object.approach_arc_height":0.09966,"approach_object.approach_speed":0.07029,"descend_place.place_speed":0.04875,"descend_place.place_x_offset":0.00727,"descend_place.place_y_offset":-0.00947,"descend_to_grasp.descend_speed":0.0767,"descend_to_grasp.descend_x_offset":0.01683,"lift.lift_height":0.0936,"lift.lift_speed":0.0726,"pull_up.pull_up_speed":0.03321},"optimized_scores":{"best_composite_score":0.29516,"best_fitness_score":0.99516,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":318.0,"contact_point_centroid":[0.53032,-0.01784,-0.00143],"force_p95":0.41393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60597,"mean_force":0.10807,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53482,-0.01902,0.03033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14080.0,"contact_point_centroid":[0.53103,-0.0381,0.05103],"force_p95":0.07384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27576,"mean_force":0.04975,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53075,-0.01895,0.04917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53698,-0.02097,-0.00225],"force_p95":0.18529,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25888,"mean_force":0.14132,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53875,-0.01909,0.02944]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14080.0,"contact_point_centroid":[0.53096,0.0002,0.05107],"force_p95":0.07343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24636,"mean_force":0.04882,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53075,-0.01895,0.04917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9469.0,"contact_point_centroid":[0.57063,0.09423,0.33998],"force_p95":0.10785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24572,"mean_force":0.07546,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56647,0.11296,0.33899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9557.0,"contact_point_centroid":[0.57069,0.13049,0.33966],"force_p95":0.1037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23763,"mean_force":0.07515,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56606,0.11186,0.33889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2507.0,"contact_point_centroid":[0.61382,0.2001,0.29636],"force_p95":0.11608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23688,"mean_force":0.0836,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60872,0.21877,0.29547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2961.0,"contact_point_centroid":[0.61407,0.2373,0.29199],"force_p95":0.10352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2288,"mean_force":0.07353,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60892,0.21869,0.2919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4737.0,"contact_point_centroid":[0.53766,0.00012,0.0299],"force_p95":0.07667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16455,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53749,-0.01907,0.02798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17239.0,"contact_point_centroid":[0.52156,-0.03788,0.19911],"force_p95":0.07434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14297,"mean_force":0.0508,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52098,-0.01877,0.19733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16853.0,"contact_point_centroid":[0.52152,0.00036,0.19738],"force_p95":0.07724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13917,"mean_force":0.0515,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52104,-0.01877,0.19532]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51441,0.01647,0.24216]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53678,-0.01114,0.11186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5089.0,"contact_point_centroid":[0.53775,-0.03842,0.02988],"force_p95":0.07734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08581,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5375,-0.01907,0.02799]}],"total_contact_groups":14},"final_pose_error":0.0196,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62268,0.21716,0.20591],"final_tcp_position":[0.61291,0.2175,0.22643],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60597,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53008,-0.00333,0.18525],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1733,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11626.0,"raw_peak_contact_force":0.25888,"subtask_id":"reach_object","tcp_end":[0.54639,-0.01912,0.03859],"tcp_start":[0.53008,-0.00333,0.18525],"tcp_to_object_dist_end":0.01583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53684,-0.01927,0.02509],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31569,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07174,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":28478.0,"raw_peak_contact_force":0.60597,"tcp_end":[0.53747,-0.01906,0.02794],"tcp_start":[0.54639,-0.01912,0.03859],"tcp_to_object_dist_end":0.00293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":704.0,"n_steps_budget":600.0,"object_pos_end":[0.53221,-0.01908,0.04525],"object_pos_start":[0.53684,-0.01927,0.02509],"object_to_goal_dist_end":0.30549,"object_to_goal_dist_start":0.31569,"object_z_max":0.06516,"peak_contact_force":0.10652,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":34092.0,"raw_peak_contact_force":0.14297,"tcp_end":[0.52768,-0.01889,0.07053],"tcp_start":[0.53248,-0.01898,0.04929],"tcp_to_object_dist_end":0.02569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":868.0,"n_steps_budget":810.0,"object_pos_end":[0.52805,-0.01886,0.13851],"object_pos_start":[0.52742,-0.01895,0.0652],"object_to_goal_dist_end":0.26895,"object_to_goal_dist_start":0.29658,"object_z_max":0.32078,"peak_contact_force":0.10037,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19026.0,"raw_peak_contact_force":0.24572,"subtask_id":"lift_clearance","tcp_end":[0.51873,-0.01874,0.33238],"tcp_start":[0.52066,-0.01876,0.23859],"tcp_to_object_dist_end":0.19409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.61274,0.21149,0.32736],"object_pos_start":[0.53497,-0.01858,0.32103],"object_to_goal_dist_end":0.12107,"object_to_goal_dist_start":0.28154,"object_z_max":0.33197,"peak_contact_force":0.11176,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5468.0,"raw_peak_contact_force":0.23688,"subtask_id":"place_object","tcp_end":[0.60592,0.21974,0.35044],"tcp_start":[0.60573,0.21829,0.35053],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.62268,0.21716,0.20591],"object_pos_start":[0.61582,0.21974,0.33213],"object_to_goal_dist_end":0.01635,"object_to_goal_dist_start":0.1251,"object_z_max":0.33215,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.61291,0.2175,0.22643],"tcp_start":[0.60592,0.21974,0.35044],"tcp_to_object_dist_end":0.02273,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34211,"average_solve_count":342.0,"average_success_count":342.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06184,"approach_object.approach_arc_height":0.09268,"approach_object.approach_speed":0.1327,"descend_place.place_speed":0.08508,"descend_place.place_x_offset":-0.00491,"descend_place.place_y_offset":0.01962,"descend_to_grasp.descend_speed":0.04512,"descend_to_grasp.descend_x_offset":0.01668,"lift.lift_height":0.07894,"lift.lift_speed":0.09517,"pull_up.pull_up_speed":0.04177},"optimized_scores":{"best_composite_score":0.29597,"best_fitness_score":0.99597,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":346.0,"contact_point_centroid":[0.53865,-0.02519,-0.00144],"force_p95":0.4162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61669,"mean_force":0.10857,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.54282,-0.02661,0.02988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15180.0,"contact_point_centroid":[0.53904,-0.04564,0.05056],"force_p95":0.07431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27981,"mean_force":0.04972,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53877,-0.02649,0.0487]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02884,-0.00229],"force_p95":0.19369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27046,"mean_force":0.14375,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54693,-0.02673,0.02893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10464.0,"contact_point_centroid":[0.57824,0.08414,0.30091],"force_p95":0.10293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25437,"mean_force":0.06629,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57547,0.06543,0.30006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10257.0,"contact_point_centroid":[0.57894,0.04743,0.30079],"force_p95":0.10114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24484,"mean_force":0.0686,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57586,0.06613,0.30021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3967.0,"contact_point_centroid":[0.62726,0.18731,0.25426],"force_p95":0.09654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24472,"mean_force":0.06012,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62582,0.16857,0.2536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15180.0,"contact_point_centroid":[0.539,-0.00735,0.05062],"force_p95":0.07405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24345,"mean_force":0.04865,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53877,-0.02649,0.0487]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3716.0,"contact_point_centroid":[0.62741,0.14961,0.25421],"force_p95":0.10428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22053,"mean_force":0.0672,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62582,0.16867,0.25302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4723.0,"contact_point_centroid":[0.54585,-0.00751,0.02935],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15501,"mean_force":0.04508,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54566,-0.0267,0.02742]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51946,0.01617,0.23871]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54522,-0.01859,0.11048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14426.0,"contact_point_centroid":[0.52904,-0.00704,0.17764],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10278,"mean_force":0.05086,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52867,-0.02618,0.17555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14840.0,"contact_point_centroid":[0.52898,-0.04531,0.17981],"force_p95":0.07271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10216,"mean_force":0.04997,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52858,-0.02617,0.17801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5121.0,"contact_point_centroid":[0.5459,-0.04608,0.02932],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08841,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54568,-0.0267,0.02743]}],"total_contact_groups":14},"final_pose_error":0.01949,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62588,0.17791,0.17862],"final_tcp_position":[0.62498,0.17853,0.19522],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53884,-0.01059,0.1823],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17997,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11644.0,"raw_peak_contact_force":0.27046,"subtask_id":"reach_object","tcp_end":[0.55466,-0.02686,0.03835],"tcp_start":[0.53884,-0.01059,0.1823],"tcp_to_object_dist_end":0.01549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54541,-0.02691,0.02497],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25988,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.0718,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":30706.0,"raw_peak_contact_force":0.61669,"tcp_end":[0.54564,-0.02669,0.02738],"tcp_start":[0.55466,-0.02686,0.03835],"tcp_to_object_dist_end":0.00244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":759.0,"n_steps_budget":600.0,"object_pos_end":[0.54071,-0.02665,0.04506],"object_pos_start":[0.54541,-0.02691,0.02497],"object_to_goal_dist_end":0.25016,"object_to_goal_dist_start":0.25988,"object_z_max":0.06493,"peak_contact_force":0.08702,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":29266.0,"raw_peak_contact_force":0.10278,"tcp_end":[0.53573,-0.0264,0.07002],"tcp_start":[0.54058,-0.02654,0.04872],"tcp_to_object_dist_end":0.02546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":735.0,"n_steps_budget":600.0,"object_pos_end":[0.53592,-0.02632,0.12368],"object_pos_start":[0.53584,-0.02646,0.06497],"object_to_goal_dist_end":0.22092,"object_to_goal_dist_start":0.24202,"object_z_max":0.2781,"peak_contact_force":1573.09317,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20721.0,"raw_peak_contact_force":0.25437,"subtask_id":"lift_clearance","tcp_end":[0.5258,-0.0261,0.28798],"tcp_start":[0.52827,-0.02616,0.20871],"tcp_to_object_dist_end":0.16462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.63565,0.15119,0.29871],"object_pos_start":[0.54057,-0.02597,0.27836],"object_to_goal_dist_end":0.12259,"object_to_goal_dist_start":0.23505,"object_z_max":0.30392,"peak_contact_force":0.07207,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7683.0,"raw_peak_contact_force":0.24472,"subtask_id":"place_object","tcp_end":[0.62715,0.15842,0.31947],"tcp_start":[0.62693,0.15727,0.31947],"tcp_to_object_dist_end":0.02357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.62588,0.17791,0.17862],"object_pos_start":[0.63959,0.15867,0.30407],"object_to_goal_dist_end":0.01483,"object_to_goal_dist_start":0.12748,"object_z_max":0.30409,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.62498,0.17853,0.19522],"tcp_start":[0.62715,0.15842,0.31947],"tcp_to_object_dist_end":0.01663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29023,"average_solve_count":348.0,"average_success_count":348.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09255,"approach_object.approach_arc_height":0.14068,"approach_object.approach_speed":0.1135,"descend_place.place_speed":0.07892,"descend_place.place_x_offset":0.00727,"descend_place.place_y_offset":0.01036,"descend_to_grasp.descend_speed":0.0571,"descend_to_grasp.descend_x_offset":0.01285,"lift.lift_height":0.10984,"lift.lift_speed":0.04741,"pull_up.pull_up_speed":0.03269},"optimized_scores":{"best_composite_score":0.28964,"best_fitness_score":0.98964,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.45755,0.00164,-0.00133],"force_p95":0.43456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53241,"mean_force":0.10444,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.461,0.00107,0.03379]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7039.0,"contact_point_centroid":[0.53306,0.09678,0.32244],"force_p95":0.12842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33247,"mean_force":0.08464,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52871,0.07809,0.32136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7743.0,"contact_point_centroid":[0.53449,0.0607,0.32145],"force_p95":0.12435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33028,"mean_force":0.07742,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52992,0.07922,0.32049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8660.0,"contact_point_centroid":[0.45742,-0.01812,0.05461],"force_p95":0.07201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25848,"mean_force":0.0503,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45717,0.00103,0.0527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8660.0,"contact_point_centroid":[0.45737,0.02017,0.05457],"force_p95":0.07183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25328,"mean_force":0.04993,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45717,0.00103,0.0527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3903.0,"contact_point_centroid":[0.60611,0.13253,0.20177],"force_p95":0.11467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25026,"mean_force":0.07062,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60407,0.15155,0.20084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4004.0,"contact_point_centroid":[0.60593,0.17009,0.20268],"force_p95":0.10559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24028,"mean_force":0.06576,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60388,0.15134,0.20259]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,0.0001,-0.00212],"force_p95":0.1532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21543,"mean_force":0.13155,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46386,0.00111,0.03302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18746.0,"contact_point_centroid":[0.44927,-0.01816,0.22451],"force_p95":0.07428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15827,"mean_force":0.05089,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44872,0.00094,0.22264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18346.0,"contact_point_centroid":[0.44922,0.02008,0.22211],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15482,"mean_force":0.05168,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44877,0.00094,0.22011]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.46286,-7e-05,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48391,0.01719,0.25014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4797.0,"contact_point_centroid":[0.46292,0.02028,0.03383],"force_p95":0.07147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12505,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46276,0.00109,0.03194]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46724,0.0069,0.1174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.46298,-0.01815,0.03386],"force_p95":0.07191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08218,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46276,0.00109,0.03195]}],"total_contact_groups":14},"final_pose_error":0.01959,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.61301,0.15839,0.12018],"final_tcp_position":[0.61038,0.15875,0.13992],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.53241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46645,0.0125,0.19513],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.14814,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11569.0,"raw_peak_contact_force":0.21543,"subtask_id":"reach_object","tcp_end":[0.47063,0.00125,0.03985],"tcp_start":[0.46645,0.0125,0.19513],"tcp_to_object_dist_end":0.01592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46272,0.00093,0.02557],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23272,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07078,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17516.0,"raw_peak_contact_force":0.53241,"tcp_end":[0.46273,0.00109,0.03191],"tcp_start":[0.47063,0.00125,0.03985],"tcp_to_object_dist_end":0.00635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.45843,0.00094,0.04602],"object_pos_start":[0.46272,0.00093,0.02557],"object_to_goal_dist_end":0.22782,"object_to_goal_dist_start":0.23272,"object_z_max":0.06615,"peak_contact_force":0.10629,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":37092.0,"raw_peak_contact_force":0.15827,"tcp_end":[0.45417,0.001,0.07398],"tcp_start":[0.45838,0.00104,0.05297],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.45074,0.00091,0.15565],"object_pos_start":[0.4541,0.00092,0.06623],"object_to_goal_dist_end":0.22276,"object_to_goal_dist_start":0.22488,"object_z_max":0.37069,"peak_contact_force":0.10224,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14782.0,"raw_peak_contact_force":0.33247,"subtask_id":"lift_clearance","tcp_end":[0.44708,0.00091,0.38464],"tcp_start":[0.44843,0.00094,0.27458],"tcp_to_object_dist_end":0.22901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.60539,0.14028,0.25388],"object_pos_start":[0.46373,0.00109,0.37096],"object_to_goal_dist_end":0.13238,"object_to_goal_dist_start":0.32613,"object_z_max":0.37114,"peak_contact_force":0.07911,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7907.0,"raw_peak_contact_force":0.25026,"subtask_id":"place_object","tcp_end":[0.59825,0.14414,0.27025],"tcp_start":[0.59701,0.14265,0.27131],"tcp_to_object_dist_end":0.01827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.61301,0.15839,0.12018],"object_pos_start":[0.60864,0.14399,0.25184],"object_to_goal_dist_end":0.00654,"object_to_goal_dist_start":0.12996,"object_z_max":0.25184,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.61038,0.15875,0.13992],"tcp_start":[0.59825,0.14414,0.27025],"tcp_to_object_dist_end":0.01991,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```