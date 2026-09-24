## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2089 | 0.40 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2033 | 0.41 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.0823 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2046 | 0.41 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0765 | 0.40 | ✅ accepted |

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

## Current Skill (Q=-0.209) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.15
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.15
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.15
- id: place_at_goal
  target_entity: object
  weight: 0.55
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: impedance_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.005
  subtask_id: grasp_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.015
  subtask_id: lift_object
- id: transport_to_goal
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
    - 0.08
    tolerance: 0.03
    orientation:
      mode: none
  parameters:
    transport_offset_z:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    place_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: place_contact
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: place_at_goal
- id: release
  type: release
  control: impedance_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_at_goal
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.015]
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=none
  - parameter_bindings:
    - transport_offset_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=place_contact, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_offset_z: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.209
- **task_score** (E): 0.399
- **fitness_score**: 0.671  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1491 |
| descend | 1.00 | 1.00 | 0.1077 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 0.67 | 1.00 | 0.0953 |
| transport_to_goal | 1.00 | 1.00 | 0.2105 |
| descend_to_place | 1.00 | 1.00 | 0.0530 |
| release | 1.00 | 1.00 | 0.0211 |
| retract_after_place | 1.00 | 1.00 | 0.0878 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.155) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.511, 0.017, 0.155)→(0.511, 0.018, 0.047) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.140 | 0.191 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.047)→(0.503, 0.018, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 40.333 | 0.071 | 0.484 |
| lift | lift | 0.67 / step_budget | (0.503, 0.018, 0.038)→(0.508, 0.018, 0.134) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.113) | 0.236→0.201 | 1.00 / 24.667 | 0.117 | 0.652 |
| transport_to_goal | approach | 1.00 / step_budget | (0.508, 0.018, 0.134)→(0.597, 0.169, 0.240) | (0.515, 0.018, 0.113)→(0.603, 0.171, 0.168) | 0.201→0.063 | 1.00 / 19.333 | 0.107 | 0.211 |
| descend_to_place | descend | 1.00 / step_budget | (0.597, 0.169, 0.240)→(0.599, 0.176, 0.188) | (0.603, 0.171, 0.168)→(0.604, 0.175, 0.127) | 0.063→0.041 | 1.00 / 2.667 | 0.149 | 1.024 |
| release | release | 1.00 / step_budget | (0.599, 0.176, 0.188)→(0.594, 0.174, 0.208) | (0.604, 0.175, 0.127)→(0.600, 0.174, 0.018) | 0.041→0.150 | 1.00 / 4.000 | 0.123 | 0.237 |
| retract_after_place | retract | 1.00 / step_budget | (0.594, 0.174, 0.208)→(0.602, 0.178, 0.295) | (0.600, 0.174, 0.018)→(0.601, 0.174, 0.019) | 0.150→0.149 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.342
- phase_breakdown.approach_object_score: 0.710
- phase_breakdown.place_at_goal_score: 0.041
- phase_breakdown.grasp_object_score: 0.632
- phase_breakdown.lift_object_score: 0.787
- grasp_place_fitness: 0.738

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.738
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: -0.183
- **K-run variance**: 0.0046
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04577,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.10871,"approach_object.approach_speed":0.02694,"descend.descend_offset_z":0.02841,"descend.descend_speed":0.06541,"descend_to_place.place_offset_z":0.0127,"descend_to_place.place_speed":0.02678,"descend_to_place.place_tolerance":0.0052,"lift.lift_offset_z":0.1393,"lift.lift_speed":0.06074,"retract_after_place.retract_offset_z":0.17967,"retract_after_place.retract_speed":0.06806,"transport_to_goal.transport_offset_z":0.08379,"transport_to_goal.transport_speed":0.14164,"transport_to_goal.transport_tolerance":0.02849},"optimized_scores":{"best_composite_score":-0.14152,"best_fitness_score":0.73848,"best_task_score":0.54011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.60112,0.16164,-0.00656],"force_p95":1.22884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66315,"mean_force":0.38312,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58679,0.15575,0.17675]},{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.5274,0.02928,-0.00117],"force_p95":0.25353,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45491,"mean_force":0.06895,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51591,0.02974,0.04296]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3803.0,"contact_point_centroid":[0.54975,0.09213,0.15074],"force_p95":0.12803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31374,"mean_force":0.07864,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5442,0.07368,0.15019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18557.0,"contact_point_centroid":[0.52031,0.01059,0.09223],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28861,"mean_force":0.05462,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51877,0.02961,0.09013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18356.0,"contact_point_centroid":[0.52009,0.04869,0.09078],"force_p95":0.08084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28759,"mean_force":0.05563,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51866,0.02961,0.08887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3196.0,"contact_point_centroid":[0.54706,0.05048,0.1501],"force_p95":0.16065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23262,"mean_force":0.09061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54201,0.06921,0.14892]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03062,-0.00208],"force_p95":0.14537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20155,"mean_force":0.12878,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51861,0.02995,0.04263]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.59971,0.17102,-0.00198],"force_p95":0.12337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17713,"mean_force":0.12268,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59199,0.16986,0.14778]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51067,0.01374,0.22254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.51793,0.01066,0.04404],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13729,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5174,0.02987,0.04124]},{"body_a":"world","body_b":"grasp_target","contact_count":3548.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52367,0.02947,0.08453]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59971,0.17102,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58905,0.17089,0.13643]},{"body_a":"world","body_b":"grasp_target","contact_count":1880.0,"contact_point_centroid":[0.59971,0.17102,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5912,0.1733,0.21168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4938.0,"contact_point_centroid":[0.51795,0.04897,0.04306],"force_p95":0.07119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07755,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02987,0.04125]},{"body_a":"left_finger","body_b":"right_finger","contact_count":58.0,"contact_point_centroid":[0.59166,0.1637,0.18179],"force_p95":0.01613,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01375,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59104,0.16368,0.17946]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4256.0,"contact_point_centroid":[0.59247,0.16989,0.15005],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59199,0.16986,0.14777]}],"total_contact_groups":17},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59971,0.17102,0.01602],"final_tcp_position":[0.59779,0.17697,0.26823],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.66315,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3548.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52415,0.02811,0.14566],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":887.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14116,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.20155,"subtask_id":"grasp_object","tcp_end":[0.52544,0.0304,0.05056],"tcp_start":[0.52415,0.02811,0.14566],"tcp_to_object_dist_end":0.02506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.02995,0.02572],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18421,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.07758,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37110.0,"raw_peak_contact_force":0.45491,"subtask_id":"grasp_object","tcp_end":[0.51737,0.02986,0.04121],"tcp_start":[0.52544,0.0304,0.05056],"tcp_to_object_dist_end":0.02025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53236,0.02957,0.11686],"object_pos_start":[0.53042,0.02995,0.02572],"object_to_goal_dist_end":0.16452,"object_to_goal_dist_start":0.18421,"object_z_max":0.11674,"peak_contact_force":0.17887,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7264.0,"raw_peak_contact_force":1.66315,"subtask_id":"lift_object","tcp_end":[0.52417,0.02966,0.14007],"tcp_start":[0.51737,0.02986,0.04121],"tcp_to_object_dist_end":0.02461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.59954,0.17101,0.01666],"object_pos_start":[0.53236,0.02957,0.11686],"object_to_goal_dist_end":0.09176,"object_to_goal_dist_start":0.16452,"object_z_max":0.1372,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8256.0,"raw_peak_contact_force":0.17713,"subtask_id":"place_at_goal","tcp_end":[0.592,0.16566,0.18007],"tcp_start":[0.52417,0.02966,0.14007],"tcp_to_object_dist_end":0.16367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59971,0.17102,0.01602],"object_pos_start":[0.59954,0.17101,0.01666],"object_to_goal_dist_end":0.0924,"object_to_goal_dist_start":0.09176,"object_z_max":0.01666,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.59361,0.17231,0.13539],"tcp_start":[0.592,0.16566,0.18007],"tcp_to_object_dist_end":0.11954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59971,0.17102,0.01602],"object_pos_start":[0.59971,0.17102,0.01602],"object_to_goal_dist_end":0.0924,"object_to_goal_dist_start":0.0924,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58726,0.17031,0.15616],"tcp_start":[0.59361,0.17231,0.13539],"tcp_to_object_dist_end":0.1407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.59971,0.17102,0.01602],"object_pos_start":[0.59971,0.17102,0.01602],"object_to_goal_dist_end":0.0924,"object_to_goal_dist_start":0.0924,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.59779,0.17697,0.26823],"tcp_start":[0.58726,0.17031,0.15616],"tcp_to_object_dist_end":0.25229,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05145,"average_solve_count":311.0,"average_success_count":311.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.13606,"approach_object.approach_speed":0.06754,"descend.descend_offset_z":0.02015,"descend.descend_speed":0.04281,"descend_to_place.place_offset_z":0.00403,"descend_to_place.place_speed":0.02978,"descend_to_place.place_tolerance":0.00829,"lift.lift_offset_z":0.14958,"lift.lift_speed":0.05776,"retract_after_place.retract_offset_z":0.10576,"retract_after_place.retract_speed":0.09146,"transport_to_goal.transport_offset_z":0.08052,"transport_to_goal.transport_speed":0.05615,"transport_to_goal.transport_tolerance":0.0213},"optimized_scores":{"best_composite_score":-0.30193,"best_fitness_score":0.57807,"best_task_score":0.21231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.57673,0.18262,-0.01363],"force_p95":1.64011,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71383,"mean_force":0.90769,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.579,0.18331,0.26798]},{"body_a":"world","body_b":"grasp_target","contact_count":186.0,"contact_point_centroid":[0.50054,-0.01522,-0.00115],"force_p95":0.29867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46778,"mean_force":0.0731,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48954,-0.01539,0.04003]},{"body_a":"world","body_b":"grasp_target","contact_count":895.0,"contact_point_centroid":[0.59785,0.18334,-0.00218],"force_p95":0.16171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36218,"mean_force":0.12164,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58098,0.18457,0.30487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19016.0,"contact_point_centroid":[0.49215,0.00382,0.08886],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29906,"mean_force":0.05284,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49173,-0.0153,0.0867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19471.0,"contact_point_centroid":[0.492,-0.03438,0.08701],"force_p95":0.07624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27541,"mean_force":0.05195,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49158,-0.0153,0.08506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.58498,0.20337,0.25132],"force_p95":0.0775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17528,"mean_force":0.04887,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58174,0.18443,0.25026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.58406,0.16535,0.24995],"force_p95":0.0868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16691,"mean_force":0.05472,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58172,0.18442,0.25022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4502.0,"contact_point_centroid":[0.58457,0.19991,0.28408],"force_p95":0.07911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16678,"mean_force":0.05712,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58129,0.18095,0.28271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4224.0,"contact_point_centroid":[0.58363,0.16194,0.28373],"force_p95":0.08408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15196,"mean_force":0.06069,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58127,0.18091,0.28305]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01556,-0.00203],"force_p95":0.13267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15118,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49216,-0.01544,0.03968]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49891,-0.00673,0.23782]},{"body_a":"world","body_b":"grasp_target","contact_count":3244.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49774,-0.01473,0.10644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.49141,0.00385,0.04121],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11289,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.491,-0.01542,0.03844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20273.0,"contact_point_centroid":[0.53652,0.06048,0.2202],"force_p95":0.07455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10034,"mean_force":0.04835,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53592,0.07957,0.21859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19464.0,"contact_point_centroid":[0.53944,0.10294,0.22459],"force_p95":0.07479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09789,"mean_force":0.05004,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53783,0.08379,0.22259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5288.0,"contact_point_centroid":[0.49088,-0.03447,0.041],"force_p95":0.06415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08806,"mean_force":0.04138,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.491,-0.01542,0.03844]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5991,0.18336,0.01602],"final_tcp_position":[0.58405,0.18611,0.33417],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.71383,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3244.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49981,-0.01394,0.17486],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":811.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13153,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11204.0,"raw_peak_contact_force":0.15118,"subtask_id":"grasp_object","tcp_end":[0.49888,-0.01552,0.04693],"tcp_start":[0.49981,-0.01394,0.17486],"tcp_to_object_dist_end":0.02148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01527,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3121,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.06805,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":38673.0,"raw_peak_contact_force":0.46778,"subtask_id":"grasp_object","tcp_end":[0.49097,-0.01542,0.03841],"tcp_start":[0.49888,-0.01552,0.04693],"tcp_to_object_dist_end":0.01788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50237,-0.01522,0.11288],"object_pos_start":[0.50372,-0.01527,0.02588],"object_to_goal_dist_end":0.2579,"object_to_goal_dist_start":0.3121,"object_z_max":0.11278,"peak_contact_force":0.07898,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39737.0,"raw_peak_contact_force":0.10034,"subtask_id":"lift_object","tcp_end":[0.49612,-0.01524,0.13278],"tcp_start":[0.49097,-0.01542,0.03841],"tcp_to_object_dist_end":0.02086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.58495,0.17784,0.28772],"object_pos_start":[0.50237,-0.01522,0.11288],"object_to_goal_dist_end":0.0408,"object_to_goal_dist_start":0.2579,"object_z_max":0.28757,"peak_contact_force":0.0857,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8726.0,"raw_peak_contact_force":0.16678,"subtask_id":"place_at_goal","tcp_end":[0.58103,0.1779,0.31215],"tcp_start":[0.49612,-0.01524,0.13278],"tcp_to_object_dist_end":0.02474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.58722,0.18478,0.22816],"object_pos_start":[0.58495,0.17784,0.28772],"object_to_goal_dist_end":0.02014,"object_to_goal_dist_start":0.0408,"object_z_max":0.28776,"peak_contact_force":0.18039,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2076.0,"raw_peak_contact_force":1.71383,"subtask_id":"place_at_goal","tcp_end":[0.58313,0.18485,0.254],"tcp_start":[0.58103,0.1779,0.31215],"tcp_to_object_dist_end":0.02616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58739,0.18329,0.01028],"object_pos_start":[0.58722,0.18478,0.22816],"object_to_goal_dist_end":0.23787,"object_to_goal_dist_start":0.02014,"object_z_max":0.22816,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":895.0,"raw_peak_contact_force":0.36218,"subtask_id":"place_at_goal","tcp_end":[0.57898,0.1833,0.27447],"tcp_start":[0.58313,0.18485,0.254],"tcp_to_object_dist_end":0.26432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":600.0,"object_pos_end":[0.5991,0.18336,0.01602],"object_pos_start":[0.58739,0.18329,0.01028],"object_to_goal_dist_end":0.23245,"object_to_goal_dist_start":0.23787,"object_z_max":0.01628,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.58405,0.18611,0.33417],"tcp_start":[0.57898,0.1833,0.27447],"tcp_to_object_dist_end":0.31852,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41126,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.10607,"approach_object.approach_speed":0.09531,"descend.descend_offset_z":0.02184,"descend.descend_speed":0.032,"descend_to_place.place_offset_z":0.02485,"descend_to_place.place_speed":0.02992,"descend_to_place.place_tolerance":0.00659,"lift.lift_offset_z":0.16343,"lift.lift_speed":0.05622,"retract_after_place.retract_offset_z":0.15793,"retract_after_place.retract_speed":0.07773,"transport_to_goal.transport_offset_z":0.09847,"transport_to_goal.transport_speed":0.15359,"transport_to_goal.transport_tolerance":0.02657},"optimized_scores":{"best_composite_score":-0.1832,"best_fitness_score":0.6968,"best_task_score":0.44448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.60954,0.16724,-0.0064],"force_p95":1.14755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23418,"mean_force":0.34716,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61581,0.16765,0.18267]},{"body_a":"world","body_b":"grasp_target","contact_count":203.0,"contact_point_centroid":[0.50895,0.03779,-0.0012],"force_p95":0.34015,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52888,"mean_force":0.0817,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49813,0.03844,0.03724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19708.0,"contact_point_centroid":[0.49998,0.05737,0.08301],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29805,"mean_force":0.05158,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49966,0.03827,0.08117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10651.0,"contact_point_centroid":[0.62423,0.18557,0.18825],"force_p95":0.12461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28906,"mean_force":0.08491,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61924,0.1673,0.19019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19332.0,"contact_point_centroid":[0.50018,0.01915,0.08516],"force_p95":0.07807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27484,"mean_force":0.05187,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49981,0.03827,0.08301]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9584.0,"contact_point_centroid":[0.62415,0.14885,0.18807],"force_p95":0.1317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26088,"mean_force":0.09392,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61926,0.16731,0.1902]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.60364,0.16714,-0.00203],"force_p95":0.1733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22757,"mean_force":0.12539,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61892,0.16916,0.23927]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03951,-0.0021],"force_p95":0.15225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21957,"mean_force":0.13043,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50091,0.0387,0.03683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9199.0,"contact_point_centroid":[0.56258,0.11929,0.17682],"force_p95":0.09622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19325,"mean_force":0.06728,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55877,0.10056,0.17578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8671.0,"contact_point_centroid":[0.56308,0.08305,0.17793],"force_p95":0.11198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19194,"mean_force":0.07151,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56006,0.10192,0.17694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4085.0,"contact_point_centroid":[0.50016,0.01933,0.03835],"force_p95":0.08102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14607,"mean_force":0.05214,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49973,0.0386,0.03553]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50279,0.01768,0.22182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":567.0,"contact_point_centroid":[0.62485,0.15042,0.16485],"force_p95":0.12226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12316,"mean_force":0.08456,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61973,0.16893,0.17]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":602.0,"contact_point_centroid":[0.62457,0.18723,0.16461],"force_p95":0.1136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12291,"mean_force":0.08046,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61969,0.16892,0.16992]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50644,0.0381,0.07719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5457.0,"contact_point_centroid":[0.49946,0.0577,0.03815],"force_p95":0.06787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07569,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49973,0.0386,0.03554]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60303,0.16713,0.02602],"final_tcp_position":[0.62407,0.1712,0.2835],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.23418,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50773,0.03615,0.14409],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14725,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11342.0,"raw_peak_contact_force":0.21957,"subtask_id":"grasp_object","tcp_end":[0.50762,0.03925,0.04423],"tcp_start":[0.50773,0.03615,0.14409],"tcp_to_object_dist_end":0.01886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03864,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21314,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.06808,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":39243.0,"raw_peak_contact_force":0.52888,"subtask_id":"grasp_object","tcp_end":[0.4997,0.0386,0.0355],"tcp_start":[0.50762,0.03925,0.04423],"tcp_to_object_dist_end":0.0161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51064,0.03829,0.11028],"object_pos_start":[0.51243,0.03864,0.02565],"object_to_goal_dist_end":0.18138,"object_to_goal_dist_start":0.21314,"object_z_max":0.11019,"peak_contact_force":0.09303,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17870.0,"raw_peak_contact_force":0.19325,"subtask_id":"lift_object","tcp_end":[0.50362,0.03829,0.12772],"tcp_start":[0.4997,0.0386,0.0355],"tcp_to_object_dist_end":0.0188,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.62355,0.16419,0.1997],"object_pos_start":[0.51064,0.03829,0.11028],"object_to_goal_dist_end":0.05546,"object_to_goal_dist_start":0.18138,"object_z_max":0.19959,"peak_contact_force":0.11299,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20235.0,"raw_peak_contact_force":0.28906,"subtask_id":"place_at_goal","tcp_end":[0.61766,0.16393,0.22846],"tcp_start":[0.50362,0.03829,0.12772],"tcp_to_object_dist_end":0.02936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62639,0.16949,0.13626],"object_pos_start":[0.62355,0.16419,0.1997],"object_to_goal_dist_end":0.00934,"object_to_goal_dist_start":0.05546,"object_z_max":0.19973,"peak_contact_force":0.14455,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1367.0,"raw_peak_contact_force":1.23418,"subtask_id":"place_at_goal","tcp_end":[0.62147,0.16944,0.17381],"tcp_start":[0.61766,0.16393,0.22846],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61285,0.16713,0.02715],"object_pos_start":[0.62639,0.16949,0.13626],"object_to_goal_dist_end":0.11892,"object_to_goal_dist_start":0.00934,"object_z_max":0.13626,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.22757,"subtask_id":"place_at_goal","tcp_end":[0.61575,0.16763,0.19339],"tcp_start":[0.62147,0.16944,0.17381],"tcp_to_object_dist_end":0.16627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":900.0,"object_pos_end":[0.60303,0.16713,0.02602],"object_pos_start":[0.61285,0.16713,0.02715],"object_to_goal_dist_end":0.12163,"object_to_goal_dist_start":0.11892,"object_z_max":0.02793,"peak_contact_force":0.12262,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.62407,0.1712,0.2835],"tcp_start":[0.61575,0.16763,0.19339],"tcp_to_object_dist_end":0.25837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```