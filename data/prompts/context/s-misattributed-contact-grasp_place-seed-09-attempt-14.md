## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2421 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2045 | 0.83 | ❌ rejected |
| 12 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2935 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2928 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → pull → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2936 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.242) — your mutation base

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

- **Composite score**: 0.242
- **task_score** (E): 1.000
- **fitness_score**: 0.992  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1245 |
| descend_to_grasp | 1.00 | 1.00 | 0.1450 |
| grasp | 1.00 | 1.00 | 0.0132 |
| pull_up | 1.00 | 1.00 | 0.0357 |
| lift | 1.00 | 1.00 | 0.0972 |
| approach_goal | 0.00 | 1.00 | 0.0000 |
| descend_place | 1.00 | 1.00 | 0.2988 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.001, 0.182) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.512, 0.001, 0.182)→(0.526, -0.015, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 44.000 | 0.172 | 0.258 |
| grasp | grasp | 1.00 / step_budget | (0.526, -0.015, 0.039)→(0.517, -0.015, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 40.000 | 0.071 | 0.612 |
| pull_up | pull | 1.00 / step_budget | (0.513, -0.015, 0.064)→(0.508, -0.015, 0.100) | (0.515, -0.015, 0.025)→(0.511, -0.015, 0.058) | 0.269→0.255 | 1.00 / 30.000 | 0.094 | 0.141 |
| lift | lift | 1.00 / step_budget | (0.502, -0.014, 0.275)→(0.501, -0.014, 0.372) | (0.507, -0.015, 0.092)→(0.507, -0.015, 0.169) | 0.245→0.234 | 1.00 / 30.000 | 0.105 | 0.138 |
| approach_goal | approach | 0.00 / guard_failure | (0.501, -0.014, 0.372)→(0.501, -0.014, 0.372) | (0.516, -0.014, 0.358)→(0.516, -0.014, 0.358) | 0.297→0.297 | 1.00 / 26.000 | 0.107 | 0.170 |
| descend_place | descend | 1.00 / step_budget | (0.501, -0.014, 0.372)→(0.609, 0.173, 0.174) | (0.516, -0.014, 0.358)→(0.616, 0.173, 0.153) | 0.297→0.019 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.019
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.447
- phase_breakdown.reach_object_score: 0.158
- phase_breakdown.lift_clearance_score: 0.031
- phase_breakdown.place_object_score: 0.811
- grasp_place_fitness: 0.996

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.996
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.241
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51321,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14052,"approach_object.approach_arc_height":0.06477,"approach_object.approach_speed":0.09026,"descend_place.place_speed":0.11358,"descend_place.place_x_offset":0.0005,"descend_place.place_y_offset":0.00162,"descend_to_grasp.descend_speed":0.08106,"descend_to_grasp.descend_x_offset":0.0217,"lift.lift_height":0.10761,"lift.lift_speed":0.04035,"pull_up.pull_up_height":0.03159,"pull_up.pull_up_speed":0.03537},"optimized_scores":{"best_composite_score":0.24079,"best_fitness_score":0.99079,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":353.0,"contact_point_centroid":[0.53014,-0.01748,-0.00146],"force_p95":0.42109,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63739,"mean_force":0.10657,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53896,-0.01881,0.0303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15600.0,"contact_point_centroid":[0.53521,-0.03788,0.05241],"force_p95":0.07464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28511,"mean_force":0.05002,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53496,-0.01873,0.05054]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53692,-0.02095,-0.00228],"force_p95":0.1906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26944,"mean_force":0.14309,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54307,-0.01887,0.02918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15600.0,"contact_point_centroid":[0.5352,0.00041,0.05244],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25261,"mean_force":0.04905,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53496,-0.01873,0.05054]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4728.0,"contact_point_centroid":[0.54201,0.00034,0.02961],"force_p95":0.07759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15512,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54181,-0.01885,0.0277]},{"body_a":"world","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51566,0.02921,0.23703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12782.0,"contact_point_centroid":[0.56255,0.07587,0.29438],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13654,"mean_force":0.0511,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56224,0.09503,0.29255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12785.0,"contact_point_centroid":[0.56253,0.11414,0.2944],"force_p95":0.07586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13614,"mean_force":0.05089,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56223,0.09501,0.29257]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54002,-0.01054,0.10799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.52376,-0.03775,0.37883],"force_p95":0.08882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10946,"mean_force":0.05403,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52426,-0.01858,0.37752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20470.0,"contact_point_centroid":[0.5262,-0.03772,0.2217],"force_p95":0.07104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1079,"mean_force":0.04946,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5259,-0.01858,0.21987]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20472.0,"contact_point_centroid":[0.52619,0.00055,0.2218],"force_p95":0.07095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10644,"mean_force":0.04923,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5259,-0.01858,0.21989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.52375,0.00057,0.37893],"force_p95":0.08223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10461,"mean_force":0.05433,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52426,-0.01858,0.37752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5113.0,"contact_point_centroid":[0.54204,-0.03823,0.02961],"force_p95":0.07868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08528,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54182,-0.01885,0.02771]}],"total_contact_groups":14},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60814,0.21161,0.19602],"final_tcp_position":[0.60218,0.2116,0.21029],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.63739,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53223,-0.00236,0.17743],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.17851,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11641.0,"raw_peak_contact_force":0.26944,"subtask_id":"reach_object","tcp_end":[0.55075,-0.0189,0.03847],"tcp_start":[0.53223,-0.00236,0.17743],"tcp_to_object_dist_end":0.01869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53682,-0.01909,0.02501],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3156,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07248,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":31553.0,"raw_peak_contact_force":0.63739,"tcp_end":[0.54178,-0.01885,0.02766],"tcp_start":[0.55075,-0.0189,0.03847],"tcp_to_object_dist_end":0.00563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":780.0,"n_steps_budget":600.0,"object_pos_end":[0.53251,-0.01887,0.04603],"object_pos_start":[0.53682,-0.01909,0.02501],"object_to_goal_dist_end":0.30483,"object_to_goal_dist_start":0.3156,"object_z_max":0.06716,"peak_contact_force":0.06833,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":40942.0,"raw_peak_contact_force":0.1079,"tcp_end":[0.53198,-0.01868,0.07342],"tcp_start":[0.53677,-0.01876,0.05056],"tcp_to_object_dist_end":0.0274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1022.0,"n_steps_budget":1000.0,"object_pos_end":[0.52394,-0.01864,0.15405],"object_pos_start":[0.52816,-0.01874,0.0672],"object_to_goal_dist_end":0.2665,"object_to_goal_dist_start":0.29524,"object_z_max":0.36599,"peak_contact_force":0.07441,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":132.0,"raw_peak_contact_force":0.10946,"subtask_id":"lift_clearance","tcp_end":[0.52427,-0.01859,0.37744],"tcp_start":[0.52561,-0.01857,0.26953],"tcp_to_object_dist_end":0.2234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53668,-0.0186,0.36634],"object_pos_start":[0.53667,-0.01861,0.36624],"object_to_goal_dist_end":0.30227,"object_to_goal_dist_start":0.30223,"object_z_max":0.36639,"peak_contact_force":0.07526,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25567.0,"raw_peak_contact_force":0.13654,"subtask_id":"place_object","tcp_end":[0.52423,-0.01858,0.3776],"tcp_start":[0.52422,-0.01858,0.37759],"tcp_to_object_dist_end":0.01679,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.60814,0.21161,0.19602],"object_pos_start":[0.53671,-0.0186,0.3664],"object_to_goal_dist_end":0.01988,"object_to_goal_dist_start":0.3023,"object_z_max":0.3664,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.60218,0.2116,0.21029],"tcp_start":[0.52423,-0.01858,0.3776],"tcp_to_object_dist_end":0.01546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24545,"average_solve_count":330.0,"average_success_count":330.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.08642,"approach_object.approach_arc_height":0.07354,"approach_object.approach_speed":0.1368,"descend_place.place_speed":0.04082,"descend_place.place_x_offset":0.00481,"descend_place.place_y_offset":0.00881,"descend_to_grasp.descend_speed":0.04834,"descend_to_grasp.descend_x_offset":0.0174,"lift.lift_height":0.08199,"lift.lift_speed":0.07873,"pull_up.pull_up_height":0.05764,"pull_up.pull_up_speed":0.03164},"optimized_scores":{"best_composite_score":0.24556,"best_fitness_score":0.99556,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":354.0,"contact_point_centroid":[0.53886,-0.02509,-0.00147],"force_p95":0.41628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61636,"mean_force":0.1088,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.54349,-0.02651,0.02996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":33420.0,"contact_point_centroid":[0.53987,-0.04553,0.07602],"force_p95":0.07162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27974,"mean_force":0.04893,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53961,-0.02639,0.07417]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54555,-0.02883,-0.0023],"force_p95":0.1961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27187,"mean_force":0.1445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54764,-0.02663,0.02899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":33420.0,"contact_point_centroid":[0.53986,-0.00725,0.07609],"force_p95":0.07145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24212,"mean_force":0.04828,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53961,-0.02639,0.07417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4719.0,"contact_point_centroid":[0.54657,-0.0074,0.02941],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16616,"mean_force":0.04511,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54637,-0.02659,0.02748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":35.0,"contact_point_centroid":[0.53427,-0.04468,0.35339],"force_p95":0.13804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15661,"mean_force":0.09528,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5291,-0.0261,0.35221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14622.0,"contact_point_centroid":[0.53196,-0.00703,0.23311],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14928,"mean_force":0.0532,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53125,-0.02613,0.23103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14977.0,"contact_point_centroid":[0.53191,-0.04524,0.23432],"force_p95":0.07975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14783,"mean_force":0.0523,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5312,-0.02613,0.23254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6451.0,"contact_point_centroid":[0.58254,0.08414,0.26613],"force_p95":0.11718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14215,"mean_force":0.09044,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57686,0.06551,0.26465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7345.0,"contact_point_centroid":[0.58101,0.04399,0.26839],"force_p95":0.11398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14172,"mean_force":0.08122,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57521,0.06244,0.26739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":34.0,"contact_point_centroid":[0.53419,-0.0075,0.3538],"force_p95":0.13448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13869,"mean_force":0.09738,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5291,-0.0261,0.35221]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52047,0.0231,0.23547]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54628,-0.0184,0.1086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5132.0,"contact_point_centroid":[0.54659,-0.046,0.02938],"force_p95":0.0795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08566,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54638,-0.02659,0.02749]}],"total_contact_groups":14},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63571,0.15772,0.15889],"final_tcp_position":[0.62632,0.15796,0.18117],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.61636,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.54025,-0.01034,0.17813],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.18155,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11651.0,"raw_peak_contact_force":0.27187,"subtask_id":"reach_object","tcp_end":[0.55536,-0.02675,0.03844],"tcp_start":[0.54025,-0.01034,0.17813],"tcp_to_object_dist_end":0.01599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54541,-0.02682,0.02493],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25984,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.06971,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":67194.0,"raw_peak_contact_force":0.61636,"tcp_end":[0.54634,-0.02659,0.02744],"tcp_start":[0.55536,-0.02675,0.03844],"tcp_to_object_dist_end":0.00269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1671.0,"n_steps_budget":1000.0,"object_pos_end":[0.54112,-0.0265,0.07053],"object_pos_start":[0.54541,-0.02682,0.02493],"object_to_goal_dist_end":0.23744,"object_to_goal_dist_start":0.25984,"object_z_max":0.11635,"peak_contact_force":0.10625,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":29599.0,"raw_peak_contact_force":0.14928,"tcp_end":[0.53714,-0.02631,0.12504],"tcp_start":[0.54152,-0.02644,0.07634],"tcp_to_object_dist_end":0.05466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":773.0,"n_steps_budget":660.0,"object_pos_end":[0.53978,-0.0262,0.17819],"object_pos_start":[0.53886,-0.02631,0.11639],"object_to_goal_dist_end":0.21259,"object_to_goal_dist_start":0.22152,"object_z_max":0.33699,"peak_contact_force":0.13749,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":69.0,"raw_peak_contact_force":0.15661,"subtask_id":"lift_clearance","tcp_end":[0.52912,-0.0261,0.35212],"tcp_start":[0.53083,-0.02612,0.27006],"tcp_to_object_dist_end":0.17426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54541,-0.02604,0.33734],"object_pos_start":[0.54539,-0.02604,0.33724],"object_to_goal_dist_end":0.26429,"object_to_goal_dist_start":0.26423,"object_z_max":0.3374,"peak_contact_force":0.11092,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13796.0,"raw_peak_contact_force":0.14215,"subtask_id":"place_object","tcp_end":[0.52908,-0.02609,0.3523],"tcp_start":[0.52907,-0.02609,0.35228],"tcp_to_object_dist_end":0.02214,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.63571,0.15772,0.15889],"object_pos_start":[0.54545,-0.02604,0.33741],"object_to_goal_dist_end":0.01963,"object_to_goal_dist_start":0.26432,"object_z_max":0.33741,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.62632,0.15796,0.18117],"tcp_start":[0.52908,-0.02609,0.3523],"tcp_to_object_dist_end":0.02418,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24918,"average_solve_count":305.0,"average_success_count":305.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06552,"approach_object.approach_arc_height":0.09852,"approach_object.approach_speed":0.10543,"descend_place.place_speed":0.04034,"descend_place.place_x_offset":0.00266,"descend_place.place_y_offset":0.00871,"descend_to_grasp.descend_speed":0.09095,"descend_to_grasp.descend_x_offset":0.01436,"lift.lift_height":0.10128,"lift.lift_speed":0.06032,"pull_up.pull_up_height":0.04371,"pull_up.pull_up_speed":0.03949},"optimized_scores":{"best_composite_score":0.23982,"best_fitness_score":0.98982,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.4575,0.00246,-0.00136],"force_p95":0.41473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58309,"mean_force":0.1032,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46208,0.00145,0.03357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14200.0,"contact_point_centroid":[0.45824,-0.01773,0.06793],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28199,"mean_force":0.04968,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45798,0.00141,0.06602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14200.0,"contact_point_centroid":[0.45817,0.02056,0.06789],"force_p95":0.07179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27321,"mean_force":0.04923,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45798,0.00141,0.06602]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46282,0.00014,-0.00216],"force_p95":0.1639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23161,"mean_force":0.13468,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46497,0.00149,0.03265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8274.0,"contact_point_centroid":[0.52517,0.05383,0.26308],"force_p95":0.13861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23044,"mean_force":0.08794,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51922,0.07218,0.26299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7438.0,"contact_point_centroid":[0.52554,0.09128,0.26239],"force_p95":0.14649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21983,"mean_force":0.09613,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51978,0.07274,0.26203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16289.0,"contact_point_centroid":[0.45079,0.02044,0.23198],"force_p95":0.08635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16597,"mean_force":0.05462,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45002,0.00133,0.22998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16711.0,"contact_point_centroid":[0.45086,-0.01773,0.23402],"force_p95":0.08433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16346,"mean_force":0.05361,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44997,0.00133,0.2322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.45379,-0.01723,0.38728],"force_p95":0.13435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14934,"mean_force":0.08797,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4482,0.00129,0.38623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.45355,0.01993,0.38804],"force_p95":0.12661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14575,"mean_force":0.09425,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4482,0.00129,0.38623]},{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.46286,-7e-05,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48346,0.02468,0.24885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4779.0,"contact_point_centroid":[0.46403,0.02067,0.03345],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13333,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46386,0.00148,0.03157]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46726,0.0089,0.11538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.4641,-0.0178,0.03349],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08275,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46387,0.00148,0.03158]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60413,0.15028,0.10553],"final_tcp_position":[0.5987,0.15052,0.13084],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46498,0.01607,0.19101],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.15635,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11592.0,"raw_peak_contact_force":0.23161,"subtask_id":"reach_object","tcp_end":[0.47176,0.00165,0.03953],"tcp_start":[0.46498,0.01607,0.19101],"tcp_to_object_dist_end":0.01627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4627,0.00126,0.02541],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23258,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07063,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":28599.0,"raw_peak_contact_force":0.58309,"tcp_end":[0.46384,0.00148,0.03154],"tcp_start":[0.47176,0.00165,0.03953],"tcp_to_object_dist_end":0.00624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":710.0,"n_steps_budget":720.0,"object_pos_end":[0.45863,0.00132,0.05892],"object_pos_start":[0.4627,0.00126,0.02541],"object_to_goal_dist_end":0.22345,"object_to_goal_dist_start":0.23258,"object_z_max":0.09217,"peak_contact_force":0.10745,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":33000.0,"raw_peak_contact_force":0.16597,"tcp_end":[0.45541,0.00139,0.10091],"tcp_start":[0.45951,0.00143,0.06627],"tcp_to_object_dist_end":0.04211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.45694,0.00132,0.17338],"object_pos_start":[0.45461,0.00132,0.09224],"object_to_goal_dist_end":0.2215,"object_to_goal_dist_start":0.21922,"object_z_max":0.36986,"peak_contact_force":0.10235,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":69.0,"raw_peak_contact_force":0.14934,"subtask_id":"lift_clearance","tcp_end":[0.44819,0.00129,0.38612],"tcp_start":[0.44955,0.00133,0.28451],"tcp_to_object_dist_end":0.21292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.46601,0.00138,0.37024],"object_pos_start":[0.46598,0.00137,0.37012],"object_to_goal_dist_end":0.32443,"object_to_goal_dist_start":0.32436,"object_z_max":0.37029,"peak_contact_force":0.13374,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15712.0,"raw_peak_contact_force":0.23044,"subtask_id":"place_object","tcp_end":[0.44821,0.00129,0.38634],"tcp_start":[0.44821,0.00129,0.38631],"tcp_to_object_dist_end":0.024,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.60413,0.15028,0.10553],"object_pos_start":[0.46603,0.00139,0.3703],"object_to_goal_dist_end":0.0179,"object_to_goal_dist_start":0.32446,"object_z_max":0.3703,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":984.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_object","tcp_end":[0.5987,0.15052,0.13084],"tcp_start":[0.44821,0.00129,0.38634],"tcp_to_object_dist_end":0.02589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```