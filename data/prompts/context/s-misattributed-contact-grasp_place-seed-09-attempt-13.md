## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2045 | 0.83 | ❌ rejected |
| 12 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2935 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2928 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2936 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0598 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.204) — your mutation base

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

- **Composite score**: 0.204
- **task_score** (E): 0.829
- **fitness_score**: 0.904  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1207 |
| descend_to_grasp | 1.00 | 1.00 | 0.1493 |
| grasp | 1.00 | 1.00 | 0.0132 |
| pull_up | 1.00 | 1.00 | 0.0217 |
| lift | 1.00 | 1.00 | 0.1170 |
| approach_goal | 1.00 | 1.00 | 0.0021 |
| descend_place | 1.00 | 1.00 | 0.1289 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.001, 0.186) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.001, 0.186)→(0.528, -0.015, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 42.667 | 0.171 | 0.256 |
| grasp | grasp | 1.00 / step_budget | (0.528, -0.015, 0.039)→(0.519, -0.015, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 41.000 | 0.072 | 0.594 |
| pull_up | pull | 1.00 / step_budget | (0.514, -0.015, 0.050)→(0.510, -0.015, 0.071) | (0.515, -0.015, 0.025)→(0.511, -0.015, 0.045) | 0.269→0.261 | 1.00 / 27.333 | 0.105 | 0.163 |
| lift | lift | 1.00 / step_budget | (0.503, -0.015, 0.285)→(0.502, -0.015, 0.402) | (0.506, -0.015, 0.064)→(0.504, -0.015, 0.160) | 0.254→0.237 | 1.00 / 22.000 | 90995.467 | 0.888 |
| approach_goal | approach | 1.00 / step_budget | (0.609, 0.171, 0.317)→(0.610, 0.173, 0.316) | (0.519, -0.014, 0.386)→(0.609, 0.156, 0.218) | 0.319→0.119 | 1.00 / 20.000 | 3249.736 | 0.219 |
| descend_place | descend | 1.00 / step_budget | (0.610, 0.173, 0.316)→(0.618, 0.181, 0.187) | (0.609, 0.163, 0.220)→(0.610, 0.168, 0.135) | 0.119→0.040 | 1.00 / 4.000 | 13.063 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.698
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.381
- phase_breakdown.reach_object_score: 0.158
- phase_breakdown.lift_clearance_score: 0.025
- phase_breakdown.place_object_score: 0.684
- grasp_place_fitness: 0.996

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.996
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.295
- **K-run variance**: 0.0166
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06733,"average_solve_count":401.0,"average_success_count":401.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14708,"approach_object.approach_arc_height":0.09941,"approach_object.approach_speed":0.10394,"descend_place.place_speed":0.02845,"descend_place.place_x_offset":-0.00275,"descend_place.place_y_offset":0.00189,"descend_to_grasp.descend_speed":0.09662,"descend_to_grasp.descend_x_offset":0.01549,"lift.lift_height":0.10438,"lift.lift_speed":0.02647,"pull_up.pull_up_speed":0.03764},"optimized_scores":{"best_composite_score":0.29525,"best_fitness_score":0.99525,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":310.0,"contact_point_centroid":[0.53035,-0.01777,-0.00142],"force_p95":0.41308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60237,"mean_force":0.10863,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53363,-0.01904,0.03024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13960.0,"contact_point_centroid":[0.52983,-0.03811,0.05099],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27456,"mean_force":0.04972,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52956,-0.01896,0.04912]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53699,-0.02097,-0.00225],"force_p95":0.18436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25916,"mean_force":0.14095,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53752,-0.01911,0.02941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13960.0,"contact_point_centroid":[0.52977,0.00018,0.05103],"force_p95":0.07334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24584,"mean_force":0.04881,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52956,-0.01896,0.04912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9467.0,"contact_point_centroid":[0.56443,0.08032,0.35573],"force_p95":0.11498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24121,"mean_force":0.07192,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5615,0.09915,0.35484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.60959,0.20319,0.29558],"force_p95":0.11558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22442,"mean_force":0.08812,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60508,0.22194,0.29438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10297.0,"contact_point_centroid":[0.56683,0.12437,0.35527],"force_p95":0.10142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21772,"mean_force":0.0645,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56397,0.10576,0.35453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3189.0,"contact_point_centroid":[0.6088,0.24042,0.29523],"force_p95":0.09983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21228,"mean_force":0.06915,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60508,0.22188,0.29527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4737.0,"contact_point_centroid":[0.53644,0.0001,0.02987],"force_p95":0.07649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1441,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53627,-0.01909,0.02795]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51446,0.01643,0.24215]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53631,-0.0112,0.11192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20105.0,"contact_point_centroid":[0.52066,-0.03793,0.21287],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11238,"mean_force":0.04934,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52027,-0.0188,0.21104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19784.0,"contact_point_centroid":[0.52063,0.00034,0.21096],"force_p95":0.07121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10604,"mean_force":0.04974,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52031,-0.0188,0.20895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5088.0,"contact_point_centroid":[0.53652,-0.03844,0.02986],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08555,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53628,-0.01909,0.02796]}],"total_contact_groups":14},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61308,0.22641,0.20333],"final_tcp_position":[0.60483,0.22636,0.22679],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60237,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53006,-0.00342,0.18547],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.17308,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11625.0,"raw_peak_contact_force":0.25916,"subtask_id":"reach_object","tcp_end":[0.54515,-0.01914,0.03851],"tcp_start":[0.53006,-0.00342,0.18547],"tcp_to_object_dist_end":0.01506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53685,-0.01929,0.02511],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31569,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07175,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":28230.0,"raw_peak_contact_force":0.60237,"tcp_end":[0.53624,-0.01908,0.02792],"tcp_start":[0.54515,-0.01914,0.03851],"tcp_to_object_dist_end":0.00288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":698.0,"n_steps_budget":600.0,"object_pos_end":[0.53214,-0.0191,0.04537],"object_pos_start":[0.53685,-0.01929,0.02511],"object_to_goal_dist_end":0.30546,"object_to_goal_dist_start":0.31569,"object_z_max":0.06529,"peak_contact_force":0.08524,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":39889.0,"raw_peak_contact_force":0.11238,"tcp_end":[0.52648,-0.01891,0.07053],"tcp_start":[0.53126,-0.01899,0.04929],"tcp_to_object_dist_end":0.02579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5224,-0.01887,0.14935],"object_pos_start":[0.52726,-0.01897,0.06533],"object_to_goal_dist_end":0.26818,"object_to_goal_dist_start":0.29658,"object_z_max":0.35393,"peak_contact_force":0.11583,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19764.0,"raw_peak_contact_force":0.24121,"subtask_id":"lift_clearance","tcp_end":[0.51843,-0.01879,0.36458],"tcp_start":[0.51995,-0.01879,0.26013],"tcp_to_object_dist_end":0.21526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.60927,0.21038,0.32654],"object_pos_start":[0.53319,-0.0187,0.35419],"object_to_goal_dist_end":0.12039,"object_to_goal_dist_start":0.29704,"object_z_max":0.35449,"peak_contact_force":0.11414,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5569.0,"raw_peak_contact_force":0.22442,"subtask_id":"place_object","tcp_end":[0.60563,0.21866,0.35116],"tcp_start":[0.60537,0.21698,0.35142],"tcp_to_object_dist_end":0.02623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.61308,0.22641,0.20333],"object_pos_start":[0.61224,0.21856,0.33003],"object_to_goal_dist_end":0.00511,"object_to_goal_dist_start":0.12298,"object_z_max":0.33004,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.60483,0.22636,0.22679],"tcp_start":[0.60563,0.21866,0.35116],"tcp_to_object_dist_end":0.02487,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26866,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.11073,"approach_object.approach_arc_height":0.12607,"approach_object.approach_speed":0.07496,"descend_place.place_speed":0.06783,"descend_place.place_x_offset":0.00422,"descend_place.place_y_offset":-0.00061,"descend_to_grasp.descend_speed":0.05849,"descend_to_grasp.descend_x_offset":0.01683,"lift.lift_height":0.10396,"lift.lift_speed":0.0671,"pull_up.pull_up_speed":0.0267},"optimized_scores":{"best_composite_score":0.29615,"best_fitness_score":0.99615,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":401.0,"contact_point_centroid":[0.53843,-0.02539,-0.00143],"force_p95":0.40064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6015,"mean_force":0.1063,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.54265,-0.02683,0.02981]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.53923,-0.04587,0.04969],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27173,"mean_force":0.04956,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53895,-0.02672,0.04784]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02886,-0.00226],"force_p95":0.18723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2612,"mean_force":0.14192,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54698,-0.02695,0.02891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6354.0,"contact_point_centroid":[0.58401,0.04978,0.33993],"force_p95":0.12477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25541,"mean_force":0.08604,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57866,0.0685,0.33842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.63207,0.13972,0.26067],"force_p95":0.13086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24831,"mean_force":0.09358,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62855,0.15865,0.26045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7258.0,"contact_point_centroid":[0.58615,0.09111,0.33846],"force_p95":0.1122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24044,"mean_force":0.07685,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58087,0.07256,0.33751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.53916,-0.00758,0.04976],"force_p95":0.07322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23868,"mean_force":0.04861,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53895,-0.02672,0.04784]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3427.0,"contact_point_centroid":[0.63244,0.17712,0.25798],"force_p95":0.10472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23153,"mean_force":0.06879,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62867,0.15877,0.25779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4731.0,"contact_point_centroid":[0.54588,-0.00773,0.02934],"force_p95":0.07704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15987,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54571,-0.02692,0.0274]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18612.0,"contact_point_centroid":[0.53015,-0.00733,0.20773],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15385,"mean_force":0.05255,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5295,-0.02643,0.20568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18988.0,"contact_point_centroid":[0.53019,-0.04553,0.20921],"force_p95":0.07808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15162,"mean_force":0.05195,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52945,-0.02643,0.20746]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51843,0.00921,0.24164]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5446,-0.01951,0.11216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5098.0,"contact_point_centroid":[0.54596,-0.04628,0.02929],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08806,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54572,-0.02692,0.02741]}],"total_contact_groups":14},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63762,0.16123,0.17675],"final_tcp_position":[0.63207,0.1618,0.19562],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.6015,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53747,-0.01209,0.1862],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1748,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11629.0,"raw_peak_contact_force":0.2612,"subtask_id":"reach_object","tcp_end":[0.5547,-0.02709,0.03833],"tcp_start":[0.53747,-0.01209,0.1862],"tcp_to_object_dist_end":0.01546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54542,-0.02711,0.02506],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25997,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.07121,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":33641.0,"raw_peak_contact_force":0.6015,"tcp_end":[0.54568,-0.02691,0.02736],"tcp_start":[0.5547,-0.02709,0.03833],"tcp_to_object_dist_end":0.00233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":831.0,"n_steps_budget":720.0,"object_pos_end":[0.54071,-0.02685,0.04497],"object_pos_start":[0.54542,-0.02711,0.02506],"object_to_goal_dist_end":0.25036,"object_to_goal_dist_start":0.25997,"object_z_max":0.06484,"peak_contact_force":0.10652,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":37600.0,"raw_peak_contact_force":0.15385,"tcp_end":[0.53576,-0.02662,0.07006],"tcp_start":[0.54061,-0.02676,0.04876],"tcp_to_object_dist_end":0.02558,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":983.0,"n_steps_budget":960.0,"object_pos_end":[0.5356,-0.02652,0.14837],"object_pos_start":[0.53583,-0.02667,0.06488],"object_to_goal_dist_end":0.21662,"object_to_goal_dist_start":0.24222,"object_z_max":0.35031,"peak_contact_force":0.11408,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13612.0,"raw_peak_contact_force":0.25541,"subtask_id":"lift_clearance","tcp_end":[0.52759,-0.0264,0.36317],"tcp_start":[0.52911,-0.02642,0.25895],"tcp_to_object_dist_end":0.21494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.6338,0.14865,0.30246],"object_pos_start":[0.54451,-0.02634,0.35055],"object_to_goal_dist_end":0.12659,"object_to_goal_dist_start":0.273,"object_z_max":0.35077,"peak_contact_force":0.13121,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6067.0,"raw_peak_contact_force":0.24831,"subtask_id":"place_object","tcp_end":[0.62595,0.15599,0.32126],"tcp_start":[0.62546,0.15431,0.32172],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.63762,0.16123,0.17675],"object_pos_start":[0.63734,0.15593,0.30419],"object_to_goal_dist_end":0.00604,"object_to_goal_dist_start":0.12767,"object_z_max":0.30419,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1092.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.63207,0.1618,0.19562],"tcp_start":[0.62595,0.15599,0.32126],"tcp_to_object_dist_end":0.01968,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12723,"average_solve_count":448.0,"average_success_count":448.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.12041,"approach_object.approach_arc_height":0.07548,"approach_object.approach_speed":0.0923,"descend_place.place_speed":0.03188,"descend_place.place_x_offset":0.01432,"descend_place.place_y_offset":0.0055,"descend_to_grasp.descend_speed":0.11929,"descend_to_grasp.descend_x_offset":0.02743,"lift.lift_height":0.14201,"lift.lift_speed":0.02092,"pull_up.pull_up_speed":0.04824},"optimized_scores":{"best_composite_score":0.02205,"best_fitness_score":0.72205,"best_task_score":0.4872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":359.0,"contact_point_centroid":[0.58075,0.11398,-0.00628],"force_p95":1.25036,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16803,"mean_force":0.2983,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59256,0.13668,0.28522]},{"body_a":"world","body_b":"grasp_target","contact_count":250.0,"contact_point_centroid":[0.45699,0.00229,-0.00143],"force_p95":0.41362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5794,"mean_force":0.09901,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.47305,0.00168,0.03308]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4535.0,"contact_point_centroid":[0.50429,0.06409,0.4098],"force_p95":0.14659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32992,"mean_force":0.08916,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50447,0.04566,0.41373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9385.0,"contact_point_centroid":[0.4696,-0.01755,0.05342],"force_p95":0.07456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3021,"mean_force":0.05181,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46929,0.00164,0.05193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9933.0,"contact_point_centroid":[0.4696,0.02079,0.05316],"force_p95":0.07348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27286,"mean_force":0.04853,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46933,0.00164,0.05173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4549.0,"contact_point_centroid":[0.50798,0.03164,0.4038],"force_p95":0.15507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26592,"mean_force":0.09012,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50889,0.05019,0.40738]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46273,6e-05,-0.00217],"force_p95":0.16854,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2473,"mean_force":0.13566,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47629,0.00174,0.03173]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":24926.0,"contact_point_centroid":[0.46181,-0.0176,0.26073],"force_p95":0.0753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2242,"mean_force":0.05047,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46158,0.00154,0.25946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":24598.0,"contact_point_centroid":[0.46185,0.02071,0.25943],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2152,"mean_force":0.05086,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46159,0.00154,0.25811]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.57903,0.11521,-0.00198],"force_p95":0.14312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1837,"mean_force":0.12318,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60625,0.14874,0.20937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4739.0,"contact_point_centroid":[0.47499,0.02072,0.03254],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1387,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47516,0.00172,0.0306]},{"body_a":"world","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48297,0.03222,0.24754]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47201,0.01022,0.11251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4110.0,"contact_point_centroid":[0.47494,-0.01757,0.03359],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09217,"mean_force":0.05356,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47517,0.00172,0.0306]},{"body_a":"left_finger","body_b":"right_finger","contact_count":246.0,"contact_point_centroid":[0.59683,0.14096,0.2812],"force_p95":0.01459,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01139,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59638,0.14094,0.2788]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1107.0,"contact_point_centroid":[0.60681,0.14876,0.21154],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.0104,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60625,0.14874,0.20935]}],"total_contact_groups":16},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.57902,0.11523,0.02602],"final_tcp_position":[0.6163,0.15476,0.14008],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":272986.17002,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46343,0.01847,0.18647],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.16661,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10649.0,"raw_peak_contact_force":0.2473,"subtask_id":"reach_object","tcp_end":[0.48318,0.00191,0.03889],"tcp_start":[0.46343,0.01847,0.18647],"tcp_to_object_dist_end":0.02414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46265,0.00125,0.0254],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23263,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07192,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19568.0,"raw_peak_contact_force":0.5794,"tcp_end":[0.47513,0.00172,0.03057],"tcp_start":[0.48318,0.00191,0.03889],"tcp_to_object_dist_end":0.01352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.45912,0.00144,0.04403],"object_pos_start":[0.46265,0.00125,0.0254],"object_to_goal_dist_end":0.2277,"object_to_goal_dist_start":0.23263,"object_z_max":0.06305,"peak_contact_force":0.12334,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":49524.0,"raw_peak_contact_force":0.2242,"tcp_end":[0.46635,0.00161,0.07269],"tcp_start":[0.47066,0.00166,0.05169],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1217.0,"n_steps_budget":1000.0,"object_pos_end":[0.4539,0.00147,0.18226],"object_pos_start":[0.45569,0.00144,0.06312],"object_to_goal_dist_end":0.2257,"object_to_goal_dist_start":0.22422,"object_z_max":0.45252,"peak_contact_force":272986.17002,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9689.0,"raw_peak_contact_force":2.16803,"subtask_id":"lift_clearance","tcp_end":[0.46118,0.00149,0.47954],"tcp_start":[0.46131,0.00154,0.33736],"tcp_to_object_dist_end":0.29737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.58258,0.10946,0.02491],"object_pos_start":[0.48004,0.00162,0.45276],"object_to_goal_dist_end":0.11004,"object_to_goal_dist_start":0.38611,"object_z_max":0.45286,"peak_contact_force":9748.96153,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2139.0,"raw_peak_contact_force":0.1837,"subtask_id":"place_object","tcp_end":[0.59866,0.14377,0.27467],"tcp_start":[0.59761,0.14235,0.27674],"tcp_to_object_dist_end":0.25262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.57902,0.11523,0.02602],"object_pos_start":[0.57881,0.11552,0.0265],"object_to_goal_dist_end":0.10786,"object_to_goal_dist_start":0.1074,"object_z_max":0.0265,"peak_contact_force":38.94254,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1144.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.6163,0.15476,0.14008],"tcp_start":[0.59866,0.14377,0.27467],"tcp_to_object_dist_end":0.12634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```