## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.0999 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.0208 | 0.16 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0851 | 0.21 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0598 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0637 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=-0.100) — your mutation base

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
- id: grasp_success
  anchor: object
  metric: contact
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place_accuracy
  target_entity: object
  weight: 0.4
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    descent_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_object
- id: grasp_object
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
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_success
- id: lift_object
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  subtask_id: lift_clearance
- id: transport_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_accuracy
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
      tolerance: 0.1
  parameters:
    place_height:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_accuracy
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
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_after_place
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
    tolerance: 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - descent_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.05]
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.100
- **task_score** (E): 0.168
- **fitness_score**: 0.380  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1270 |
| descend_grasp | 1.00 | 1.00 | 0.1259 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 0.67 | 1.00 | 0.0581 |
| transport_goal | 1.00 | 1.00 | 0.0006 |
| descend_place | 1.00 | 1.00 | 0.1614 |
| release_object | 1.00 | 1.00 | 0.0192 |
| retract_after_place | 1.00 | 1.00 | 0.1074 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.001, 0.181) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.513, -0.001, 0.181)→(0.516, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.516, -0.001, 0.055)→(0.508, -0.001, 0.046) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.667 | 0.145 | 0.193 |
| lift_object | lift | 0.67 / step_budget | (0.518, 0.013, 0.296)→(0.521, 0.014, 0.354) | (0.522, -0.001, 0.026)→(0.527, 0.016, 0.073) | 0.289→0.264 | 1.00 / 9.333 | 94253.917 | 1.443 |
| transport_goal | approach | 1.00 / step_budget | (0.606, 0.204, 0.385)→(0.606, 0.204, 0.386) | (0.527, 0.016, 0.073)→(0.527, 0.033, 0.016) | 0.264→0.271 | 1.00 / 8.333 | 94249.473 | 0.619 |
| descend_place | descend | 1.00 / step_budget | (0.606, 0.204, 0.386)→(0.606, 0.206, 0.225) | (0.527, 0.033, 0.016)→(0.527, 0.033, 0.016) | 0.271→0.271 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.606, 0.206, 0.225)→(0.601, 0.204, 0.243) | (0.527, 0.033, 0.016)→(0.527, 0.033, 0.016) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.601, 0.204, 0.243)→(0.600, 0.203, 0.350) | (0.527, 0.033, 0.016)→(0.527, 0.033, 0.016) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.219
- phase_score: 0.760
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.reach_object_score: 0.222
- phase_breakdown.lift_clearance_score: 0.747
- phase_breakdown.place_accuracy_score: 0.915
- grasp_place_fitness: 0.573

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.573
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.219
- **Median Q (composite search score)**: -0.194
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.449


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64493,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.36805,"descend_grasp.descent_height":0.02182,"descend_place.place_height":0.00183,"lift_object.lift_height":0.39288,"retract_after_place.retract_height":0.09418,"transport_goal.transport_speed":0.24988},"optimized_scores":{"best_composite_score":-0.19392,"best_fitness_score":0.28608,"best_task_score":0.15166},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.48623,0.07016,-0.00244],"force_p95":0.20795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02562,"mean_force":0.14545,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47904,0.052,0.34848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8761.0,"contact_point_centroid":[0.4729,0.06541,0.12886],"force_p95":0.12764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32459,"mean_force":0.07284,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46972,0.04675,0.12844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8129.0,"contact_point_centroid":[0.47281,0.0279,0.12948],"force_p95":0.13919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2723,"mean_force":0.07714,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46974,0.04675,0.12947]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04864,-0.00214],"force_p95":0.16342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22054,"mean_force":0.13318,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47137,0.04708,0.04945]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48665,0.02732,0.22652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4336.0,"contact_point_centroid":[0.47032,0.02771,0.04926],"force_p95":0.07695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13703,"mean_force":0.04977,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04697,0.0483]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47665,0.04508,0.11939]},{"body_a":"world","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.48632,0.07101,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.5429,0.1647,0.40465]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.48632,0.07101,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57972,0.22623,0.33396]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48632,0.07101,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57663,0.22585,0.2517]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.48632,0.07101,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57415,0.22452,0.30802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5503.0,"contact_point_centroid":[0.46981,0.06613,0.0498],"force_p95":0.06974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07199,"mean_force":0.04032,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04697,0.04831]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2275.0,"contact_point_centroid":[0.47996,0.05242,0.36527],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01058,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47957,0.05241,0.363]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1161.0,"contact_point_centroid":[0.5803,0.22628,0.33566],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57972,0.22623,0.33345]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2320.0,"contact_point_centroid":[0.54344,0.16496,0.40689],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01041,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.54303,0.16493,0.40456]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57902,0.22682,0.24976],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57839,0.22676,0.24763]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48632,0.07101,0.01602],"final_tcp_position":[0.57431,0.22448,0.34584],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273015.68579,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47773,0.04278,0.18305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47796,0.04772,0.05638],"tcp_start":[0.47773,0.04278,0.18305],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04755,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29109,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16033,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11639.0,"raw_peak_contact_force":0.22054,"subtask_id":"grasp_success","tcp_end":[0.47024,0.04697,0.04827],"tcp_start":[0.47796,0.04772,0.05638],"tcp_to_object_dist_end":0.02597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1256.0,"n_steps_budget":1000.0,"object_pos_end":[0.48632,0.07101,0.01602],"object_pos_start":[0.48268,0.04755,0.02548],"object_to_goal_dist_end":0.28291,"object_to_goal_dist_start":0.29109,"object_z_max":0.2018,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21493.0,"raw_peak_contact_force":2.02562,"subtask_id":"lift_clearance","tcp_end":[0.48449,0.06783,0.44083],"tcp_start":[0.4845,0.06722,0.43947],"tcp_to_object_dist_end":0.42483,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.48632,0.07101,0.01602],"object_pos_start":[0.48632,0.07101,0.01602],"object_to_goal_dist_end":0.28291,"object_to_goal_dist_start":0.28291,"object_z_max":0.01602,"peak_contact_force":9748.8058,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4484.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.57926,0.22522,0.41167],"tcp_start":[0.57901,0.22463,0.41115],"tcp_to_object_dist_end":0.43469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.48632,0.07101,0.01602],"object_pos_start":[0.48632,0.07101,0.01602],"object_to_goal_dist_end":0.28291,"object_to_goal_dist_start":0.28291,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2253.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.57977,0.22736,0.25209],"tcp_start":[0.57926,0.22522,0.41167],"tcp_to_object_dist_end":0.29817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48632,0.07101,0.01602],"object_pos_start":[0.48632,0.07101,0.01602],"object_to_goal_dist_end":0.28291,"object_to_goal_dist_start":0.28291,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57566,0.22532,0.27141],"tcp_start":[0.57977,0.22736,0.25209],"tcp_to_object_dist_end":0.31148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":600.0,"object_pos_end":[0.48632,0.07101,0.01602],"object_pos_start":[0.48632,0.07101,0.01602],"object_to_goal_dist_end":0.28291,"object_to_goal_dist_start":0.28291,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57431,0.22448,0.34584],"tcp_start":[0.57566,0.22532,0.27141],"tcp_to_object_dist_end":0.37427,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62876,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.40419,"descend_grasp.descent_height":0.02003,"descend_place.place_height":0.01514,"lift_object.lift_height":0.35589,"retract_after_place.retract_height":0.11067,"transport_goal.transport_speed":0.10777},"optimized_scores":{"best_composite_score":-0.19859,"best_fitness_score":0.28141,"best_task_score":0.13395},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2206.0,"contact_point_centroid":[0.53931,0.0049,-0.00249],"force_p95":0.22078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89051,"mean_force":0.14412,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53263,-0.01547,0.32257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7864.0,"contact_point_centroid":[0.5265,-0.00197,0.12381],"force_p95":0.1273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30225,"mean_force":0.07918,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52262,-0.02074,0.12204]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8071.0,"contact_point_centroid":[0.52645,-0.03948,0.12111],"force_p95":0.1277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27935,"mean_force":0.07732,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52252,-0.02074,0.11975]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.0212,-0.00205],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16855,"mean_force":0.12648,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52409,-0.02086,0.04547]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51739,-0.01207,0.22551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.52379,-0.00163,0.04678],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12852,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02083,0.04407]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52733,-0.01993,0.11676]},{"body_a":"world","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.53939,0.0058,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.57951,0.13531,0.37443]},{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.53939,0.0058,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60844,0.2252,0.31734]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53939,0.0058,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6047,0.2247,0.24075]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.53939,0.0058,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60214,0.22337,0.30492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.52378,-0.03991,0.04585],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08689,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02083,0.04407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2088.0,"contact_point_centroid":[0.53373,-0.01479,0.34135],"force_p95":0.01122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53335,-0.01478,0.33899]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1038.0,"contact_point_centroid":[0.60894,0.22523,0.31932],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60844,0.2252,0.3171]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3099.0,"contact_point_centroid":[0.57977,0.13488,0.37672],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.57937,0.13488,0.37452]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.60712,0.22564,0.23931],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60657,0.22559,0.2372]}],"total_contact_groups":16},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53939,0.0058,0.01602],"final_tcp_position":[0.60251,0.22343,0.35096],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273008.64532,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52601,-0.019,0.18034],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53126,-0.02099,0.05395],"tcp_start":[0.52601,-0.019,0.18034],"tcp_to_object_dist_end":0.02852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0208,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13392,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.16855,"subtask_id":"grasp_success","tcp_end":[0.52286,-0.02083,0.04403],"tcp_start":[0.53126,-0.02099,0.05395],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1238.0,"n_steps_budget":1000.0,"object_pos_end":[0.53939,0.0058,0.01602],"object_pos_start":[0.53694,-0.0208,0.02582],"object_to_goal_dist_end":0.30154,"object_to_goal_dist_start":0.31645,"object_z_max":0.19564,"peak_contact_force":273001.32049,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20229.0,"raw_peak_contact_force":1.89051,"subtask_id":"lift_clearance","tcp_end":[0.5372,0.00222,0.40366],"tcp_start":[0.53732,0.00146,0.40265],"tcp_to_object_dist_end":0.38766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.53939,0.0058,0.01602],"object_pos_start":[0.53939,0.0058,0.01602],"object_to_goal_dist_end":0.30154,"object_to_goal_dist_start":0.30154,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6011.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.60838,0.22429,0.38836],"tcp_start":[0.60834,0.22373,0.38808],"tcp_to_object_dist_end":0.43719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.53939,0.0058,0.01602],"object_pos_start":[0.53939,0.0058,0.01602],"object_to_goal_dist_end":0.30154,"object_to_goal_dist_start":0.30154,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.608,0.22618,0.24201],"tcp_start":[0.60838,0.22429,0.38836],"tcp_to_object_dist_end":0.32303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53939,0.0058,0.01602],"object_pos_start":[0.53939,0.0058,0.01602],"object_to_goal_dist_end":0.30154,"object_to_goal_dist_start":0.30154,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60367,0.22416,0.2601],"tcp_start":[0.608,0.22618,0.24201],"tcp_to_object_dist_end":0.33376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":720.0,"object_pos_end":[0.53939,0.0058,0.01602],"object_pos_start":[0.53939,0.0058,0.01602],"object_to_goal_dist_end":0.30154,"object_to_goal_dist_start":0.30154,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1452.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60251,0.22343,0.35096],"tcp_start":[0.60367,0.22416,0.2601],"tcp_to_object_dist_end":0.40439,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81858,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.25928,"descend_grasp.descent_height":0.02115,"descend_place.place_height":-0.01705,"lift_object.lift_height":0.20963,"retract_after_place.retract_height":0.1767,"transport_goal.transport_speed":0.27359},"optimized_scores":{"best_composite_score":0.09288,"best_fitness_score":0.57288,"best_task_score":0.21921},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2768.0,"contact_point_centroid":[0.55689,0.02296,-0.00241],"force_p95":0.1248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61054,"mean_force":0.14027,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.6033,0.10669,0.29262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.54922,-0.00942,0.21214],"force_p95":0.33499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4453,"mean_force":0.16632,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.54264,-0.02553,0.21751]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.54352,-0.02828,-0.00137],"force_p95":0.36513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41353,"mean_force":0.07835,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53005,-0.02846,0.04617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.54858,-0.04597,0.20941],"force_p95":0.27631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28467,"mean_force":0.20321,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.54159,-0.02822,0.21662]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8806.0,"contact_point_centroid":[0.53755,-0.04737,0.12076],"force_p95":0.11803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27607,"mean_force":0.07059,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53337,-0.02846,0.11871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8689.0,"contact_point_centroid":[0.53792,-0.0096,0.12321],"force_p95":0.10758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27377,"mean_force":0.07082,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53353,-0.02847,0.12083]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02917,-0.00207],"force_p95":0.14199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18853,"mean_force":0.12798,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53241,-0.02854,0.04624]},{"body_a":"world","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52224,-0.01653,0.22547]},{"body_a":"world","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53551,-0.02741,0.11678]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.55676,0.02298,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62992,0.16313,0.27067]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55676,0.02298,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6248,0.16228,0.17793]},{"body_a":"world","body_b":"grasp_target","contact_count":2508.0,"contact_point_centroid":[0.55676,0.02298,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62114,0.16106,0.27505]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.53236,-0.00926,0.04737],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10257,"mean_force":0.04505,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5312,-0.0285,0.04479]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5403.0,"contact_point_centroid":[0.53173,-0.04772,0.04738],"force_p95":0.06584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07957,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5312,-0.0285,0.04479]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2787.0,"contact_point_centroid":[0.6063,0.1122,0.2983],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.60593,0.1122,0.29602]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1250.0,"contact_point_centroid":[0.63046,0.16315,0.27266],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62992,0.16313,0.2705]}],"total_contact_groups":17},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55676,0.02298,0.01602],"final_tcp_position":[0.62209,0.16124,0.35425],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273012.71265,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53395,-0.02622,0.17922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1532.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53966,-0.02876,0.05501],"tcp_start":[0.53395,-0.02622,0.17922],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02872,0.02574],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1404,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12038.0,"raw_peak_contact_force":0.18853,"subtask_id":"grasp_success","tcp_end":[0.53117,-0.0285,0.04475],"tcp_start":[0.53966,-0.02876,0.05501],"tcp_to_object_dist_end":0.02383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.55609,-0.02836,0.18813],"object_pos_start":[0.54553,-0.02872,0.02574],"object_to_goal_dist_end":0.20827,"object_to_goal_dist_start":0.26073,"object_z_max":0.18803,"peak_contact_force":9760.30694,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17576.0,"raw_peak_contact_force":0.41353,"subtask_id":"lift_clearance","tcp_end":[0.54126,-0.0286,0.21608],"tcp_start":[0.53117,-0.0285,0.04475],"tcp_to_object_dist_end":0.03165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.55676,0.02298,0.01602],"object_pos_start":[0.55609,-0.02836,0.18813],"object_to_goal_dist_end":0.22766,"object_to_goal_dist_start":0.20827,"object_z_max":0.18813,"peak_contact_force":272999.49174,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5713.0,"raw_peak_contact_force":1.61054,"subtask_id":"place_accuracy","tcp_end":[0.6304,0.1628,0.35755],"tcp_start":[0.63047,0.16252,0.35726],"tcp_to_object_dist_end":0.37632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.55676,0.02298,0.01602],"object_pos_start":[0.55676,0.02298,0.01602],"object_to_goal_dist_end":0.22766,"object_to_goal_dist_start":0.22766,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2434.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.6294,0.16364,0.17943],"tcp_start":[0.6304,0.1628,0.35755],"tcp_to_object_dist_end":0.22752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55676,0.02298,0.01602],"object_pos_start":[0.55676,0.02298,0.01602],"object_to_goal_dist_end":0.22766,"object_to_goal_dist_start":0.22766,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62329,0.16179,0.19731],"tcp_start":[0.6294,0.16364,0.17943],"tcp_to_object_dist_end":0.23782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.55676,0.02298,0.01602],"object_pos_start":[0.55676,0.02298,0.01602],"object_to_goal_dist_end":0.22766,"object_to_goal_dist_start":0.22766,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2508.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62209,0.16124,0.35425],"tcp_start":[0.62329,0.16179,0.19731],"tcp_to_object_dist_end":0.3712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```