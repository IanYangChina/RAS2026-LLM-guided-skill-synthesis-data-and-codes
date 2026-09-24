## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1096 | 0.40 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0493 | 0.47 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2132 | 0.73 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2588 | 0.82 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1245 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.110) — your mutation base

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

- **Composite score**: -0.110
- **task_score** (E): 0.396
- **fitness_score**: 0.670  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1707 |
| descend_1 | 1.00 | 1.00 | 0.0884 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.1765 |
| transport_1 | 0.00 | 1.00 | 0.1163 |
| place_descend_1 | 0.67 | 0.67 | 0.0848 |
| release_1 | 1.00 | 1.00 | 0.0011 |
| retract_1 | 1.00 | 1.00 | 0.0355 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.025, 0.134) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.025, 0.134)→(0.510, 0.019, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.019, 0.046)→(0.502, 0.019, 0.037) | (0.516, 0.018, 0.026)→(0.516, 0.019, 0.026) | 0.236→0.236 | 1.00 / 41.000 | 0.201 | 0.227 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.019, 0.037)→(0.511, 0.018, 0.213) | (0.516, 0.019, 0.026)→(0.523, 0.018, 0.196) | 0.236→0.205 | 1.00 / 32.000 | 11.473 | 0.512 |
| transport_1 | approach | 0.00 / guard_failure | (0.511, 0.018, 0.213)→(0.564, 0.103, 0.263) | (0.523, 0.018, 0.196)→(0.576, 0.105, 0.237) | 0.205→0.110 | 1.00 / 21.000 | 0.003 | 0.292 |
| place_descend_1 | descend | 0.67 / step_budget | (0.564, 0.103, 0.263)→(0.587, 0.149, 0.196) | (0.576, 0.105, 0.237)→(0.599, 0.151, 0.168) | 0.110→0.033 | 0.67 / 14.333 | 0.100 | 0.300 |
| release_1 | release | 1.00 / step_budget | (0.582, 0.148, 0.230)→(0.582, 0.148, 0.231) | (0.599, 0.151, 0.168)→(0.597, 0.167, 0.020) | 0.033→0.149 | 1.00 / 4.000 | 0.124 | 1.637 |
| retract_1 | retract | 1.00 / step_budget | (0.582, 0.148, 0.231)→(0.579, 0.147, 0.267) | (0.596, 0.167, 0.019)→(0.595, 0.167, 0.019) | 0.150→0.150 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.553
- phase_score: 0.362
- phase_breakdown.lift_clear_score: 0.126
- phase_breakdown.transport_goal_score: 0.022
- phase_breakdown.place_goal_score: 0.365
- phase_breakdown.grasp_target_score: 0.668
- phase_breakdown.reach_object_score: 0.820
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.553
- **Median Q (composite search score)**: -0.095
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.depth
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20122,"average_solve_count":328.0,"average_success_count":328.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.17151,"approach_1.speed":0.06453,"descend_1.depth":0.01523,"descend_1.speed":0.0662,"lift_1.lift_height":0.27732,"lift_1.speed":0.05461,"place_descend_1.place_z_offset":0.00098,"place_descend_1.speed":0.03869,"release_1.release_duration":0.73515,"retract_1.speed":0.05541,"transport_1.speed":0.15793,"transport_1.transport_z":0.07858},"optimized_scores":{"best_composite_score":-0.03424,"best_fitness_score":0.74576,"best_task_score":0.55253},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":774.0,"contact_point_centroid":[0.57562,0.16215,-0.00302],"force_p95":0.62,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9521,"mean_force":0.18451,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58374,0.16249,0.14304]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.52789,0.03079,-0.00139],"force_p95":0.40513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48365,"mean_force":0.12737,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51555,0.03086,0.04086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.59177,0.14514,0.11438],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41367,"mean_force":0.05339,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58834,0.16405,0.11302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.59196,0.18311,0.1141],"force_p95":0.08809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37099,"mean_force":0.05523,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5883,0.16402,0.11295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7430.0,"contact_point_centroid":[0.56294,0.12053,0.19504],"force_p95":0.08489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34498,"mean_force":0.06135,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56032,0.10174,0.19484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6571.0,"contact_point_centroid":[0.56266,0.08228,0.19689],"force_p95":0.08998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31223,"mean_force":0.06768,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.56009,0.10126,0.19545]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16760.0,"contact_point_centroid":[0.52091,0.01156,0.16512],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30159,"mean_force":0.05516,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51989,0.0306,0.16298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16083.0,"contact_point_centroid":[0.52077,0.0497,0.1617],"force_p95":0.0808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28739,"mean_force":0.05719,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51972,0.0306,0.15946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":570.0,"contact_point_centroid":[0.53181,0.0167,0.28108],"force_p95":0.13428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23369,"mean_force":0.07379,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53024,0.03567,0.27929]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53049,0.03073,-0.00202],"force_p95":0.22594,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22921,"mean_force":0.16189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51784,0.03103,0.04113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":591.0,"contact_point_centroid":[0.53227,0.0549,0.27971],"force_p95":0.11797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19401,"mean_force":0.06636,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53031,0.03579,0.27918]},{"body_a":"world","body_b":"grasp_target","contact_count":2720.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50975,0.04269,0.22363]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4844.0,"contact_point_centroid":[0.51745,0.05001,0.04154],"force_p95":0.07827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12888,"mean_force":0.05413,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51665,0.03095,0.03976]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.57134,0.16211,-0.00199],"force_p95":0.1232,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12551,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5804,0.16151,0.16945]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52356,0.03469,0.09133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4144.0,"contact_point_centroid":[0.51742,0.01174,0.04254],"force_p95":0.08582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1132,"mean_force":0.06079,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51665,0.03095,0.03976]}],"total_contact_groups":16},"final_pose_error":0.0149,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57134,0.16211,0.02602],"final_tcp_position":[0.57992,0.16136,0.18792],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":306.47941,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2720.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52471,0.03795,0.1337],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.52495,0.03155,0.04938],"tcp_start":[0.52471,0.03795,0.1337],"tcp_to_object_dist_end":0.02402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.03074,0.02589],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18351,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.22578,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10788.0,"raw_peak_contact_force":0.22921,"tcp_end":[0.51662,0.03094,0.03973],"tcp_start":[0.52495,0.03155,0.04938],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.53457,0.03056,0.26248],"object_pos_start":[0.53039,0.03074,0.02589],"object_to_goal_dist_end":0.22412,"object_to_goal_dist_start":0.18351,"object_z_max":0.26223,"peak_contact_force":34.23453,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32930.0,"raw_peak_contact_force":0.48365,"subtask_id":"lift_clear","tcp_end":[0.52719,0.03056,0.28371],"tcp_start":[0.51662,0.03094,0.03973],"tcp_to_object_dist_end":0.02248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.54037,0.04311,0.25103],"object_pos_start":[0.53457,0.03056,0.26248],"object_to_goal_dist_end":0.20622,"object_to_goal_dist_start":0.22412,"object_z_max":0.26263,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1161.0,"raw_peak_contact_force":0.23369,"subtask_id":"transport_goal","tcp_end":[0.5336,0.04328,0.27254],"tcp_start":[0.52719,0.03056,0.28371],"tcp_to_object_dist_end":0.02255,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.59678,0.16365,0.09373],"object_pos_start":[0.54037,0.04311,0.25103],"object_to_goal_dist_end":0.02125,"object_to_goal_dist_start":0.20622,"object_z_max":0.25103,"peak_contact_force":0.09038,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14001.0,"raw_peak_contact_force":0.34498,"subtask_id":"place_goal","tcp_end":[0.59091,0.16415,0.11726],"tcp_start":[0.5336,0.04328,0.27254],"tcp_to_object_dist_end":0.02426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.57613,0.16137,0.02692],"object_pos_start":[0.59678,0.16365,0.09373],"object_to_goal_dist_end":0.08678,"object_to_goal_dist_start":0.02125,"object_z_max":0.09373,"peak_contact_force":0.12564,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2806.0,"raw_peak_contact_force":0.9521,"subtask_id":"place_goal","tcp_end":[0.5835,0.16245,0.15234],"tcp_start":[0.58362,0.16249,0.15121],"tcp_to_object_dist_end":0.12564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.57134,0.16211,0.02602],"object_pos_start":[0.57153,0.1621,0.02602],"object_to_goal_dist_end":0.08899,"object_to_goal_dist_start":0.08892,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12551,"tcp_end":[0.57992,0.16136,0.18792],"tcp_start":[0.5835,0.16245,0.15234],"tcp_to_object_dist_end":0.16213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1581,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.17603,"approach_1.speed":0.05208,"descend_1.depth":0.01008,"descend_1.speed":0.06701,"lift_1.lift_height":0.20265,"lift_1.speed":0.03874,"place_descend_1.place_z_offset":0.02709,"place_descend_1.speed":0.05324,"release_1.release_duration":0.77024,"retract_1.speed":0.07082,"transport_1.speed":0.1393,"transport_1.transport_z":0.10711},"optimized_scores":{"best_composite_score":-0.19996,"best_fitness_score":0.58004,"best_task_score":0.21234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5888,0.17516,-0.0034],"force_p95":0.66056,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3775,"mean_force":0.18362,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5522,0.11919,0.32164]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.50015,-0.01385,-0.00154],"force_p95":0.45906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47817,"mean_force":0.18459,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48966,-0.01429,0.03671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5584.0,"contact_point_centroid":[0.52573,0.06121,0.24635],"force_p95":0.11332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35777,"mean_force":0.0694,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52219,0.04257,0.24527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11885.0,"contact_point_centroid":[0.4931,0.00485,0.12101],"force_p95":0.07787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27911,"mean_force":0.05372,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49302,-0.01431,0.11862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12507.0,"contact_point_centroid":[0.49299,-0.03342,0.1203],"force_p95":0.07591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26884,"mean_force":0.05184,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49299,-0.01431,0.1183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4659.0,"contact_point_centroid":[0.52433,0.02075,0.24498],"force_p95":0.13636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25082,"mean_force":0.07888,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52091,0.03963,0.24321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.56212,0.13202,0.29178],"force_p95":0.21962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22892,"mean_force":0.10752,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5555,0.11915,0.299]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01544,-0.00212],"force_p95":0.15741,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22366,"mean_force":0.13184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4918,-0.01432,0.03695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.4912,0.00491,0.03848],"force_p95":0.08019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14636,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49065,-0.0143,0.03572]},{"body_a":"world","body_b":"grasp_target","contact_count":2616.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49876,0.01943,0.21299]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.58891,0.17504,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55061,0.1188,0.35253]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49787,-0.01055,0.08787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.49122,-0.03344,0.03758],"force_p95":0.07259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07909,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49065,-0.0143,0.03573]}],"total_contact_groups":13},"final_pose_error":0.01488,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58891,0.17504,0.01602],"final_tcp_position":[0.55049,0.11874,0.37098],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.3775,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2616.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4996,-0.00686,0.13171],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.49869,-0.01437,0.04437],"tcp_start":[0.4996,-0.00686,0.13171],"tcp_to_object_dist_end":0.0191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01444,0.02559],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31176,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15079,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10868.0,"raw_peak_contact_force":0.22366,"tcp_end":[0.49062,-0.0143,0.03569],"tcp_start":[0.49869,-0.01437,0.04437],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.50888,-0.01441,0.19431],"object_pos_start":[0.50374,-0.01444,0.02559],"object_to_goal_dist_end":0.22301,"object_to_goal_dist_start":0.31176,"object_z_max":0.19404,"peak_contact_force":0.08127,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24483.0,"raw_peak_contact_force":0.47817,"subtask_id":"lift_clear","tcp_end":[0.49958,-0.01437,0.20886],"tcp_start":[0.49062,-0.0143,0.03569],"tcp_to_object_dist_end":0.01726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.57454,0.12294,0.27084],"object_pos_start":[0.50888,-0.01441,0.19431],"object_to_goal_dist_end":0.06951,"object_to_goal_dist_start":0.22301,"object_z_max":0.27341,"peak_contact_force":0.00931,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10243.0,"raw_peak_contact_force":0.35777,"subtask_id":"transport_goal","tcp_end":[0.55544,0.11878,0.29894],"tcp_start":[0.49958,-0.01437,0.20886],"tcp_to_object_dist_end":0.03423,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.5755,0.12557,0.26795],"object_pos_start":[0.57454,0.12294,0.27084],"object_to_goal_dist_end":0.06597,"object_to_goal_dist_start":0.06951,"object_z_max":0.27084,"peak_contact_force":0.0,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12.0,"raw_peak_contact_force":0.22892,"subtask_id":"place_goal","tcp_end":[0.55565,0.11985,0.29882],"tcp_start":[0.55544,0.11878,0.29894],"tcp_to_object_dist_end":0.03715,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.58878,0.17524,0.01642],"object_pos_start":[0.5755,0.12557,0.26795],"object_to_goal_dist_end":0.23203,"object_to_goal_dist_start":0.06597,"object_z_max":0.26795,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1004.0,"raw_peak_contact_force":2.3775,"subtask_id":"place_goal","tcp_end":[0.55197,0.11918,0.33578],"tcp_start":[0.55206,0.1192,0.33463],"tcp_to_object_dist_end":0.32633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":600.0,"object_pos_end":[0.58891,0.17504,0.01602],"object_pos_start":[0.58891,0.17504,0.01602],"object_to_goal_dist_end":0.23244,"object_to_goal_dist_start":0.23244,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":896.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.55049,0.11874,0.37098],"tcp_start":[0.55197,0.11918,0.33578],"tcp_to_object_dist_end":0.36145,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08333,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.23434,"approach_1.speed":0.07483,"descend_1.depth":0.01,"descend_1.speed":0.06396,"lift_1.lift_height":0.14005,"lift_1.speed":0.08219,"place_descend_1.place_z_offset":0.01443,"place_descend_1.speed":0.01317,"release_1.release_duration":0.70979,"retract_1.speed":0.04503,"transport_1.speed":0.17791,"transport_1.transport_z":0.09586},"optimized_scores":{"best_composite_score":-0.09462,"best_fitness_score":0.68538,"best_task_score":0.42238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":950.0,"contact_point_centroid":[0.62606,0.16457,-0.00302],"force_p95":0.53494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5807,"mean_force":0.17375,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60963,0.16106,0.19303]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.51051,0.03928,-0.00137],"force_p95":0.44977,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57461,"mean_force":0.11978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49813,0.03918,0.03656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.62006,0.14489,0.16336],"force_p95":0.32269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47744,"mean_force":0.2123,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61434,0.16266,0.16866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":304.0,"contact_point_centroid":[0.61977,0.17942,0.16398],"force_p95":0.20091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44105,"mean_force":0.11271,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61399,0.16254,0.16795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1241.0,"contact_point_centroid":[0.61278,0.17094,0.19921],"force_p95":0.14214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32721,"mean_force":0.08978,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.60682,0.15259,0.20021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5753.0,"contact_point_centroid":[0.50377,0.02012,0.08713],"force_p95":0.10611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30609,"mean_force":0.06954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50087,0.03893,0.08525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5622.0,"contact_point_centroid":[0.50334,0.05788,0.08517],"force_p95":0.10907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30004,"mean_force":0.07086,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5007,0.03894,0.08303]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3599.0,"contact_point_centroid":[0.5608,0.07516,0.18239],"force_p95":0.1388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28511,"mean_force":0.09749,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55494,0.09383,0.18039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.6126,0.13439,0.19822],"force_p95":0.16255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28116,"mean_force":0.10508,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.60707,0.15287,0.19935]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03958,-0.00204],"force_p95":0.22536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2271,"mean_force":0.16272,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50029,0.03938,0.03663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4272.0,"contact_point_centroid":[0.56126,0.11255,0.18165],"force_p95":0.12389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19746,"mean_force":0.0852,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55521,0.09415,0.18058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.49976,0.02009,0.03815],"force_p95":0.0869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16418,"mean_force":0.06026,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03929,0.03536]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50226,0.03856,0.22502]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.62613,0.16425,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60676,0.16021,0.22259]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50611,0.04218,0.09046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4894.0,"contact_point_centroid":[0.49976,0.05838,0.03714],"force_p95":0.07652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11149,"mean_force":0.05369,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03929,0.03536]}],"total_contact_groups":16},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62613,0.16425,0.01602],"final_tcp_position":[0.60645,0.16009,0.24109],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.5807,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50762,0.04455,0.13724],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_target","tcp_end":[0.50725,0.03999,0.04434],"tcp_start":[0.50762,0.04455,0.13724],"tcp_to_object_dist_end":0.01906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03922,0.02585],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21269,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.2252,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10803.0,"raw_peak_contact_force":0.2271,"tcp_end":[0.49909,0.03929,0.03532],"tcp_start":[0.50725,0.03999,0.04434],"tcp_to_object_dist_end":0.01635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":377.0,"n_steps_budget":990.0,"object_pos_end":[0.52492,0.03914,0.13206],"object_pos_start":[0.51241,0.03922,0.02585],"object_to_goal_dist_end":0.1688,"object_to_goal_dist_start":0.21269,"object_z_max":0.13181,"peak_contact_force":0.10198,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11453.0,"raw_peak_contact_force":0.57461,"subtask_id":"lift_clear","tcp_end":[0.50717,0.03889,0.14687],"tcp_start":[0.49909,0.03929,0.03532],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.61195,0.14746,0.18967],"object_pos_start":[0.52492,0.03914,0.13206],"object_to_goal_dist_end":0.05353,"object_to_goal_dist_start":0.1688,"object_z_max":0.18952,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7871.0,"raw_peak_contact_force":0.28511,"subtask_id":"transport_goal","tcp_end":[0.60314,0.14746,0.21603],"tcp_start":[0.50717,0.03889,0.14687],"tcp_to_object_dist_end":0.02779,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.62329,0.16272,0.14366],"object_pos_start":[0.61195,0.14746,0.18967],"object_to_goal_dist_end":0.01078,"object_to_goal_dist_start":0.05353,"object_z_max":0.18975,"peak_contact_force":0.21067,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2257.0,"raw_peak_contact_force":0.32721,"subtask_id":"place_goal","tcp_end":[0.61586,0.16267,0.17207],"tcp_start":[0.60314,0.14746,0.21603],"tcp_to_object_dist_end":0.02937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.62609,0.16402,0.01647],"object_pos_start":[0.62329,0.16272,0.14366],"object_to_goal_dist_end":0.12884,"object_to_goal_dist_start":0.01078,"object_z_max":0.14366,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1379.0,"raw_peak_contact_force":1.5807,"subtask_id":"place_goal","tcp_end":[0.6094,0.16103,0.20566],"tcp_start":[0.60951,0.16106,0.20454],"tcp_to_object_dist_end":0.18995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":720.0,"object_pos_end":[0.62613,0.16425,0.01602],"object_pos_start":[0.62613,0.16425,0.01602],"object_to_goal_dist_end":0.12928,"object_to_goal_dist_start":0.12928,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.60645,0.16009,0.24109],"tcp_start":[0.6094,0.16103,0.20566],"tcp_to_object_dist_end":0.22597,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```