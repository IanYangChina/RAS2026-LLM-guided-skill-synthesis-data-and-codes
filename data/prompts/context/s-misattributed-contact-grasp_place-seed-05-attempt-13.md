## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2033 | 0.41 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.0823 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2046 | 0.41 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0765 | 0.40 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0041 | 0.37 | ✅ accepted |

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

## Current Skill (Q=-0.203) — your mutation base

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

- **Composite score**: -0.203
- **task_score** (E): 0.406
- **fitness_score**: 0.677  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1550 |
| descend | 1.00 | 1.00 | 0.1039 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 0.67 | 1.00 | 0.1040 |
| transport_to_goal | 1.00 | 0.67 | 0.2013 |
| descend_to_place | 1.00 | 1.00 | 0.0675 |
| release | 1.00 | 1.00 | 0.0216 |
| retract_after_place | 1.00 | 1.00 | 0.0711 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.149) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.017, 0.149)→(0.511, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 43.667 | 0.140 | 0.195 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.045)→(0.503, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 33.000 | 0.114 | 0.518 |
| lift | lift | 0.67 / step_budget | (0.503, 0.018, 0.036)→(0.508, 0.017, 0.140) | (0.516, 0.018, 0.026)→(0.518, 0.018, 0.121) | 0.237→0.197 | 1.00 / 31.000 | 0.097 | 0.229 |
| transport_to_goal | approach | 1.00 / step_budget | (0.508, 0.017, 0.140)→(0.593, 0.162, 0.247) | (0.518, 0.018, 0.121)→(0.602, 0.165, 0.225) | 0.197→0.060 | 0.67 / 25.333 | 0.050 | 0.371 |
| descend_to_place | descend | 1.00 / step_budget | (0.593, 0.162, 0.247)→(0.599, 0.175, 0.181) | (0.602, 0.165, 0.225)→(0.608, 0.176, 0.148) | 0.060→0.020 | 1.00 / 3.333 | 0.177 | 1.617 |
| release | release | 1.00 / step_budget | (0.599, 0.175, 0.181)→(0.594, 0.173, 0.201) | (0.608, 0.176, 0.148)→(0.597, 0.170, 0.023) | 0.020→0.146 | 1.00 / 4.000 | 0.123 | 0.179 |
| retract_after_place | retract | 1.00 / step_budget | (0.594, 0.173, 0.201)→(0.601, 0.178, 0.272) | (0.597, 0.170, 0.023)→(0.592, 0.171, 0.023) | 0.146→0.147 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.566
- phase_score: 0.308
- phase_breakdown.approach_object_score: 0.330
- phase_breakdown.place_at_goal_score: 0.088
- phase_breakdown.grasp_object_score: 0.591
- phase_breakdown.lift_object_score: 0.809
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: -0.187
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.269


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17829,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.14844,"approach_object.approach_speed":0.04165,"descend.descend_offset_z":0.02156,"descend.descend_speed":0.06996,"descend_to_place.place_offset_z":0.00974,"descend_to_place.place_speed":0.02882,"descend_to_place.place_tolerance":0.01312,"lift.lift_offset_z":0.19771,"lift.lift_speed":0.05706,"retract_after_place.retract_offset_z":0.14041,"retract_after_place.retract_speed":0.14252,"transport_to_goal.transport_offset_z":0.12122,"transport_to_goal.transport_speed":0.14632,"transport_to_goal.transport_tolerance":0.03245},"optimized_scores":{"best_composite_score":-0.12449,"best_fitness_score":0.75551,"best_task_score":0.56619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":296.0,"contact_point_centroid":[0.58162,0.17152,-0.00413],"force_p95":0.9154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01926,"mean_force":0.24205,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58891,0.17264,0.13356]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.52647,0.02921,-0.0012],"force_p95":0.28548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50293,"mean_force":0.08315,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51555,0.02967,0.03902]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4798.0,"contact_point_centroid":[0.58987,0.18569,0.16996],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32532,"mean_force":0.05876,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59096,0.16678,0.16713]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.59245,0.19308,0.12412],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31859,"mean_force":0.05055,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59324,0.17398,0.12053]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4756.0,"contact_point_centroid":[0.59708,0.14877,0.1665],"force_p95":0.0882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31308,"mean_force":0.05996,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59109,0.16702,0.16574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18882.0,"contact_point_centroid":[0.51715,0.04862,0.08437],"force_p95":0.07793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29744,"mean_force":0.05357,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5165,0.02954,0.08228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18647.0,"contact_point_centroid":[0.51729,0.01046,0.08595],"force_p95":0.07862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2953,"mean_force":0.05368,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51658,0.02954,0.08368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1118.0,"contact_point_centroid":[0.59969,0.15571,0.12103],"force_p95":0.07528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28587,"mean_force":0.04875,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59323,0.17397,0.12052]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03061,-0.00209],"force_p95":0.14819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2121,"mean_force":0.12951,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51852,0.02989,0.03873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5664.0,"contact_point_centroid":[0.55469,0.07279,0.16747],"force_p95":0.08918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19476,"mean_force":0.05904,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55175,0.09163,0.166]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5599.0,"contact_point_centroid":[0.55281,0.11368,0.16997],"force_p95":0.08109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17234,"mean_force":0.05797,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55338,0.09469,0.1679]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.57948,0.17098,-0.00197],"force_p95":0.15162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16146,"mean_force":0.12267,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59181,0.17451,0.18692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.51788,0.0106,0.04013],"force_p95":0.07899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13876,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51731,0.02981,0.03735]},{"body_a":"world","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51055,0.01336,0.24211]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52341,0.02911,0.10046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.51788,0.04892,0.03916],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07947,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51731,0.02981,0.03735]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57946,0.17098,0.02602],"final_tcp_position":[0.5971,0.17697,0.22929],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.01926,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52381,0.02745,0.18486],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14327,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10840.0,"raw_peak_contact_force":0.2121,"subtask_id":"grasp_object","tcp_end":[0.52546,0.03035,0.04673],"tcp_start":[0.52381,0.02745,0.18486],"tcp_to_object_dist_end":0.02132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02987,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18429,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.06924,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":37745.0,"raw_peak_contact_force":0.50293,"subtask_id":"grasp_object","tcp_end":[0.51728,0.0298,0.03731],"tcp_start":[0.52546,0.03035,0.04673],"tcp_to_object_dist_end":0.01754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5265,0.02961,0.11045],"object_pos_start":[0.53041,0.02987,0.02569],"object_to_goal_dist_end":0.16682,"object_to_goal_dist_start":0.18429,"object_z_max":0.11035,"peak_contact_force":0.08853,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11263.0,"raw_peak_contact_force":0.19476,"subtask_id":"lift_object","tcp_end":[0.51997,0.02956,0.12974],"tcp_start":[0.51728,0.0298,0.03731],"tcp_to_object_dist_end":0.02036,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.59844,0.16252,0.18983],"object_pos_start":[0.5265,0.02961,0.11045],"object_to_goal_dist_end":0.08336,"object_to_goal_dist_start":0.16682,"object_z_max":0.1896,"peak_contact_force":0.07466,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9554.0,"raw_peak_contact_force":0.32532,"subtask_id":"place_at_goal","tcp_end":[0.58906,0.16003,0.20983],"tcp_start":[0.51997,0.02956,0.12974],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.60279,0.17753,0.10195],"object_pos_start":[0.59844,0.16252,0.18983],"object_to_goal_dist_end":0.00635,"object_to_goal_dist_start":0.08336,"object_z_max":0.19,"peak_contact_force":0.1538,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2466.0,"raw_peak_contact_force":1.01926,"subtask_id":"place_at_goal","tcp_end":[0.59541,0.17452,0.12438],"tcp_start":[0.58906,0.16003,0.20983],"tcp_to_object_dist_end":0.0238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58021,0.17107,0.02651],"object_pos_start":[0.60279,0.17753,0.10195],"object_to_goal_dist_end":0.08465,"object_to_goal_dist_start":0.00635,"object_z_max":0.10195,"peak_contact_force":0.12264,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.16146,"subtask_id":"place_at_goal","tcp_end":[0.58878,0.1726,0.1453],"tcp_start":[0.59541,0.17452,0.12438],"tcp_to_object_dist_end":0.11911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":600.0,"object_pos_end":[0.57946,0.17098,0.02602],"object_pos_start":[0.58021,0.17107,0.02651],"object_to_goal_dist_end":0.08532,"object_to_goal_dist_start":0.08465,"object_z_max":0.02651,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1740.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.5971,0.17697,0.22929],"tcp_start":[0.58878,0.1726,0.1453],"tcp_to_object_dist_end":0.20412,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85788,"average_solve_count":387.0,"average_success_count":387.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.09524,"approach_object.approach_speed":0.01116,"descend.descend_offset_z":0.02034,"descend.descend_speed":0.0402,"descend_to_place.place_offset_z":-0.00359,"descend_to_place.place_speed":0.01333,"descend_to_place.place_tolerance":0.01473,"lift.lift_offset_z":0.14531,"lift.lift_speed":0.06842,"retract_after_place.retract_offset_z":0.10651,"retract_after_place.retract_speed":0.09925,"transport_to_goal.transport_offset_z":0.08617,"transport_to_goal.transport_speed":0.10309,"transport_to_goal.transport_tolerance":0.03351},"optimized_scores":{"best_composite_score":-0.29843,"best_fitness_score":0.58157,"best_task_score":0.21164},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":542.0,"contact_point_centroid":[0.60003,0.17279,-0.00445],"force_p95":0.93982,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29768,"mean_force":0.22236,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57815,0.18156,0.25548]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.50124,-0.01539,-0.00111],"force_p95":0.35743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54025,"mean_force":0.06869,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48968,-0.01545,0.03602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1559.0,"contact_point_centroid":[0.57762,0.19324,0.28696],"force_p95":0.17025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44302,"mean_force":0.09906,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57853,0.17451,0.28971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1597.0,"contact_point_centroid":[0.58917,0.15964,0.28318],"force_p95":0.13653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40951,"mean_force":0.10055,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57881,0.17517,0.28657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16772.0,"contact_point_centroid":[0.49377,0.0036,0.08798],"force_p95":0.08987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29233,"mean_force":0.06044,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49207,-0.01541,0.08615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17518.0,"contact_point_centroid":[0.49373,-0.03437,0.08697],"force_p95":0.08763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28307,"mean_force":0.05824,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49201,-0.01541,0.08541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6185.0,"contact_point_centroid":[0.53692,0.09484,0.22478],"force_p95":0.12823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22052,"mean_force":0.08114,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53568,0.07594,0.2245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6540.0,"contact_point_centroid":[0.54002,0.05244,0.21904],"force_p95":0.12904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21181,"mean_force":0.07792,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53307,0.07,0.21909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01562,-0.00203],"force_p95":0.13047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15494,"mean_force":0.125,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49225,-0.01549,0.03578]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49865,-0.00699,0.2172]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.59985,0.17264,-0.00199],"force_p95":0.12282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12344,"mean_force":0.12264,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58013,0.18354,0.30347]},{"body_a":"world","body_b":"grasp_target","contact_count":2724.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4977,-0.01501,0.08123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.49095,0.00378,0.03767],"force_p95":0.06548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09134,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01547,0.03453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5362.0,"contact_point_centroid":[0.49082,-0.03471,0.03719],"force_p95":0.06369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08056,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01547,0.03453]}],"total_contact_groups":14},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59985,0.17264,0.01602],"final_tcp_position":[0.58369,0.18591,0.3352],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.29768,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2724.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49958,-0.01433,0.13406],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12972,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12253.0,"raw_peak_contact_force":0.15494,"subtask_id":"grasp_object","tcp_end":[0.49889,-0.01558,0.0429],"tcp_start":[0.49958,-0.01433,0.13406],"tcp_to_object_dist_end":0.01758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01548,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.17221,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":34451.0,"raw_peak_contact_force":0.54025,"subtask_id":"grasp_object","tcp_end":[0.49105,-0.01547,0.0345],"tcp_start":[0.49889,-0.01558,0.0429],"tcp_to_object_dist_end":0.01531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50973,-0.0153,0.12639],"object_pos_start":[0.5037,-0.01548,0.02588],"object_to_goal_dist_end":0.24876,"object_to_goal_dist_start":0.31223,"object_z_max":0.1263,"peak_contact_force":0.1273,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12725.0,"raw_peak_contact_force":0.22052,"subtask_id":"lift_object","tcp_end":[0.49761,-0.0154,0.14445],"tcp_start":[0.49105,-0.01547,0.0345],"tcp_to_object_dist_end":0.02175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.58926,0.17409,0.29005],"object_pos_start":[0.50973,-0.0153,0.12639],"object_to_goal_dist_end":0.04407,"object_to_goal_dist_start":0.24876,"object_z_max":0.28975,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3156.0,"raw_peak_contact_force":0.44302,"subtask_id":"place_at_goal","tcp_end":[0.5779,0.17034,0.3114],"tcp_start":[0.49761,-0.0154,0.14445],"tcp_to_object_dist_end":0.02447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.59468,0.17951,0.20119],"object_pos_start":[0.58926,0.17409,0.29005],"object_to_goal_dist_end":0.04823,"object_to_goal_dist_start":0.04407,"object_z_max":0.29031,"peak_contact_force":0.12351,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":542.0,"raw_peak_contact_force":2.29768,"subtask_id":"place_at_goal","tcp_end":[0.58217,0.18284,0.25193],"tcp_start":[0.5779,0.17034,0.3114],"tcp_to_object_dist_end":0.05237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59985,0.17264,0.016],"object_pos_start":[0.59468,0.17951,0.20119],"object_to_goal_dist_end":0.23295,"object_to_goal_dist_start":0.04823,"object_z_max":0.20119,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":948.0,"raw_peak_contact_force":0.12344,"subtask_id":"place_at_goal","tcp_end":[0.57787,0.18145,0.27314],"tcp_start":[0.58217,0.18284,0.25193],"tcp_to_object_dist_end":0.25823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.59985,0.17264,0.01602],"object_pos_start":[0.59985,0.17264,0.016],"object_to_goal_dist_end":0.23293,"object_to_goal_dist_start":0.23295,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.58369,0.18591,0.3352],"tcp_start":[0.57787,0.18145,0.27314],"tcp_to_object_dist_end":0.31986,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11155,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.09071,"approach_object.approach_speed":0.06276,"descend.descend_offset_z":0.02416,"descend.descend_speed":0.04553,"descend_to_place.place_offset_z":0.01596,"descend_to_place.place_speed":0.01873,"descend_to_place.place_tolerance":0.00963,"lift.lift_offset_z":0.15772,"lift.lift_speed":0.06699,"retract_after_place.retract_offset_z":0.12587,"retract_after_place.retract_speed":0.12962,"transport_to_goal.transport_offset_z":0.09171,"transport_to_goal.transport_speed":0.14983,"transport_to_goal.transport_tolerance":0.03561},"optimized_scores":{"best_composite_score":-0.18707,"best_fitness_score":0.69293,"best_task_score":0.44096},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.60478,0.16873,-0.00715],"force_p95":1.21015,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5346,"mean_force":0.37492,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61426,0.16629,0.17589]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.50988,0.0377,-0.00117],"force_p95":0.32324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51226,"mean_force":0.0687,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49824,0.03845,0.03931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3737.0,"contact_point_centroid":[0.6124,0.1806,0.19507],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34335,"mean_force":0.05317,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61432,0.16164,0.19213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1114.0,"contact_point_centroid":[0.61636,0.18647,0.16442],"force_p95":0.08119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32879,"mean_force":0.05499,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61812,0.16746,0.16152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16958.0,"contact_point_centroid":[0.50195,0.05729,0.08861],"force_p95":0.09358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30027,"mean_force":0.06034,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50024,0.03828,0.08696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4327.0,"contact_point_centroid":[0.61806,0.14294,0.19215],"force_p95":0.06974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28968,"mean_force":0.04745,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61432,0.16164,0.19213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17105.0,"contact_point_centroid":[0.50226,0.01935,0.0914],"force_p95":0.08818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27834,"mean_force":0.05908,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50046,0.03828,0.08968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1350.0,"contact_point_centroid":[0.6219,0.14878,0.1609],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27518,"mean_force":0.04656,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61815,0.16747,0.16157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5664.0,"contact_point_centroid":[0.56636,0.0837,0.18479],"force_p95":0.10713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27239,"mean_force":0.0638,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56196,0.10226,0.18399]},{"body_a":"world","body_b":"grasp_target","contact_count":1011.0,"contact_point_centroid":[0.59863,0.16986,-0.00207],"force_p95":0.21055,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25178,"mean_force":0.12872,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61795,0.16852,0.21995]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03953,-0.0021],"force_p95":0.15157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21725,"mean_force":0.13023,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50091,0.0387,0.039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5151.0,"contact_point_centroid":[0.56209,0.12035,0.18538],"force_p95":0.10842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20147,"mean_force":0.06722,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5612,0.10142,0.18346]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50262,0.01786,0.21403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.50015,0.01932,0.04052],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13224,"mean_force":0.05211,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49973,0.0386,0.0377]},{"body_a":"world","body_b":"grasp_target","contact_count":3844.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50639,0.0382,0.07293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5455.0,"contact_point_centroid":[0.49946,0.0577,0.04032],"force_p95":0.06781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07385,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49973,0.0386,0.03771]}],"total_contact_groups":16},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59731,0.16989,0.02602],"final_tcp_position":[0.62299,0.17086,0.2515],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.5346,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3844.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50761,0.03642,0.12872],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14685,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11344.0,"raw_peak_contact_force":0.21725,"subtask_id":"grasp_object","tcp_end":[0.50758,0.03925,0.04639],"tcp_start":[0.50761,0.03642,0.12872],"tcp_to_object_dist_end":0.02097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03867,0.02566],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21312,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.09921,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":34235.0,"raw_peak_contact_force":0.51226,"subtask_id":"grasp_object","tcp_end":[0.4997,0.0386,0.03767],"tcp_start":[0.50758,0.03925,0.04639],"tcp_to_object_dist_end":0.01751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,0.03854,0.12594],"object_pos_start":[0.51244,0.03867,0.02566],"object_to_goal_dist_end":0.17512,"object_to_goal_dist_start":0.21312,"object_z_max":0.12584,"peak_contact_force":0.07497,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.27239,"subtask_id":"lift_object","tcp_end":[0.50568,0.03833,0.14678],"tcp_start":[0.4997,0.0386,0.03767],"tcp_to_object_dist_end":0.02345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.61747,0.1585,0.19515],"object_pos_start":[0.51644,0.03854,0.12594],"object_to_goal_dist_end":0.05301,"object_to_goal_dist_start":0.17512,"object_z_max":0.19495,"peak_contact_force":0.0747,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8064.0,"raw_peak_contact_force":0.34335,"subtask_id":"place_at_goal","tcp_end":[0.61092,0.15629,0.21839],"tcp_start":[0.50568,0.03833,0.14678],"tcp_to_object_dist_end":0.02425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.62587,0.17057,0.14134],"object_pos_start":[0.61747,0.1585,0.19515],"object_to_goal_dist_end":0.0045,"object_to_goal_dist_start":0.05301,"object_z_max":0.19529,"peak_contact_force":0.25291,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2652.0,"raw_peak_contact_force":1.5346,"subtask_id":"place_at_goal","tcp_end":[0.62013,0.16792,0.16566],"tcp_start":[0.61092,0.15629,0.21839],"tcp_to_object_dist_end":0.02513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60986,0.16528,0.02633],"object_pos_start":[0.62587,0.17057,0.14134],"object_to_goal_dist_end":0.12022,"object_to_goal_dist_start":0.0045,"object_z_max":0.14134,"peak_contact_force":0.1231,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1011.0,"raw_peak_contact_force":0.25178,"subtask_id":"place_at_goal","tcp_end":[0.61418,0.16627,0.18581],"tcp_start":[0.62013,0.16792,0.16566],"tcp_to_object_dist_end":0.15954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.59731,0.16989,0.02602],"object_pos_start":[0.60986,0.16528,0.02633],"object_to_goal_dist_end":0.12282,"object_to_goal_dist_start":0.12022,"object_z_max":0.02809,"peak_contact_force":0.12262,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.62299,0.17086,0.2515],"tcp_start":[0.61418,0.16627,0.18581],"tcp_to_object_dist_end":0.22694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```