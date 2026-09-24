## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2928 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2936 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0598 | 0.39 | ✅ accepted |
| 8 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0087 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0152 | 0.24 | ✅ accepted |

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

## Current Skill (Q=0.293) — your mutation base

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

- **Composite score**: 0.293
- **task_score** (E): 1.000
- **fitness_score**: 0.993  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1178 |
| descend_to_grasp | 1.00 | 1.00 | 0.1514 |
| grasp | 1.00 | 1.00 | 0.0131 |
| pull_up | 1.00 | 1.00 | 0.0217 |
| lift | 1.00 | 1.00 | 0.1112 |
| approach_goal | 1.00 | 1.00 | 0.0020 |
| descend_place | 1.00 | 1.00 | 0.1277 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.000, 0.189) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.000, 0.189)→(0.525, -0.015, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 44.000 | 0.166 | 0.249 |
| grasp | grasp | 1.00 / step_budget | (0.525, -0.015, 0.039)→(0.517, -0.015, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 40.000 | 0.072 | 0.589 |
| pull_up | pull | 1.00 / step_budget | (0.512, -0.015, 0.050)→(0.507, -0.015, 0.071) | (0.515, -0.015, 0.025)→(0.511, -0.015, 0.045) | 0.269→0.261 | 1.00 / 27.000 | 0.103 | 0.149 |
| lift | lift | 1.00 / step_budget | (0.501, -0.015, 0.274)→(0.500, -0.015, 0.385) | (0.506, -0.015, 0.065)→(0.504, -0.015, 0.155) | 0.254→0.236 | 1.00 / 36.333 | 0.053 | 0.249 |
| approach_goal | approach | 1.00 / step_budget | (0.609, 0.171, 0.316)→(0.610, 0.173, 0.315) | (0.516, -0.015, 0.372)→(0.614, 0.167, 0.296) | 0.308→0.128 | 1.00 / 34.000 | 0.101 | 0.197 |
| descend_place | descend | 1.00 / step_budget | (0.610, 0.173, 0.315)→(0.612, 0.182, 0.188) | (0.616, 0.173, 0.297)→(0.613, 0.182, 0.168) | 0.128→0.008 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.468
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.383
- phase_breakdown.reach_object_score: 0.159
- phase_breakdown.lift_clearance_score: 0.049
- phase_breakdown.place_object_score: 0.674
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
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21607,"average_solve_count":361.0,"average_success_count":361.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.11491,"approach_object.approach_arc_height":0.11601,"approach_object.approach_speed":0.10816,"descend_place.place_speed":0.04948,"descend_place.place_x_offset":-0.00501,"descend_place.place_y_offset":0.00561,"descend_to_grasp.descend_speed":0.05296,"descend_to_grasp.descend_x_offset":0.01597,"lift.lift_height":0.11411,"lift.lift_speed":0.05252,"pull_up.pull_up_speed":0.04465},"optimized_scores":{"best_composite_score":0.29535,"best_fitness_score":0.99535,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":309.0,"contact_point_centroid":[0.53039,-0.01803,-0.00141],"force_p95":0.41361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60133,"mean_force":0.10828,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53402,-0.01919,0.03026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14000.0,"contact_point_centroid":[0.5302,-0.03826,0.05105],"force_p95":0.07335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27379,"mean_force":0.04969,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52992,-0.01911,0.04919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7750.0,"contact_point_centroid":[0.57005,0.08814,0.36987],"force_p95":0.11957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25931,"mean_force":0.0827,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56502,0.10688,0.36851]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53699,-0.02099,-0.00223],"force_p95":0.18081,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25532,"mean_force":0.13995,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5379,-0.01925,0.02945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14000.0,"contact_point_centroid":[0.53013,3e-05,0.05109],"force_p95":0.07307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24658,"mean_force":0.04883,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52992,-0.01911,0.04919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8709.0,"contact_point_centroid":[0.57098,0.12804,0.3689],"force_p95":0.10798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23849,"mean_force":0.07555,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56597,0.10947,0.36807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2333.0,"contact_point_centroid":[0.60893,0.20396,0.29591],"force_p95":0.14033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22746,"mean_force":0.09132,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60424,0.2226,0.29678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.60908,0.24124,0.29445],"force_p95":0.11293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20374,"mean_force":0.07873,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6042,0.22276,0.29503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20253.0,"contact_point_centroid":[0.5216,0.00016,0.22128],"force_p95":0.07799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16142,"mean_force":0.0518,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52103,-0.01895,0.21925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20612.0,"contact_point_centroid":[0.52165,-0.03806,0.22298],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15897,"mean_force":0.05131,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52099,-0.01895,0.22119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4744.0,"contact_point_centroid":[0.53683,-5e-05,0.02991],"force_p95":0.07588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14843,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53665,-0.01923,0.02799]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51416,0.0129,0.24339]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53603,-0.01188,0.113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5072.0,"contact_point_centroid":[0.53691,-0.03857,0.02989],"force_p95":0.07648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0862,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53666,-0.01923,0.028]}],"total_contact_groups":14},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6126,0.22918,0.20637],"final_tcp_position":[0.60298,0.22921,0.22676],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60133,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52952,-0.0046,0.1876],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.17007,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11616.0,"raw_peak_contact_force":0.25532,"subtask_id":"reach_object","tcp_end":[0.54552,-0.0193,0.03856],"tcp_start":[0.52952,-0.0046,0.1876],"tcp_to_object_dist_end":0.01529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53685,-0.01942,0.02516],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31577,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07152,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":28309.0,"raw_peak_contact_force":0.60133,"tcp_end":[0.53662,-0.01923,0.02796],"tcp_start":[0.54552,-0.0193,0.03856],"tcp_to_object_dist_end":0.00282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":700.0,"n_steps_budget":600.0,"object_pos_end":[0.53216,-0.01924,0.04539],"object_pos_start":[0.53685,-0.01942,0.02516],"object_to_goal_dist_end":0.30556,"object_to_goal_dist_start":0.31577,"object_z_max":0.0653,"peak_contact_force":0.10718,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":40865.0,"raw_peak_contact_force":0.16142,"tcp_end":[0.52685,-0.01905,0.07056],"tcp_start":[0.53164,-0.01914,0.04933],"tcp_to_object_dist_end":0.02573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1059.0,"n_steps_budget":1000.0,"object_pos_end":[0.52409,-0.01901,0.15884],"object_pos_start":[0.5273,-0.01911,0.06535],"object_to_goal_dist_end":0.26587,"object_to_goal_dist_start":0.29667,"object_z_max":0.3813,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16459.0,"raw_peak_contact_force":0.25931,"subtask_id":"lift_clearance","tcp_end":[0.51956,-0.01896,0.39395],"tcp_start":[0.52068,-0.01894,0.27955],"tcp_to_object_dist_end":0.23516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.61342,0.21006,0.33209],"object_pos_start":[0.53658,-0.01891,0.38155],"object_to_goal_dist_end":0.12596,"object_to_goal_dist_start":0.31081,"object_z_max":0.38177,"peak_contact_force":0.15407,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5121.0,"raw_peak_contact_force":0.22746,"subtask_id":"place_object","tcp_end":[0.60539,0.21794,0.35167],"tcp_start":[0.60507,0.2161,0.35207],"tcp_to_object_dist_end":0.02259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.6126,0.22918,0.20637],"object_pos_start":[0.61606,0.21789,0.33451],"object_to_goal_dist_end":0.00288,"object_to_goal_dist_start":0.12761,"object_z_max":0.33451,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.60298,0.22921,0.22676],"tcp_start":[0.60539,0.21794,0.35167],"tcp_to_object_dist_end":0.02254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38318,"average_solve_count":321.0,"average_success_count":321.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.12763,"approach_object.approach_arc_height":0.14979,"approach_object.approach_speed":0.06878,"descend_place.place_speed":0.07822,"descend_place.place_x_offset":-0.00038,"descend_place.place_y_offset":0.00943,"descend_to_grasp.descend_speed":0.06985,"descend_to_grasp.descend_x_offset":0.01625,"lift.lift_height":0.09274,"lift.lift_speed":0.05175,"pull_up.pull_up_speed":0.04215},"optimized_scores":{"best_composite_score":0.29606,"best_fitness_score":0.99606,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":331.0,"contact_point_centroid":[0.53863,-0.02577,-0.00141],"force_p95":0.4168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60903,"mean_force":0.10836,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.54243,-0.027,0.02985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15120.0,"contact_point_centroid":[0.53858,-0.04602,0.05065],"force_p95":0.07336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27607,"mean_force":0.04961,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53832,-0.02687,0.0488]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02888,-0.00224],"force_p95":0.18259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25773,"mean_force":0.14056,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54647,-0.02711,0.02904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15120.0,"contact_point_centroid":[0.53855,-0.00773,0.05072],"force_p95":0.07318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24492,"mean_force":0.0487,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53832,-0.02687,0.0488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11674.0,"contact_point_centroid":[0.58089,0.09152,0.32357],"force_p95":0.07889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18429,"mean_force":0.0506,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58023,0.07254,0.32172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4382.0,"contact_point_centroid":[0.62745,0.1818,0.26292],"force_p95":0.08443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18042,"mean_force":0.05527,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62716,0.16279,0.26106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4145.0,"contact_point_centroid":[0.62731,0.14384,0.2601],"force_p95":0.08604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15961,"mean_force":0.05761,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62721,0.16309,0.25808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9791.0,"contact_point_centroid":[0.58038,0.05181,0.32423],"force_p95":0.08535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15153,"mean_force":0.05924,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57938,0.071,0.32178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4739.0,"contact_point_centroid":[0.54539,-0.00789,0.02946],"force_p95":0.07631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14331,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5452,-0.02708,0.02753]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51789,0.00596,0.24291]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54405,-0.02026,0.11303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17877.0,"contact_point_centroid":[0.52895,-0.04573,0.19857],"force_p95":0.07102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09853,"mean_force":0.04915,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52868,-0.02657,0.19676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17794.0,"contact_point_centroid":[0.52894,-0.00744,0.19815],"force_p95":0.07061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09655,"mean_force":0.0491,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52869,-0.02657,0.19617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5081.0,"contact_point_centroid":[0.54543,-0.04642,0.02942],"force_p95":0.07706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0882,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54521,-0.02708,0.02754]}],"total_contact_groups":14},"final_pose_error":0.01949,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62334,0.1695,0.17834],"final_tcp_position":[0.62854,0.17004,0.19552],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.60903,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53687,-0.0134,0.188],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17141,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11620.0,"raw_peak_contact_force":0.25773,"subtask_id":"reach_object","tcp_end":[0.55419,-0.02725,0.03846],"tcp_start":[0.53687,-0.0134,0.188],"tcp_to_object_dist_end":0.01525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54542,-0.02726,0.02513],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26003,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.07137,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":30571.0,"raw_peak_contact_force":0.60903,"tcp_end":[0.54517,-0.02707,0.02749],"tcp_start":[0.55419,-0.02725,0.03846],"tcp_to_object_dist_end":0.00239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":756.0,"n_steps_budget":600.0,"object_pos_end":[0.54068,-0.02701,0.04525],"object_pos_start":[0.54542,-0.02726,0.02513],"object_to_goal_dist_end":0.25034,"object_to_goal_dist_start":0.26003,"object_z_max":0.06512,"peak_contact_force":0.07977,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":35671.0,"raw_peak_contact_force":0.09853,"tcp_end":[0.53528,-0.02678,0.07013],"tcp_start":[0.54012,-0.02692,0.04884],"tcp_to_object_dist_end":0.02547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.53097,-0.02668,0.13752],"object_pos_start":[0.53578,-0.02683,0.06515],"object_to_goal_dist_end":0.22055,"object_to_goal_dist_start":0.24225,"object_z_max":0.32019,"peak_contact_force":0.08477,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21465.0,"raw_peak_contact_force":0.18429,"subtask_id":"lift_clearance","tcp_end":[0.5264,-0.02652,0.3298],"tcp_start":[0.52835,-0.02656,0.23671],"tcp_to_object_dist_end":0.19233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.62838,0.14941,0.30039],"object_pos_start":[0.53894,-0.02645,0.32044],"object_to_goal_dist_end":0.12452,"object_to_goal_dist_start":0.25699,"object_z_max":0.32065,"peak_contact_force":0.07881,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8527.0,"raw_peak_contact_force":0.18042,"subtask_id":"place_object","tcp_end":[0.62639,0.15683,0.32049],"tcp_start":[0.626,0.15533,0.32077],"tcp_to_object_dist_end":0.02152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.62334,0.1695,0.17834],"object_pos_start":[0.63221,0.15694,0.30371],"object_to_goal_dist_end":0.01064,"object_to_goal_dist_start":0.12705,"object_z_max":0.30373,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.62854,0.17004,0.19552],"tcp_start":[0.62639,0.15683,0.32049],"tcp_to_object_dist_end":0.01796,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46789,"average_solve_count":327.0,"average_success_count":327.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.15109,"approach_object.approach_arc_height":0.09547,"approach_object.approach_speed":0.10277,"descend_place.place_speed":0.06991,"descend_place.place_x_offset":-4e-05,"descend_place.place_y_offset":-0.00294,"descend_to_grasp.descend_speed":0.0617,"descend_to_grasp.descend_x_offset":0.01927,"lift.lift_height":0.12597,"lift.lift_speed":0.05922,"pull_up.pull_up_speed":0.03316},"optimized_scores":{"best_composite_score":0.28694,"best_fitness_score":0.98694,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.45752,0.00221,-0.0014],"force_p95":0.42756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55783,"mean_force":0.10264,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46621,0.00151,0.03349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9111.0,"contact_point_centroid":[0.54155,0.06591,0.33925],"force_p95":0.11725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30428,"mean_force":0.06793,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53881,0.08493,0.33723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9655.0,"contact_point_centroid":[0.54023,0.10312,0.33929],"force_p95":0.11016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29278,"mean_force":0.06113,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53816,0.08429,0.33793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8880.0,"contact_point_centroid":[0.46271,-0.01768,0.05407],"force_p95":0.07352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26555,"mean_force":0.05093,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46245,0.00146,0.05216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8880.0,"contact_point_centroid":[0.46265,0.02061,0.05402],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25561,"mean_force":0.05034,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46245,0.00146,0.05216]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46279,0.00015,-0.00217],"force_p95":0.16486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23532,"mean_force":0.13516,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46924,0.00155,0.03247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19712.0,"contact_point_centroid":[0.45502,0.02048,0.23539],"force_p95":0.08851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18828,"mean_force":0.05466,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45424,0.00137,0.23339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20078.0,"contact_point_centroid":[0.45509,-0.0177,0.23748],"force_p95":0.08723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18666,"mean_force":0.05412,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45421,0.00137,0.23559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4919.0,"contact_point_centroid":[0.60109,0.1647,0.21084],"force_p95":0.08298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18261,"mean_force":0.05397,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60051,0.14549,0.20871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5233.0,"contact_point_centroid":[0.60138,0.12636,0.20898],"force_p95":0.08265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17003,"mean_force":0.05113,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60059,0.14555,0.20681]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.46286,-7e-05,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48347,0.02549,0.24889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4775.0,"contact_point_centroid":[0.46829,0.02073,0.03325],"force_p95":0.07345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13525,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46813,0.00154,0.03137]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46913,0.00921,0.11514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5023.0,"contact_point_centroid":[0.46836,-0.01774,0.0333],"force_p95":0.07415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08399,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46813,0.00154,0.03138]}],"total_contact_groups":14},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60183,0.14737,0.11929],"final_tcp_position":[0.60436,0.14779,0.14073],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.55783,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4649,0.01663,0.19073],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.15714,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11598.0,"raw_peak_contact_force":0.23532,"subtask_id":"reach_object","tcp_end":[0.47607,0.00172,0.03946],"tcp_start":[0.4649,0.01663,0.19073],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46268,0.00131,0.0254],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23257,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07273,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17980.0,"raw_peak_contact_force":0.55783,"tcp_end":[0.4681,0.00154,0.03134],"tcp_start":[0.47607,0.00172,0.03946],"tcp_to_object_dist_end":0.00805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.45872,0.00134,0.04531],"object_pos_start":[0.46268,0.00131,0.0254],"object_to_goal_dist_end":0.2276,"object_to_goal_dist_start":0.23257,"object_z_max":0.06523,"peak_contact_force":0.12132,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":39790.0,"raw_peak_contact_force":0.18828,"tcp_end":[0.45944,0.00143,0.0734],"tcp_start":[0.4637,0.00148,0.05237],"tcp_to_object_dist_end":0.0281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1064.0,"n_steps_budget":1000.0,"object_pos_end":[0.45582,0.00134,0.17007],"object_pos_start":[0.45476,0.00132,0.06531],"object_to_goal_dist_end":0.22152,"object_to_goal_dist_start":0.22438,"object_z_max":0.41314,"peak_contact_force":0.0755,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18766.0,"raw_peak_contact_force":0.30428,"subtask_id":"lift_clearance","tcp_end":[0.45308,0.00133,0.43212],"tcp_start":[0.45382,0.00137,0.30607],"tcp_to_object_dist_end":0.26207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.59886,0.14017,0.2547],"object_pos_start":[0.47271,0.00143,0.41341],"object_to_goal_dist_end":0.13359,"object_to_goal_dist_start":0.35585,"object_z_max":0.41357,"peak_contact_force":0.07148,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10152.0,"raw_peak_contact_force":0.18261,"subtask_id":"place_object","tcp_end":[0.59811,0.14369,0.27245],"tcp_start":[0.59689,0.14222,0.27405],"tcp_to_object_dist_end":0.01812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.60183,0.14737,0.11929],"object_pos_start":[0.60096,0.14358,0.25175],"object_to_goal_dist_end":0.01039,"object_to_goal_dist_start":0.13022,"object_z_max":0.25175,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.60436,0.14779,0.14073],"tcp_start":[0.59811,0.14369,0.27245],"tcp_to_object_dist_end":0.02159,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```