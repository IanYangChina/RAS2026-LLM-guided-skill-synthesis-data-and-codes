## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.0823 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2046 | 0.41 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0765 | 0.40 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0041 | 0.37 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0090 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.082) — your mutation base

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

- **Composite score**: -0.082
- **task_score** (E): 0.407
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1893 |
| descend | 1.00 | 1.00 | 0.0649 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 0.67 | 1.00 | 0.1081 |
| transport_to_goal | 1.00 | 1.00 | 0.1974 |
| descend_to_place | 1.00 | 1.00 | 0.0006 |
| release | 1.00 | 1.00 | 0.0218 |
| retract_after_place | 1.00 | 1.00 | 0.0392 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.114) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.017, 0.114)→(0.511, 0.018, 0.049) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.140 | 0.189 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.049)→(0.503, 0.018, 0.041) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 27.667 | 0.097 | 0.467 |
| lift | lift | 0.67 / step_budget | (0.503, 0.018, 0.041)→(0.509, 0.018, 0.149) | (0.516, 0.018, 0.026)→(0.519, 0.018, 0.125) | 0.236→0.198 | 1.00 / 26.333 | 0.110 | 0.240 |
| transport_to_goal | approach | 1.00 / step_budget | (0.509, 0.018, 0.149)→(0.592, 0.161, 0.246) | (0.519, 0.018, 0.125)→(0.602, 0.165, 0.220) | 0.198→0.056 | 1.00 / 26.333 | 57066.699 | 0.465 |
| descend_to_place | descend | 1.00 / force_exceeded | (0.592, 0.161, 0.246)→(0.592, 0.162, 0.245) | (0.602, 0.165, 0.220)→(0.602, 0.165, 0.220) | 0.056→0.056 | 1.00 / 2.333 | 0.672 | 1.945 |
| release | release | 1.00 / step_budget | (0.592, 0.162, 0.245)→(0.588, 0.161, 0.267) | (0.602, 0.165, 0.220)→(0.592, 0.163, 0.009) | 0.056→0.160 | 1.00 / 2.667 | 0.208 | 0.647 |
| retract_after_place | retract | 1.00 / step_budget | (0.588, 0.161, 0.267)→(0.596, 0.171, 0.294) | (0.592, 0.163, 0.009)→(0.593, 0.162, 0.024) | 0.160→0.146 | 1.00 / 4.000 | 7.473 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.551
- phase_score: 0.359
- phase_breakdown.approach_object_score: 0.849
- phase_breakdown.place_at_goal_score: 0.103
- phase_breakdown.grasp_object_score: 0.659
- phase_breakdown.lift_object_score: 0.508
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.551
- **Median Q (composite search score)**: -0.057
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3401,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.09722,"approach_object.approach_speed":0.04229,"descend.descend_offset_z":0.02992,"descend.descend_speed":0.05705,"descend_to_place.place_force_threshold":4.06457,"descend_to_place.place_offset_z":-0.03092,"descend_to_place.place_speed":0.01998,"lift.lift_offset_z":0.16106,"lift.lift_speed":0.07495,"retract_after_place.retract_offset_z":0.12285,"retract_after_place.retract_speed":0.06337,"transport_to_goal.transport_offset_z":0.10432,"transport_to_goal.transport_speed":0.15573,"transport_to_goal.transport_tolerance":0.02544},"optimized_scores":{"best_composite_score":-0.0144,"best_fitness_score":0.7406,"best_task_score":0.55051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.57437,0.15984,-0.00912],"force_p95":1.36519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68188,"mean_force":0.51055,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58269,0.1559,0.21257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11.0,"contact_point_centroid":[0.58856,0.17507,0.19808],"force_p95":0.5775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5859,"mean_force":0.29036,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58791,0.15656,0.19786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.59555,0.13953,0.19535],"force_p95":0.45481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55597,"mean_force":0.23317,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58791,0.15656,0.19786]},{"body_a":"world","body_b":"grasp_target","contact_count":189.0,"contact_point_centroid":[0.52761,0.02929,-0.00122],"force_p95":0.24384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44473,"mean_force":0.06439,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51584,0.02971,0.04551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":771.0,"contact_point_centroid":[0.5942,0.13997,0.19216],"force_p95":0.17481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3347,"mean_force":0.08055,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58613,0.1571,0.19457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2868.0,"contact_point_centroid":[0.56453,0.07837,0.17791],"force_p95":0.14804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31258,"mean_force":0.09621,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55715,0.09602,0.17979]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.57806,0.15909,-0.00312],"force_p95":0.27342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31016,"mean_force":0.1365,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58593,0.16022,0.21992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":769.0,"contact_point_centroid":[0.58759,0.176,0.19418],"force_p95":0.20253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30416,"mean_force":0.08574,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58608,0.15708,0.19449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15992.0,"contact_point_centroid":[0.52211,0.04849,0.1001],"force_p95":0.09397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29261,"mean_force":0.06356,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51856,0.0296,0.09805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2731.0,"contact_point_centroid":[0.56012,0.11284,0.17816],"force_p95":0.14,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29241,"mean_force":0.09272,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55624,0.09422,0.17926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15312.0,"contact_point_centroid":[0.52164,0.01072,0.09834],"force_p95":0.0975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28433,"mean_force":0.0655,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5184,0.0296,0.09639]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03068,-0.00208],"force_p95":0.14528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2002,"mean_force":0.12924,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51859,0.02991,0.04528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4713.0,"contact_point_centroid":[0.51756,0.01064,0.04704],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13875,"mean_force":0.04546,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51739,0.02983,0.0439]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51074,0.01386,0.21666]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52362,0.0295,0.0812]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4939.0,"contact_point_centroid":[0.51795,0.04907,0.04571],"force_p95":0.07156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07493,"mean_force":0.04494,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5174,0.02983,0.0439]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57031,0.15777,0.02679],"final_tcp_position":[0.5901,0.16614,0.22056],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52416,0.02821,0.13446],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14272,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11452.0,"raw_peak_contact_force":0.2002,"subtask_id":"grasp_object","tcp_end":[0.52541,0.03037,0.05324],"tcp_start":[0.52416,0.02821,0.13446],"tcp_to_object_dist_end":0.02769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02995,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18421,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.09436,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":31493.0,"raw_peak_contact_force":0.44473,"subtask_id":"grasp_object","tcp_end":[0.51736,0.02983,0.04386],"tcp_start":[0.52541,0.03037,0.05324],"tcp_to_object_dist_end":0.02238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53627,0.02997,0.13634],"object_pos_start":[0.53043,0.02995,0.02569],"object_to_goal_dist_end":0.16475,"object_to_goal_dist_start":0.18421,"object_z_max":0.13622,"peak_contact_force":0.14066,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5599.0,"raw_peak_contact_force":0.31258,"subtask_id":"lift_object","tcp_end":[0.52482,0.02968,0.16334],"tcp_start":[0.51736,0.02983,0.04386],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.59134,0.15859,0.16698],"object_pos_start":[0.53627,0.02997,0.13634],"object_to_goal_dist_end":0.06302,"object_to_goal_dist_start":0.16475,"object_z_max":0.16686,"peak_contact_force":167951.73011,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23.0,"raw_peak_contact_force":0.5859,"subtask_id":"place_at_goal","tcp_end":[0.58791,0.15656,0.19786],"tcp_start":[0.52482,0.02968,0.16334],"tcp_to_object_dist_end":0.03113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.59145,0.15894,0.16701],"object_pos_start":[0.59134,0.15859,0.16698],"object_to_goal_dist_end":0.06292,"object_to_goal_dist_start":0.06302,"object_z_max":0.16698,"peak_contact_force":0.31789,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1680.0,"raw_peak_contact_force":1.68188,"subtask_id":"place_at_goal","tcp_end":[0.58793,0.15686,0.19788],"tcp_start":[0.58791,0.15656,0.19786],"tcp_to_object_dist_end":0.03113,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5809,0.15549,0.01954],"object_pos_start":[0.59145,0.15894,0.16701],"object_to_goal_dist_end":0.0938,"object_to_goal_dist_start":0.06292,"object_z_max":0.16701,"peak_contact_force":0.20237,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":128.0,"raw_peak_contact_force":0.31016,"subtask_id":"place_at_goal","tcp_end":[0.58264,0.15589,0.21946],"tcp_start":[0.58793,0.15686,0.19788],"tcp_to_object_dist_end":0.19993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":600.0,"object_pos_end":[0.57031,0.15777,0.02679],"object_pos_start":[0.5809,0.15549,0.01954],"object_to_goal_dist_end":0.08954,"object_to_goal_dist_start":0.0938,"object_z_max":0.0279,"peak_contact_force":22.1732,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.5901,0.16614,0.22056],"tcp_start":[0.58264,0.15589,0.21946],"tcp_to_object_dist_end":0.19496,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08946,"average_solve_count":313.0,"average_success_count":313.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.07087,"approach_object.approach_speed":0.0469,"descend.descend_offset_z":0.02039,"descend.descend_speed":0.02404,"descend_to_place.place_force_threshold":1.98214,"descend_to_place.place_offset_z":-0.02733,"descend_to_place.place_speed":0.02828,"lift.lift_offset_z":0.19638,"lift.lift_speed":0.0611,"retract_after_place.retract_offset_z":0.19309,"retract_after_place.retract_speed":0.03194,"transport_to_goal.transport_offset_z":0.08582,"transport_to_goal.transport_speed":0.1027,"transport_to_goal.transport_tolerance":0.02516},"optimized_scores":{"best_composite_score":-0.17598,"best_fitness_score":0.57902,"best_task_score":0.21175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":39.0,"contact_point_centroid":[0.58141,0.16393,-0.01163],"force_p95":2.3836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42525,"mean_force":1.50519,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57436,0.17066,0.32898]},{"body_a":"world","body_b":"grasp_target","contact_count":1498.0,"contact_point_centroid":[0.59282,0.16963,-0.00271],"force_p95":0.14526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28132,"mean_force":0.13405,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57897,0.17798,0.37562]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.50078,-0.0152,-0.00113],"force_p95":0.30335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48926,"mean_force":0.07711,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48954,-0.01539,0.03883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.58672,0.15475,0.31291],"force_p95":0.15619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42592,"mean_force":0.08768,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57774,0.17139,0.31092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.57635,0.19039,0.31316],"force_p95":0.23192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40399,"mean_force":0.09751,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57774,0.17139,0.31092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":871.0,"contact_point_centroid":[0.58565,0.15455,0.30717],"force_p95":0.11276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32319,"mean_force":0.0767,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5763,0.17137,0.30631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":895.0,"contact_point_centroid":[0.57493,0.19039,0.30792],"force_p95":0.10984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3143,"mean_force":0.07234,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57639,0.1714,0.30653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17523.0,"contact_point_centroid":[0.4917,0.00377,0.08774],"force_p95":0.08462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30605,"mean_force":0.0576,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49044,-0.0153,0.08562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18502.0,"contact_point_centroid":[0.49164,-0.03431,0.08663],"force_p95":0.08136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28127,"mean_force":0.05507,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49039,-0.0153,0.08489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7995.0,"contact_point_centroid":[0.54042,0.05909,0.22256],"force_p95":0.09355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16935,"mean_force":0.06589,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53416,0.07687,0.22145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6910.0,"contact_point_centroid":[0.53329,0.09352,0.22085],"force_p95":0.10933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16558,"mean_force":0.07504,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53304,0.07446,0.21915]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01556,-0.00203],"force_p95":0.13272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15101,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49218,-0.01543,0.03848]},{"body_a":"world","body_b":"grasp_target","contact_count":2536.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49868,-0.00712,0.20456]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49791,-0.01521,0.06288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.49142,0.00385,0.04001],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11331,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49101,-0.01542,0.03724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5289.0,"contact_point_centroid":[0.49089,-0.03447,0.0398],"force_p95":0.06416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08848,"mean_force":0.04138,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49101,-0.01542,0.03724]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59271,0.1696,0.01602],"final_tcp_position":[0.58471,0.18526,0.42169],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1715.94021,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49944,-0.0145,0.1096],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13155,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11204.0,"raw_peak_contact_force":0.15101,"subtask_id":"grasp_object","tcp_end":[0.4988,-0.01552,0.04561],"tcp_start":[0.49944,-0.0145,0.1096],"tcp_to_object_dist_end":0.02023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01526,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.09137,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":36199.0,"raw_peak_contact_force":0.48926,"subtask_id":"grasp_object","tcp_end":[0.49098,-0.01541,0.0372],"tcp_start":[0.4988,-0.01552,0.04561],"tcp_to_object_dist_end":0.01705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50346,-0.0152,0.11779],"object_pos_start":[0.50371,-0.01526,0.02588],"object_to_goal_dist_end":0.25498,"object_to_goal_dist_start":0.31209,"object_z_max":0.11768,"peak_contact_force":0.10891,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14905.0,"raw_peak_contact_force":0.16935,"subtask_id":"lift_object","tcp_end":[0.49411,-0.01525,0.13755],"tcp_start":[0.49098,-0.01541,0.0372],"tcp_to_object_dist_end":0.02186,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.59167,0.17541,0.2906],"object_pos_start":[0.50346,-0.0152,0.11779],"object_to_goal_dist_end":0.04441,"object_to_goal_dist_start":0.25498,"object_z_max":0.29029,"peak_contact_force":1715.94021,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":258.0,"raw_peak_contact_force":0.42592,"subtask_id":"place_at_goal","tcp_end":[0.57781,0.1708,0.31096],"tcp_start":[0.49411,-0.01525,0.13755],"tcp_to_object_dist_end":0.02506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.592,0.17641,0.28985],"object_pos_start":[0.59167,0.17541,0.2906],"object_to_goal_dist_end":0.04347,"object_to_goal_dist_start":0.04441,"object_z_max":0.29087,"peak_contact_force":1.3389,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1805.0,"raw_peak_contact_force":2.42525,"subtask_id":"place_at_goal","tcp_end":[0.57761,0.17172,0.31021],"tcp_start":[0.57781,0.1708,0.31096],"tcp_to_object_dist_end":0.02537,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58489,0.17285,-0.0093],"object_pos_start":[0.592,0.17641,0.28985],"object_to_goal_dist_end":0.25783,"object_to_goal_dist_start":0.04347,"object_z_max":0.28985,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1498.0,"raw_peak_contact_force":1.28132,"subtask_id":"place_at_goal","tcp_end":[0.57434,0.17066,0.33172],"tcp_start":[0.57761,0.17172,0.31021],"tcp_to_object_dist_end":0.34118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.59271,0.1696,0.01602],"object_pos_start":[0.58489,0.17285,-0.0093],"object_to_goal_dist_end":0.23285,"object_to_goal_dist_start":0.25783,"object_z_max":0.01737,"peak_contact_force":0.12262,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.58471,0.18526,0.42169],"tcp_start":[0.57434,0.17066,0.33172],"tcp_to_object_dist_end":0.40605,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5419,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.06079,"approach_object.approach_speed":0.07409,"descend.descend_offset_z":0.0274,"descend.descend_speed":0.04084,"descend_to_place.place_force_threshold":5.24971,"descend_to_place.place_offset_z":0.01295,"descend_to_place.place_speed":0.0344,"lift.lift_offset_z":0.13492,"lift.lift_speed":0.06404,"retract_after_place.retract_offset_z":0.08543,"retract_after_place.retract_speed":0.08457,"transport_to_goal.transport_offset_z":0.10269,"transport_to_goal.transport_speed":0.11754,"transport_to_goal.transport_tolerance":0.02082},"optimized_scores":{"best_composite_score":-0.05654,"best_fitness_score":0.69846,"best_task_score":0.45851},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.61052,0.1503,-0.01251],"force_p95":1.54644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72868,"mean_force":0.78029,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60708,0.15603,0.24172]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.51,0.03802,-0.00119],"force_p95":0.28113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46786,"mean_force":0.06768,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49834,0.03844,0.04244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.61165,0.17574,0.23035],"force_p95":0.37986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38351,"mean_force":0.25589,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61164,0.15682,0.22824]},{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.60886,0.15256,-0.00541],"force_p95":0.3174,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34889,"mean_force":0.16929,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60934,0.15775,0.24673]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.61786,0.13859,0.22839],"force_p95":0.29773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3233,"mean_force":0.14356,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61164,0.15682,0.22824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16939.0,"contact_point_centroid":[0.50269,0.0573,0.08939],"force_p95":0.09591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2903,"mean_force":0.06021,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50103,0.03829,0.08772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17251.0,"contact_point_centroid":[0.50301,0.01935,0.09186],"force_p95":0.08871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26673,"mean_force":0.05849,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50127,0.03829,0.09013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5490.0,"contact_point_centroid":[0.5648,0.07992,0.18638],"force_p95":0.11013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23695,"mean_force":0.06791,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55903,0.09827,0.18516]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03954,-0.0021],"force_p95":0.1509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21451,"mean_force":0.13002,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50091,0.03868,0.04204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.56291,0.11891,0.1887],"force_p95":0.10874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2085,"mean_force":0.06685,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5605,0.09991,0.18635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1034.0,"contact_point_centroid":[0.60986,0.17615,0.22715],"force_p95":0.0893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20638,"mean_force":0.05362,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6103,0.15711,0.22516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":994.0,"contact_point_centroid":[0.61624,0.13869,0.22538],"force_p95":0.08503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18814,"mean_force":0.0541,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61028,0.1571,0.22511]},{"body_a":"world","body_b":"grasp_target","contact_count":2620.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50253,0.01817,0.19871]},{"body_a":"world","body_b":"grasp_target","contact_count":3356.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50623,0.03831,0.06513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.50014,0.01931,0.04356],"force_p95":0.08084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11002,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49973,0.03858,0.04074]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5456.0,"contact_point_centroid":[0.49946,0.05769,0.04335],"force_p95":0.06776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07167,"mean_force":0.04068,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49974,0.03858,0.04074]}],"total_contact_groups":16},"final_pose_error":0.01962,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61619,0.15947,0.02935],"final_tcp_position":[0.61386,0.16173,0.23943],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1532.4262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":656.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3356.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50748,0.03685,0.09868],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":839.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14648,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11365.0,"raw_peak_contact_force":0.21451,"subtask_id":"grasp_object","tcp_end":[0.50755,0.03923,0.04943],"tcp_start":[0.50748,0.03685,0.09868],"tcp_to_object_dist_end":0.02394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.0387,0.02566],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21309,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.10452,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":34370.0,"raw_peak_contact_force":0.46786,"subtask_id":"grasp_object","tcp_end":[0.4997,0.03858,0.04071],"tcp_start":[0.50755,0.03923,0.04943],"tcp_to_object_dist_end":0.01972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51715,0.03859,0.12127],"object_pos_start":[0.51245,0.0387,0.02566],"object_to_goal_dist_end":0.1752,"object_to_goal_dist_start":0.21309,"object_z_max":0.12115,"peak_contact_force":0.08046,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10974.0,"raw_peak_contact_force":0.23695,"subtask_id":"lift_object","tcp_end":[0.50721,0.03835,0.14471],"tcp_start":[0.4997,0.03858,0.04071],"tcp_to_object_dist_end":0.02547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.62199,0.1596,0.20365],"object_pos_start":[0.51715,0.03859,0.12127],"object_to_goal_dist_end":0.06029,"object_to_goal_dist_start":0.1752,"object_z_max":0.20344,"peak_contact_force":1532.4262,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32.0,"raw_peak_contact_force":0.38351,"subtask_id":"place_at_goal","tcp_end":[0.61164,0.15682,0.22824],"tcp_start":[0.50721,0.03835,0.14471],"tcp_to_object_dist_end":0.02683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62207,0.15982,0.20378],"object_pos_start":[0.62199,0.1596,0.20365],"object_to_goal_dist_end":0.06036,"object_to_goal_dist_start":0.06029,"object_z_max":0.20365,"peak_contact_force":0.35978,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2127.0,"raw_peak_contact_force":1.72868,"subtask_id":"place_at_goal","tcp_end":[0.61171,0.15702,0.22833],"tcp_start":[0.61164,0.15682,0.22824],"tcp_to_object_dist_end":0.0268,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61126,0.15948,0.01703],"object_pos_start":[0.62207,0.15982,0.20378],"object_to_goal_dist_end":0.12969,"object_to_goal_dist_start":0.06036,"object_z_max":0.20383,"peak_contact_force":0.29916,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":62.0,"raw_peak_contact_force":0.34889,"subtask_id":"place_at_goal","tcp_end":[0.60704,0.15603,0.24929],"tcp_start":[0.61171,0.15702,0.22833],"tcp_to_object_dist_end":0.23232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.61619,0.15947,0.02935],"object_pos_start":[0.61126,0.15948,0.01703],"object_to_goal_dist_end":0.11697,"object_to_goal_dist_start":0.12969,"object_z_max":0.02936,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2620.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.61386,0.16173,0.23943],"tcp_start":[0.60704,0.15603,0.24929],"tcp_to_object_dist_end":0.21011,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```