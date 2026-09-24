## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.4101 | 0.24 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1096 | 0.40 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0493 | 0.47 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2132 | 0.73 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2588 | 0.82 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.815, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=-0.410) — your mutation base

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
- id: grasp_target
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place_goal
  weight: 0.2
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_target
- id: grasp_1
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
- id: lift_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: lift_clear
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: grip_transport
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: transport_goal
- id: place_descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.05
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grip_place
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=grip_transport, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.01], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grip_place, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]

## Design Metrics

- **Composite score**: -0.410
- **task_score** (E): 0.237
- **fitness_score**: 0.320  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1704 |
| descend_1 | 1.00 | 1.00 | 0.0704 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 0.33 | 1.00 | 0.0012 |
| transport_1 | 0.67 | 1.00 | 0.1856 |
| place_descend_1 | 1.00 | 1.00 | 0.0391 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 0.67 | 1.00 | 0.0727 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.025, 0.135) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.025, 0.135)→(0.510, 0.019, 0.064) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.064)→(0.502, 0.019, 0.055) | (0.516, 0.018, 0.026)→(0.516, 0.019, 0.026) | 0.236→0.236 | 1.00 / 27.333 | 0.160 | 0.191 |
| lift_1 | lift | 0.33 / step_budget | (0.513, 0.036, 0.245)→(0.513, 0.037, 0.246) | (0.516, 0.019, 0.026)→(0.515, 0.039, 0.016) | 0.236→0.228 | 1.00 / 8.333 | 90998.084 | 1.094 |
| transport_1 | approach | 0.67 / step_budget | (0.513, 0.037, 0.246)→(0.591, 0.158, 0.219) | (0.515, 0.039, 0.016)→(0.515, 0.039, 0.016) | 0.228→0.228 | 1.00 / 8.000 | 3249.741 | 0.123 |
| place_descend_1 | descend | 1.00 / step_budget | (0.591, 0.158, 0.219)→(0.597, 0.172, 0.185) | (0.515, 0.039, 0.016)→(0.515, 0.039, 0.016) | 0.228→0.228 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.597, 0.172, 0.185)→(0.591, 0.170, 0.204) | (0.515, 0.039, 0.016)→(0.515, 0.039, 0.016) | 0.228→0.228 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 0.67 / step_budget | (0.591, 0.170, 0.204)→(0.589, 0.169, 0.277) | (0.515, 0.039, 0.016)→(0.515, 0.039, 0.016) | 0.228→0.228 | 1.00 / 4.000 | 27.129 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.332
- phase_score: 0.523
- phase_breakdown.lift_clear_score: 0.132
- phase_breakdown.transport_goal_score: 0.553
- phase_breakdown.place_goal_score: 0.610
- phase_breakdown.grasp_target_score: 0.500
- phase_breakdown.reach_object_score: 0.821
- grasp_place_fitness: 0.368

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.368
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: -0.400
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.depth
- **Final σ (mean)**: 0.330


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31349,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.05033,"approach_1.speed":0.04956,"descend_1.depth":0.03,"descend_1.speed":0.06387,"lift_1.lift_height":0.26149,"lift_1.speed":0.07613,"place_descend_1.place_z_offset":0.01073,"place_descend_1.speed":0.0589,"retract_1.retract_speed":0.06603,"transport_1.speed":0.2693,"transport_1.transport_z":0.07514},"optimized_scores":{"best_composite_score":-0.36173,"best_fitness_score":0.36827,"best_task_score":0.33184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4215.0,"contact_point_centroid":[0.54114,0.05373,-0.00215],"force_p95":0.12385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.21462,"mean_force":0.12857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52741,0.0417,0.21762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8200.0,"contact_point_centroid":[0.519,0.01258,0.0975],"force_p95":0.12942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30179,"mean_force":0.09659,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51565,0.03093,0.10118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8482.0,"contact_point_centroid":[0.51932,0.04918,0.09906],"force_p95":0.12798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2803,"mean_force":0.09515,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51578,0.03093,0.10289]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53051,0.03079,-0.00204],"force_p95":0.13491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16867,"mean_force":0.12589,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51802,0.03135,0.0559]},{"body_a":"world","body_b":"grasp_target","contact_count":3028.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50962,0.04562,0.22422]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52375,0.03513,0.09841]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.54185,0.05473,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56465,0.11001,0.22872]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.54185,0.05473,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59311,0.16998,0.15825]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54185,0.05473,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59003,0.17229,0.13159]},{"body_a":"world","body_b":"grasp_target","contact_count":3376.0,"contact_point_centroid":[0.54185,0.05473,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58492,0.17062,0.19368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.51731,0.04994,0.0513],"force_p95":0.09171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09937,"mean_force":0.07025,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51685,0.03128,0.05453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2701.0,"contact_point_centroid":[0.51759,0.01251,0.0517],"force_p95":0.09732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0975,"mean_force":0.07581,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51685,0.03128,0.05453]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4053.0,"contact_point_centroid":[0.52884,0.04291,0.23062],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01048,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52846,0.0429,0.22832]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1777.0,"contact_point_centroid":[0.56499,0.10986,0.23117],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.0104,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56456,0.10984,0.22887]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.59364,0.17331,0.12952],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.00987,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59295,0.17328,0.12743]},{"body_a":"left_finger","body_b":"right_finger","contact_count":534.0,"contact_point_centroid":[0.59368,0.17001,0.16062],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.01028,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59311,0.16998,0.15826]}],"total_contact_groups":16},"final_pose_error":0.01306,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54185,0.05473,0.01602],"final_tcp_position":[0.58526,0.17068,0.23871],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.97692,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":758.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3028.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52483,0.03844,0.1326],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":908.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.52495,0.03187,0.06418],"tcp_start":[0.52483,0.03844,0.1326],"tcp_to_object_dist_end":0.03858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03099,0.02585],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18331,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13426,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7413.0,"raw_peak_contact_force":0.16867,"tcp_end":[0.51682,0.03127,0.05449],"tcp_start":[0.52495,0.03187,0.06418],"tcp_to_object_dist_end":0.03171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1932.0,"n_steps_budget":1000.0,"object_pos_end":[0.54188,0.05473,0.01647],"object_pos_start":[0.53043,0.03099,0.02585],"object_to_goal_dist_end":0.1652,"object_to_goal_dist_start":0.18331,"object_z_max":0.11793,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24950.0,"raw_peak_contact_force":1.21462,"subtask_id":"lift_clear","tcp_end":[0.53834,0.05394,0.27818],"tcp_start":[0.53835,0.05354,0.27729],"tcp_to_object_dist_end":0.26174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.54185,0.05473,0.01602],"object_pos_start":[0.54185,0.05473,0.01602],"object_to_goal_dist_end":0.16547,"object_to_goal_dist_start":0.16547,"object_z_max":0.01602,"peak_contact_force":9748.97692,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3433.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.59268,0.16669,0.18372],"tcp_start":[0.53834,0.05394,0.27818],"tcp_to_object_dist_end":0.20795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.54185,0.05473,0.01602],"object_pos_start":[0.54185,0.05473,0.01602],"object_to_goal_dist_end":0.16547,"object_to_goal_dist_start":0.16547,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5951,0.17377,0.13146],"tcp_start":[0.59268,0.16669,0.18372],"tcp_to_object_dist_end":0.17417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54185,0.05473,0.01602],"object_pos_start":[0.54185,0.05473,0.01602],"object_to_goal_dist_end":0.16547,"object_to_goal_dist_start":0.16547,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58826,0.17169,0.15138],"tcp_start":[0.5951,0.17377,0.13146],"tcp_to_object_dist_end":0.18482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":844.0,"n_steps_budget":960.0,"object_pos_end":[0.54185,0.05473,0.01602],"object_pos_start":[0.54185,0.05473,0.01602],"object_to_goal_dist_end":0.16547,"object_to_goal_dist_start":0.16547,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58526,0.17068,0.23871],"tcp_start":[0.58826,0.17169,0.15138],"tcp_to_object_dist_end":0.2548,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02113,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.25098,"approach_1.speed":0.05502,"descend_1.depth":0.03026,"descend_1.speed":0.03904,"lift_1.lift_height":0.14171,"lift_1.speed":0.06333,"place_descend_1.place_z_offset":0.00327,"place_descend_1.speed":0.06226,"retract_1.retract_speed":0.05392,"transport_1.speed":0.11691,"transport_1.transport_z":0.08615},"optimized_scores":{"best_composite_score":-0.46802,"best_fitness_score":0.26198,"best_task_score":0.12278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.49243,-0.00389,-0.00208],"force_p95":0.14823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77854,"mean_force":0.12861,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49522,-0.01394,0.12776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4029.0,"contact_point_centroid":[0.48981,0.00442,0.07038],"force_p95":0.14991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40191,"mean_force":0.09518,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48951,-0.01423,0.07425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4734.0,"contact_point_centroid":[0.49021,-0.03252,0.07153],"force_p95":0.11543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26038,"mean_force":0.07906,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48962,-0.01423,0.07529]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01559,-0.00211],"force_p95":0.15577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20854,"mean_force":0.13065,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49196,-0.0142,0.05725]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49876,0.01194,0.21544]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49795,-0.011,0.09967]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49192,-0.00251,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52689,0.07194,0.22426]},{"body_a":"world","body_b":"grasp_target","contact_count":568.0,"contact_point_centroid":[0.49192,-0.00251,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57042,0.15929,0.27094]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49192,-0.00251,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57513,0.17472,0.25448]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49192,-0.00251,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5722,0.17354,0.31663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2661.0,"contact_point_centroid":[0.49071,0.00464,0.05309],"force_p95":0.09791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11135,"mean_force":0.07653,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01419,0.05601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3251.0,"contact_point_centroid":[0.49076,-0.03293,0.05288],"force_p95":0.08998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09023,"mean_force":0.06433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01419,0.05602]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2367.0,"contact_point_centroid":[0.49642,-0.01386,0.13973],"force_p95":0.01131,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01064,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49611,-0.01386,0.13743]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4270.0,"contact_point_centroid":[0.52741,0.07218,0.22673],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01044,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52701,0.07217,0.22447]},{"body_a":"left_finger","body_b":"right_finger","contact_count":613.0,"contact_point_centroid":[0.57094,0.15932,0.27333],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01035,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.57043,0.15931,0.27093]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.57745,0.17555,0.25251],"force_p95":0.01084,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00983,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57696,0.17554,0.25027]}],"total_contact_groups":16},"final_pose_error":0.01406,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49192,-0.00251,0.01602],"final_tcp_position":[0.57263,0.17362,0.36037],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.44651,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49963,-0.0079,0.13458],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49868,-0.01425,0.06473],"tcp_start":[0.49963,-0.0079,0.13458],"tcp_to_object_dist_end":0.03908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50378,-0.01468,0.02561],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31189,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7712.0,"raw_peak_contact_force":0.20854,"tcp_end":[0.49081,-0.01418,0.05598],"tcp_start":[0.49868,-0.01425,0.06473],"tcp_to_object_dist_end":0.03303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1084.0,"n_steps_budget":1000.0,"object_pos_end":[0.49192,-0.00251,0.01602],"object_pos_start":[0.50378,-0.01468,0.02561],"object_to_goal_dist_end":0.31461,"object_to_goal_dist_start":0.31189,"object_z_max":0.05607,"peak_contact_force":272994.00729,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13918.0,"raw_peak_contact_force":0.77854,"subtask_id":"lift_clear","tcp_end":[0.49081,-0.00678,0.15883],"tcp_start":[0.49216,-0.00765,0.15926],"tcp_to_object_dist_end":0.14288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49192,-0.00251,0.01602],"object_pos_start":[0.49192,-0.00251,0.01602],"object_to_goal_dist_end":0.31461,"object_to_goal_dist_start":0.31461,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8270.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.56359,0.1447,0.2889],"tcp_start":[0.49081,-0.00678,0.15883],"tcp_to_object_dist_end":0.31823,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":142.0,"n_steps_budget":1000.0,"object_pos_end":[0.49192,-0.00251,0.01602],"object_pos_start":[0.49192,-0.00251,0.01602],"object_to_goal_dist_end":0.31461,"object_to_goal_dist_start":0.31461,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1181.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.57843,0.17553,0.25376],"tcp_start":[0.56359,0.1447,0.2889],"tcp_to_object_dist_end":0.30936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49192,-0.00251,0.01602],"object_pos_start":[0.49192,-0.00251,0.01602],"object_to_goal_dist_end":0.31461,"object_to_goal_dist_start":0.31461,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57411,0.17427,0.27434],"tcp_start":[0.57843,0.17553,0.25376],"tcp_to_object_dist_end":0.32363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49192,-0.00251,0.01602],"object_pos_start":[0.49192,-0.00251,0.01602],"object_to_goal_dist_end":0.31461,"object_to_goal_dist_start":0.31461,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57263,0.17362,0.36037],"tcp_start":[0.57411,0.17427,0.27434],"tcp_to_object_dist_end":0.39512,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1032,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.21598,"approach_1.speed":0.07405,"descend_1.depth":0.03002,"descend_1.speed":0.04491,"lift_1.lift_height":0.28391,"lift_1.speed":0.08397,"place_descend_1.place_z_offset":0.01428,"place_descend_1.speed":0.01063,"retract_1.retract_speed":0.02815,"transport_1.speed":0.2476,"transport_1.transport_z":0.03801},"optimized_scores":{"best_composite_score":-0.40043,"best_fitness_score":0.32957,"best_task_score":0.25584},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4422.0,"contact_point_centroid":[0.51195,0.06289,-0.00215],"force_p95":0.12389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28925,"mean_force":0.12977,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5042,0.0497,0.23198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7452.0,"contact_point_centroid":[0.50072,0.02091,0.09787],"force_p95":0.13962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30437,"mean_force":0.10007,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4979,0.03924,0.10188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7701.0,"contact_point_centroid":[0.50128,0.05745,0.09965],"force_p95":0.12972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2893,"mean_force":0.09651,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49798,0.03924,0.10369]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03969,-0.00202],"force_p95":0.19332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19685,"mean_force":0.15316,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,0.03966,0.05664]},{"body_a":"world","body_b":"grasp_target","contact_count":2424.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50223,0.04029,0.22535]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5062,0.04258,0.10043]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.51201,0.06381,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56177,0.1131,0.24012]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.51201,0.06381,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61563,0.16451,0.17684]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51201,0.06381,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61322,0.16508,0.16797]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51201,0.06381,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60844,0.16356,0.20909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2680.0,"contact_point_centroid":[0.4999,0.02082,0.05237],"force_p95":0.1119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1181,"mean_force":0.08719,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03957,0.05536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2930.0,"contact_point_centroid":[0.4996,0.05824,0.05204],"force_p95":0.10544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11617,"mean_force":0.08143,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03957,0.05536]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4251.0,"contact_point_centroid":[0.50511,0.05091,0.24557],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01048,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50462,0.0509,0.24331]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2065.0,"contact_point_centroid":[0.56277,0.11355,0.24191],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01043,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56223,0.11354,0.23963]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.61658,0.166,0.16642],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61584,0.16597,0.16422]},{"body_a":"left_finger","body_b":"right_finger","contact_count":235.0,"contact_point_centroid":[0.61624,0.16454,0.17893],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01057,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61563,0.16451,0.17679]}],"total_contact_groups":16},"final_pose_error":0.05541,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51201,0.06381,0.01602],"final_tcp_position":[0.60854,0.16356,0.23216],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273003.9447,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50764,0.04504,0.1367],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":992.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50722,0.04026,0.06441],"tcp_start":[0.50764,0.04504,0.1367],"tcp_to_object_dist_end":0.03876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03955,0.0259],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21243,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.19309,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7410.0,"raw_peak_contact_force":0.19685,"tcp_end":[0.49927,0.03957,0.05533],"tcp_start":[0.50722,0.04026,0.06441],"tcp_to_object_dist_end":0.03223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1925.0,"n_steps_budget":1000.0,"object_pos_end":[0.51202,0.06382,0.016],"object_pos_start":[0.51244,0.03955,0.0259],"object_to_goal_dist_end":0.20449,"object_to_goal_dist_start":0.21243,"object_z_max":0.12095,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23826.0,"raw_peak_contact_force":1.28925,"subtask_id":"lift_clear","tcp_end":[0.50896,0.06293,0.30048],"tcp_start":[0.50919,0.06259,0.29948],"tcp_to_object_dist_end":0.28449,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.51201,0.06381,0.01602],"object_pos_start":[0.51201,0.06381,0.01602],"object_to_goal_dist_end":0.20448,"object_to_goal_dist_start":0.20448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3997.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.61565,0.16354,0.1835],"tcp_start":[0.50896,0.06293,0.30048],"tcp_to_object_dist_end":0.22076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.51201,0.06381,0.01602],"object_pos_start":[0.51201,0.06381,0.01602],"object_to_goal_dist_end":0.20448,"object_to_goal_dist_start":0.20448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":459.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61784,0.16636,0.16844],"tcp_start":[0.61565,0.16354,0.1835],"tcp_to_object_dist_end":0.212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51201,0.06381,0.01602],"object_pos_start":[0.51201,0.06381,0.01602],"object_to_goal_dist_end":0.20448,"object_to_goal_dist_start":0.20448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61165,0.16455,0.18747],"tcp_start":[0.61784,0.16636,0.16844],"tcp_to_object_dist_end":0.22242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51201,0.06381,0.01602],"object_pos_start":[0.51201,0.06381,0.01602],"object_to_goal_dist_end":0.20448,"object_to_goal_dist_start":0.20448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60854,0.16356,0.23216],"tcp_start":[0.61165,0.16455,0.18747],"tcp_to_object_dist_end":0.25687,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```