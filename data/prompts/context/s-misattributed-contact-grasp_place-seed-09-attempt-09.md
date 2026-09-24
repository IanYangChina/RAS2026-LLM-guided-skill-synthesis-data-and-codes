## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0598 | 0.39 | ✅ accepted |
| 8 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0087 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0152 | 0.24 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.2526 | 0.17 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.2863 | 0.14 | ❌ rejected |

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

## Current Skill (Q=0.060) — your mutation base

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
  subtask_id: place_object
- id: release_object
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
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

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
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.060
- **task_score** (E): 0.393
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1220 |
| descend_to_grasp | 1.00 | 1.00 | 0.1472 |
| grasp | 1.00 | 1.00 | 0.0131 |
| pull_up | 1.00 | 1.00 | 0.0217 |
| lift | 1.00 | 1.00 | 0.1004 |
| approach_goal | 1.00 | 1.00 | 0.0018 |
| descend_place | 1.00 | 1.00 | 0.1265 |
| release_object | 1.00 | 1.00 | 0.0193 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.001, 0.185) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.001, 0.185)→(0.524, -0.015, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 44.000 | 0.171 | 0.256 |
| grasp | grasp | 1.00 / step_budget | (0.524, -0.015, 0.039)→(0.515, -0.015, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 40.000 | 0.072 | 0.581 |
| pull_up | pull | 1.00 / step_budget | (0.510, -0.015, 0.050)→(0.506, -0.015, 0.072) | (0.515, -0.015, 0.025)→(0.510, -0.015, 0.045) | 0.269→0.261 | 1.00 / 31.333 | 100.465 | 0.150 |
| lift | lift | 1.00 / step_budget | (0.499, -0.014, 0.253)→(0.498, -0.014, 0.353) | (0.506, -0.015, 0.065)→(0.505, -0.015, 0.145) | 0.254→0.238 | 1.00 / 29.333 | 0.105 | 0.328 |
| approach_goal | approach | 1.00 / step_budget | (0.610, 0.172, 0.315)→(0.610, 0.174, 0.314) | (0.514, -0.014, 0.340)→(0.615, 0.167, 0.291) | 0.292→0.124 | 1.00 / 41.667 | 0.078 | 0.237 |
| descend_place | descend | 1.00 / step_budget | (0.610, 0.174, 0.314)→(0.613, 0.179, 0.188) | (0.618, 0.174, 0.294)→(0.608, 0.179, 0.167) | 0.125→0.010 | 1.00 / 2.667 | 0.183 | 1.650 |
| release_object | release | 1.00 / step_budget | (0.613, 0.179, 0.188)→(0.608, 0.177, 0.206) | (0.608, 0.179, 0.167)→(0.599, 0.177, 0.026) | 0.010→0.145 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.528
- phase_score: 0.371
- phase_breakdown.reach_object_score: 0.163
- phase_breakdown.lift_clearance_score: 0.007
- phase_breakdown.place_object_score: 0.673
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.528
- **Median Q (composite search score)**: 0.047
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.347


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49164,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.116,"approach_object.approach_arc_height":0.0997,"approach_object.approach_speed":0.09939,"descend_to_grasp.descend_speed":0.07444,"descend_to_grasp.descend_x_offset":0.0173,"lift.lift_height":0.095,"lift.lift_speed":0.06701,"pull_up.pull_up_speed":0.04547,"release_object.release_timeout":0.36256},"optimized_scores":{"best_composite_score":0.00924,"best_fitness_score":0.63924,"best_task_score":0.28853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.58737,0.2268,-0.00788],"force_p95":1.23663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90589,"mean_force":0.39512,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60259,0.22299,0.23748]},{"body_a":"world","body_b":"grasp_target","contact_count":318.0,"contact_point_centroid":[0.53031,-0.01785,-0.00142],"force_p95":0.41487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6058,"mean_force":0.10792,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53519,-0.01906,0.03036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14140.0,"contact_point_centroid":[0.53139,-0.03814,0.05108],"force_p95":0.07371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27541,"mean_force":0.04974,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53112,-0.01899,0.04922]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53698,-0.02097,-0.00225],"force_p95":0.18351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2578,"mean_force":0.14086,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53912,-0.01913,0.02948]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14140.0,"contact_point_centroid":[0.53134,0.00016,0.05112],"force_p95":0.07338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24686,"mean_force":0.04884,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53112,-0.01899,0.04922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10045.0,"contact_point_centroid":[0.56509,0.08093,0.34125],"force_p95":0.10903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2401,"mean_force":0.07115,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56192,0.0997,0.34035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3874.0,"contact_point_centroid":[0.608,0.20315,0.28499],"force_p95":0.10743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22552,"mean_force":0.06333,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60663,0.22241,0.28312]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10770.0,"contact_point_centroid":[0.56639,0.1218,0.3413],"force_p95":0.10171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2108,"mean_force":0.0673,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56319,0.10317,0.34056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4013.0,"contact_point_centroid":[0.6076,0.24081,0.29024],"force_p95":0.0863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20386,"mean_force":0.05472,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60656,0.22215,0.28885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1117.0,"contact_point_centroid":[0.60663,0.24376,0.22244],"force_p95":0.08373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19287,"mean_force":0.04935,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60552,0.22441,0.22132]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1271.0,"contact_point_centroid":[0.60611,0.20535,0.22355],"force_p95":0.0807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18053,"mean_force":0.04273,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60555,0.22443,0.22139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4738.0,"contact_point_centroid":[0.53805,8e-05,0.02994],"force_p95":0.07641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14395,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53787,-0.01911,0.02801]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51447,0.01633,0.24208]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53699,-0.01138,0.11189]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17886.0,"contact_point_centroid":[0.52188,-0.03794,0.20256],"force_p95":0.07223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1177,"mean_force":0.04991,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52147,-0.01881,0.20073]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17519.0,"contact_point_centroid":[0.52188,0.00033,0.20053],"force_p95":0.07229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1113,"mean_force":0.05052,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52152,-0.01881,0.19849]}],"total_contact_groups":17},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59248,0.22296,0.02189],"final_tcp_position":[0.60728,0.22508,0.22676],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":301.17711,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5301,-0.00376,0.18529],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.17169,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11624.0,"raw_peak_contact_force":0.2578,"subtask_id":"reach_object","tcp_end":[0.54677,-0.01916,0.03865],"tcp_start":[0.5301,-0.00376,0.18529],"tcp_to_object_dist_end":0.0161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53684,-0.01931,0.02511],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31571,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07169,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":28598.0,"raw_peak_contact_force":0.6058,"tcp_end":[0.53784,-0.0191,0.02798],"tcp_start":[0.54677,-0.01916,0.03865],"tcp_to_object_dist_end":0.00304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":707.0,"n_steps_budget":600.0,"object_pos_end":[0.53223,-0.01912,0.04523],"object_pos_start":[0.53684,-0.01931,0.02511],"object_to_goal_dist_end":0.30552,"object_to_goal_dist_start":0.31571,"object_z_max":0.06516,"peak_contact_force":301.17711,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":35405.0,"raw_peak_contact_force":0.1177,"tcp_end":[0.52806,-0.01893,0.07058],"tcp_start":[0.53285,-0.01902,0.04932],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":889.0,"n_steps_budget":900.0,"object_pos_end":[0.52671,-0.0189,0.13989],"object_pos_start":[0.52748,-0.01899,0.0652],"object_to_goal_dist_end":0.26904,"object_to_goal_dist_start":0.2966,"object_z_max":0.32577,"peak_contact_force":0.10573,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20815.0,"raw_peak_contact_force":0.2401,"subtask_id":"lift_clearance","tcp_end":[0.51932,-0.01879,0.33686],"tcp_start":[0.52118,-0.0188,0.24153],"tcp_to_object_dist_end":0.19711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.61122,0.21097,0.32642],"object_pos_start":[0.53454,-0.01872,0.32603],"object_to_goal_dist_end":0.12019,"object_to_goal_dist_start":0.28383,"object_z_max":0.33078,"peak_contact_force":0.08388,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7887.0,"raw_peak_contact_force":0.22552,"subtask_id":"place_object","tcp_end":[0.60585,0.21947,0.35057],"tcp_start":[0.60564,0.21797,0.35068],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.60056,0.22419,0.20646],"object_pos_start":[0.61432,0.21934,0.33094],"object_to_goal_dist_end":0.01043,"object_to_goal_dist_start":0.12388,"object_z_max":0.33096,"peak_contact_force":0.15908,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2578.0,"raw_peak_contact_force":1.90589,"subtask_id":"place_object","tcp_end":[0.60728,0.22508,0.22676],"tcp_start":[0.60585,0.21947,0.35057],"tcp_to_object_dist_end":0.0214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59248,0.22296,0.02189],"object_pos_start":[0.60056,0.22419,0.20646],"object_to_goal_dist_end":0.18644,"object_to_goal_dist_start":0.01043,"object_z_max":0.20646,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.60257,0.22298,0.24476],"tcp_start":[0.60728,0.22508,0.22676],"tcp_to_object_dist_end":0.22311,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57143,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.11953,"approach_object.approach_arc_height":0.08189,"approach_object.approach_speed":0.14418,"descend_to_grasp.descend_speed":0.07833,"descend_to_grasp.descend_x_offset":0.01562,"lift.lift_height":0.0804,"lift.lift_speed":0.0796,"pull_up.pull_up_speed":0.05709,"release_object.release_timeout":0.91373},"optimized_scores":{"best_composite_score":0.04657,"best_fitness_score":0.67657,"best_task_score":0.36232},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.60753,0.16203,-0.00733],"force_p95":1.3372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70829,"mean_force":0.38704,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62317,0.16093,0.20442]},{"body_a":"world","body_b":"grasp_target","contact_count":340.0,"contact_point_centroid":[0.53873,-0.02513,-0.00145],"force_p95":0.41089,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61144,"mean_force":0.10931,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.54203,-0.02656,0.03011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15080.0,"contact_point_centroid":[0.53823,-0.04559,0.05078],"force_p95":0.07439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27973,"mean_force":0.04974,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53798,-0.02643,0.04893]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54557,-0.02884,-0.00229],"force_p95":0.19513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27174,"mean_force":0.14404,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54611,-0.02668,0.02919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8230.0,"contact_point_centroid":[0.58253,0.05342,0.30429],"force_p95":0.11223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24475,"mean_force":0.07856,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57899,0.0722,0.30369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15080.0,"contact_point_centroid":[0.53821,-0.00729,0.05084],"force_p95":0.07413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24278,"mean_force":0.04865,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.53798,-0.02643,0.04893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3873.0,"contact_point_centroid":[0.62933,0.14126,0.25408],"force_p95":0.10702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22213,"mean_force":0.06331,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62784,0.16045,0.25234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8645.0,"contact_point_centroid":[0.58505,0.0947,0.30477],"force_p95":0.10288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20953,"mean_force":0.07267,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58121,0.07615,0.30434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4033.0,"contact_point_centroid":[0.62884,0.17905,0.25834],"force_p95":0.08752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20176,"mean_force":0.05633,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62778,0.16029,0.25671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4721.0,"contact_point_centroid":[0.54504,-0.00745,0.02962],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16904,"mean_force":0.04511,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54484,-0.02664,0.02769]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51999,0.01964,0.23704]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1289.0,"contact_point_centroid":[0.62691,0.18145,0.19335],"force_p95":0.07418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13662,"mean_force":0.04232,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62672,0.1621,0.19055]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1386.0,"contact_point_centroid":[0.62677,0.14291,0.19328],"force_p95":0.07165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13522,"mean_force":0.03921,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62674,0.16211,0.1906]},{"body_a":"world","body_b":"grasp_target","contact_count":1372.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54527,-0.01857,0.10952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15042.0,"contact_point_centroid":[0.52832,-0.04525,0.18106],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11742,"mean_force":0.05062,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52782,-0.02612,0.17928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14653.0,"contact_point_centroid":[0.52836,-0.00699,0.17948],"force_p95":0.07619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11702,"mean_force":0.05147,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5279,-0.02612,0.17738]}],"total_contact_groups":17},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61492,0.16084,0.02575],"final_tcp_position":[0.62884,0.16265,0.19614],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.70829,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53957,-0.01057,0.18012],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.18163,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11647.0,"raw_peak_contact_force":0.27174,"subtask_id":"reach_object","tcp_end":[0.55384,-0.0268,0.03861],"tcp_start":[0.53957,-0.01057,0.18012],"tcp_to_object_dist_end":0.01524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54542,-0.02688,0.02495],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25986,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.07198,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":30500.0,"raw_peak_contact_force":0.61144,"tcp_end":[0.54481,-0.02664,0.02765],"tcp_start":[0.55384,-0.0268,0.03861],"tcp_to_object_dist_end":0.00278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":754.0,"n_steps_budget":600.0,"object_pos_end":[0.54068,-0.0266,0.04511],"object_pos_start":[0.54542,-0.02688,0.02495],"object_to_goal_dist_end":0.25011,"object_to_goal_dist_start":0.25986,"object_z_max":0.06494,"peak_contact_force":0.09638,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":29695.0,"raw_peak_contact_force":0.11742,"tcp_end":[0.53492,-0.02634,0.07026],"tcp_start":[0.53977,-0.02649,0.04901],"tcp_to_object_dist_end":0.02581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":751.0,"n_steps_budget":660.0,"object_pos_end":[0.53582,-0.02627,0.12502],"object_pos_start":[0.53574,-0.02641,0.06498],"object_to_goal_dist_end":0.2206,"object_to_goal_dist_start":0.24201,"object_z_max":0.28176,"peak_contact_force":0.1082,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16875.0,"raw_peak_contact_force":0.24475,"subtask_id":"lift_clearance","tcp_end":[0.52505,-0.02604,0.29245],"tcp_start":[0.52747,-0.02611,0.21189],"tcp_to_object_dist_end":0.16777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.62968,0.15026,0.29343],"object_pos_start":[0.54045,-0.02598,0.28202],"object_to_goal_dist_end":0.11748,"object_to_goal_dist_start":0.2367,"object_z_max":0.29839,"peak_contact_force":0.07458,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7906.0,"raw_peak_contact_force":0.22213,"subtask_id":"place_object","tcp_end":[0.62697,0.15808,0.31976],"tcp_start":[0.6267,0.15685,0.31983],"tcp_to_object_dist_end":0.0276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.62403,0.16221,0.17447],"object_pos_start":[0.63438,0.15793,0.29855],"object_to_goal_dist_end":0.00955,"object_to_goal_dist_start":0.12184,"object_z_max":0.29857,"peak_contact_force":0.1575,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2866.0,"raw_peak_contact_force":1.70829,"subtask_id":"place_object","tcp_end":[0.62884,0.16265,0.19614],"tcp_start":[0.62697,0.15808,0.31976],"tcp_to_object_dist_end":0.0222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61492,0.16084,0.02575],"object_pos_start":[0.62403,0.16221,0.17447],"object_to_goal_dist_end":0.15229,"object_to_goal_dist_start":0.00955,"object_z_max":0.17447,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62314,0.16091,0.21391],"tcp_start":[0.62884,0.16265,0.19614],"tcp_to_object_dist_end":0.18834,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48,"average_solve_count":325.0,"average_success_count":325.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09872,"approach_object.approach_arc_height":0.08569,"approach_object.approach_speed":0.08907,"descend_to_grasp.descend_speed":0.10009,"descend_to_grasp.descend_x_offset":0.01353,"lift.lift_height":0.12497,"lift.lift_speed":0.05437,"pull_up.pull_up_speed":0.02567,"release_object.release_timeout":0.6235},"optimized_scores":{"best_composite_score":0.12354,"best_fitness_score":0.75354,"best_task_score":0.52816},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.59256,0.15131,-0.00773],"force_p95":1.06641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33567,"mean_force":0.44398,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59743,0.1483,0.14838]},{"body_a":"world","body_b":"grasp_target","contact_count":225.0,"contact_point_centroid":[0.45758,0.0025,-0.00141],"force_p95":0.38526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52519,"mean_force":0.1052,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.46121,0.00167,0.03377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6873.0,"contact_point_centroid":[0.53377,0.09722,0.34385],"force_p95":0.1538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49908,"mean_force":0.08887,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52971,0.07848,0.34303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8603.0,"contact_point_centroid":[0.53218,0.05821,0.34575],"force_p95":0.12397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43043,"mean_force":0.07626,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52772,0.07658,0.3451]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4301.0,"contact_point_centroid":[0.60269,0.12791,0.20268],"force_p95":0.10166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26445,"mean_force":0.0627,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60086,0.14699,0.20106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9060.0,"contact_point_centroid":[0.45783,-0.01751,0.05403],"force_p95":0.07401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25513,"mean_force":0.05047,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45757,0.00163,0.05212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4191.0,"contact_point_centroid":[0.60255,0.16568,0.20516],"force_p95":0.09629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25129,"mean_force":0.06096,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6007,0.14684,0.20426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9060.0,"contact_point_centroid":[0.45776,0.02078,0.05399],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2423,"mean_force":0.04982,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.45757,0.00163,0.05212]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46282,0.00016,-0.00218],"force_p95":0.16946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23781,"mean_force":0.13625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46422,0.00171,0.03289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1329.0,"contact_point_centroid":[0.60265,0.13043,0.13811],"force_p95":0.07068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21658,"mean_force":0.04233,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6017,0.14955,0.13565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19155.0,"contact_point_centroid":[0.45073,-0.0175,0.23225],"force_p95":0.09486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21536,"mean_force":0.05541,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44957,0.00154,0.23044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18677.0,"contact_point_centroid":[0.45065,0.02062,0.22995],"force_p95":0.09716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18815,"mean_force":0.05636,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44961,0.00154,0.22799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1234.0,"contact_point_centroid":[0.60251,0.16888,0.13755],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17117,"mean_force":0.04497,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60167,0.14954,0.1356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4769.0,"contact_point_centroid":[0.46328,0.02089,0.0337],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13889,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46312,0.0017,0.03181]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.46286,-7e-05,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48326,0.02844,0.24835]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46648,0.00984,0.11436]}],"total_contact_groups":17},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.589,0.14755,0.02895],"final_tcp_position":[0.60429,0.15017,0.14087],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.33567,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46425,0.01775,0.18889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.16107,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11609.0,"raw_peak_contact_force":0.23781,"subtask_id":"reach_object","tcp_end":[0.47101,0.00188,0.03974],"tcp_start":[0.46425,0.01775,0.18889],"tcp_to_object_dist_end":0.01608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,0.00144,0.02534],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23249,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07197,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18345.0,"raw_peak_contact_force":0.52519,"tcp_end":[0.4631,0.0017,0.03178],"tcp_start":[0.47101,0.00188,0.03974],"tcp_to_object_dist_end":0.00646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":453.0,"n_steps_budget":750.0,"object_pos_end":[0.45851,0.00149,0.04573],"object_pos_start":[0.46271,0.00144,0.02534],"object_to_goal_dist_end":0.2275,"object_to_goal_dist_start":0.23249,"object_z_max":0.06582,"peak_contact_force":0.12027,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":37832.0,"raw_peak_contact_force":0.21536,"tcp_end":[0.45451,0.0016,0.07382],"tcp_start":[0.45872,0.00164,0.05287],"tcp_to_object_dist_end":0.02838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1049.0,"n_steps_budget":1000.0,"object_pos_end":[0.45155,0.00149,0.17015],"object_pos_start":[0.45414,0.00148,0.0659],"object_to_goal_dist_end":0.22444,"object_to_goal_dist_start":0.22456,"object_z_max":0.41131,"peak_contact_force":0.10251,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15476.0,"raw_peak_contact_force":0.49908,"subtask_id":"lift_clearance","tcp_end":[0.44838,0.0015,0.42941],"tcp_start":[0.44919,0.00153,0.30431],"tcp_to_object_dist_end":0.25928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.60333,0.14022,0.25435],"object_pos_start":[0.46763,0.0016,0.41157],"object_to_goal_dist_end":0.13294,"object_to_goal_dist_start":0.35629,"object_z_max":0.41174,"peak_contact_force":0.07481,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8492.0,"raw_peak_contact_force":0.26445,"subtask_id":"place_object","tcp_end":[0.59785,0.14368,0.2724],"tcp_start":[0.59655,0.14219,0.27397],"tcp_to_object_dist_end":0.01918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.6,0.14931,0.11888],"object_pos_start":[0.60591,0.14346,0.25123],"object_to_goal_dist_end":0.01125,"object_to_goal_dist_start":0.12946,"object_z_max":0.25123,"peak_contact_force":0.23098,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2721.0,"raw_peak_contact_force":1.33567,"subtask_id":"place_object","tcp_end":[0.60429,0.15017,0.14087],"tcp_start":[0.59785,0.14368,0.2724],"tcp_to_object_dist_end":0.02242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.589,0.14755,0.02895],"object_pos_start":[0.6,0.14931,0.11888],"object_to_goal_dist_end":0.09575,"object_to_goal_dist_start":0.01125,"object_z_max":0.11888,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59732,0.14827,0.15998],"tcp_start":[0.60429,0.15017,0.14087],"tcp_to_object_dist_end":0.13129,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```