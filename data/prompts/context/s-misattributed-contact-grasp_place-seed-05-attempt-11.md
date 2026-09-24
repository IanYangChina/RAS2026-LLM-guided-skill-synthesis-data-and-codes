## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2046 | 0.41 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0765 | 0.40 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0041 | 0.37 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0090 | 0.27 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1377 | 0.35 | ✅ accepted |

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

## Current Skill (Q=-0.205) — your mutation base

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

- **Composite score**: -0.205
- **task_score** (E): 0.412
- **fitness_score**: 0.675  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1634 |
| descend | 1.00 | 1.00 | 0.0912 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 0.67 | 1.00 | 0.0938 |
| transport_to_goal | 1.00 | 1.00 | 0.2160 |
| descend_to_place | 1.00 | 1.00 | 0.0798 |
| release | 1.00 | 1.00 | 0.0215 |
| retract_after_place | 1.00 | 1.00 | 0.1028 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.140) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.511, 0.017, 0.140)→(0.511, 0.018, 0.049) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 43.667 | 0.140 | 0.192 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.049)→(0.503, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.072 | 0.463 |
| lift | lift | 0.67 / step_budget | (0.503, 0.018, 0.040)→(0.508, 0.018, 0.134) | (0.516, 0.018, 0.026)→(0.514, 0.017, 0.112) | 0.237→0.202 | 1.00 / 33.333 | 0.084 | 0.164 |
| transport_to_goal | approach | 1.00 / step_budget | (0.508, 0.018, 0.134)→(0.594, 0.163, 0.263) | (0.514, 0.017, 0.112)→(0.605, 0.166, 0.241) | 0.202→0.075 | 1.00 / 31.000 | 0.084 | 0.350 |
| descend_to_place | descend | 1.00 / step_budget | (0.594, 0.163, 0.263)→(0.600, 0.176, 0.184) | (0.605, 0.166, 0.241)→(0.607, 0.179, 0.159) | 0.075→0.013 | 1.00 / 2.667 | 0.196 | 1.392 |
| release | release | 1.00 / step_budget | (0.600, 0.176, 0.184)→(0.594, 0.174, 0.205) | (0.607, 0.179, 0.159)→(0.590, 0.173, 0.022) | 0.013→0.147 | 1.00 / 4.000 | 0.123 | 0.209 |
| retract_after_place | retract | 1.00 / step_budget | (0.594, 0.174, 0.205)→(0.602, 0.178, 0.308) | (0.590, 0.173, 0.022)→(0.582, 0.171, 0.026) | 0.147→0.144 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.565
- phase_score: 0.357
- phase_breakdown.approach_object_score: 0.683
- phase_breakdown.place_at_goal_score: 0.067
- phase_breakdown.grasp_object_score: 0.633
- phase_breakdown.lift_object_score: 0.819
- grasp_place_fitness: 0.751

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.751
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: -0.184
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06574,"average_solve_count":289.0,"average_success_count":289.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.07483,"approach_object.approach_speed":0.03023,"descend.descend_offset_z":0.02851,"descend.descend_speed":0.07521,"descend_to_place.place_offset_z":0.02759,"descend_to_place.place_speed":0.02679,"descend_to_place.place_tolerance":0.01378,"lift.lift_offset_z":0.13387,"lift.lift_speed":0.06073,"retract_after_place.retract_offset_z":0.15466,"retract_after_place.retract_speed":0.10582,"transport_to_goal.transport_offset_z":0.1136,"transport_to_goal.transport_speed":0.11067,"transport_to_goal.transport_tolerance":0.0323},"optimized_scores":{"best_composite_score":-0.12922,"best_fitness_score":0.75078,"best_task_score":0.56532},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":273.0,"contact_point_centroid":[0.58099,0.1712,-0.0046],"force_p95":1.00427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12809,"mean_force":0.25941,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58882,0.17182,0.15112]},{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.52725,0.02915,-0.00118],"force_p95":0.24477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45062,"mean_force":0.06944,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51575,0.02971,0.04316]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3443.0,"contact_point_centroid":[0.58967,0.18457,0.17541],"force_p95":0.08501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35682,"mean_force":0.06309,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59075,0.16564,0.17322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.59192,0.19214,0.13926],"force_p95":0.08485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34108,"mean_force":0.05648,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59297,0.17312,0.13748]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3399.0,"contact_point_centroid":[0.59641,0.14748,0.17231],"force_p95":0.088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29906,"mean_force":0.06484,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59077,0.16566,0.17318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":955.0,"contact_point_centroid":[0.59876,0.15495,0.13598],"force_p95":0.08689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29756,"mean_force":0.05657,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59294,0.17311,0.13744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18785.0,"contact_point_centroid":[0.52001,0.01048,0.09239],"force_p95":0.07817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28651,"mean_force":0.05331,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51897,0.0296,0.08985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19822.0,"contact_point_centroid":[0.51988,0.04869,0.09217],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28639,"mean_force":0.05123,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.519,0.0296,0.08995]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03063,-0.00208],"force_p95":0.14606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20218,"mean_force":0.12894,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51853,0.02992,0.04283]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.57915,0.16954,-0.00197],"force_p95":0.15354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16792,"mean_force":0.12253,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59191,0.17411,0.20257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5859.0,"contact_point_centroid":[0.55481,0.1124,0.17089],"force_p95":0.0772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15312,"mean_force":0.05419,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55519,0.09335,0.16833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5961.0,"contact_point_centroid":[0.55771,0.07417,0.16944],"force_p95":0.08319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15136,"mean_force":0.05445,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55503,0.09308,0.16816]},{"body_a":"world","body_b":"grasp_target","contact_count":2688.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51077,0.01401,0.20548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.51788,0.01064,0.04423],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13755,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51732,0.02984,0.04144]},{"body_a":"world","body_b":"grasp_target","contact_count":3144.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52352,0.02956,0.07263]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4940.0,"contact_point_centroid":[0.51789,0.04895,0.04326],"force_p95":0.07132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07707,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51732,0.02984,0.04144]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57913,0.16953,0.02602],"final_tcp_position":[0.59717,0.17689,0.24336],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.12809,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3144.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52424,0.02846,0.11218],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14176,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10835.0,"raw_peak_contact_force":0.20218,"subtask_id":"grasp_object","tcp_end":[0.52535,0.03038,0.05075],"tcp_start":[0.52424,0.02846,0.11218],"tcp_to_object_dist_end":0.02526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.02993,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.07687,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":38822.0,"raw_peak_contact_force":0.45062,"subtask_id":"grasp_object","tcp_end":[0.51729,0.02984,0.0414],"tcp_start":[0.52535,0.03038,0.05075],"tcp_to_object_dist_end":0.02046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53037,0.02953,0.11514],"object_pos_start":[0.53042,0.02993,0.02571],"object_to_goal_dist_end":0.16532,"object_to_goal_dist_start":0.18422,"object_z_max":0.11503,"peak_contact_force":0.07904,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11820.0,"raw_peak_contact_force":0.15312,"subtask_id":"lift_object","tcp_end":[0.52448,0.02965,0.13785],"tcp_start":[0.51729,0.02984,0.0414],"tcp_to_object_dist_end":0.02347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.59864,0.16192,0.1804],"object_pos_start":[0.53037,0.02953,0.11514],"object_to_goal_dist_end":0.07426,"object_to_goal_dist_start":0.16532,"object_z_max":0.1802,"peak_contact_force":0.084,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6842.0,"raw_peak_contact_force":0.35682,"subtask_id":"place_at_goal","tcp_end":[0.58894,0.15897,0.20346],"tcp_start":[0.52448,0.02965,0.13785],"tcp_to_object_dist_end":0.02519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.60277,0.17694,0.11622],"object_pos_start":[0.59864,0.16192,0.1804],"object_to_goal_dist_end":0.00839,"object_to_goal_dist_start":0.07426,"object_z_max":0.18056,"peak_contact_force":0.15132,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2170.0,"raw_peak_contact_force":1.12809,"subtask_id":"place_at_goal","tcp_end":[0.59506,0.1736,0.14132],"tcp_start":[0.58894,0.15897,0.20346],"tcp_to_object_dist_end":0.02647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58127,0.16997,0.02645],"object_pos_start":[0.60277,0.17694,0.11622],"object_to_goal_dist_end":0.08456,"object_to_goal_dist_start":0.00839,"object_z_max":0.11622,"peak_contact_force":0.12266,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.16792,"subtask_id":"place_at_goal","tcp_end":[0.58872,0.17179,0.16224],"tcp_start":[0.59506,0.1736,0.14132],"tcp_to_object_dist_end":0.136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":630.0,"object_pos_end":[0.57913,0.16953,0.02602],"object_pos_start":[0.58127,0.16997,0.02645],"object_to_goal_dist_end":0.08555,"object_to_goal_dist_start":0.08456,"object_z_max":0.02654,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2688.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.59717,0.17689,0.24336],"tcp_start":[0.58872,0.17179,0.16224],"tcp_to_object_dist_end":0.21821,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16382,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.13638,"approach_object.approach_speed":0.0636,"descend.descend_offset_z":0.02503,"descend.descend_speed":0.0451,"descend_to_place.place_offset_z":-0.00048,"descend_to_place.place_speed":0.02433,"descend_to_place.place_tolerance":0.00977,"lift.lift_offset_z":0.13038,"lift.lift_speed":0.0562,"retract_after_place.retract_offset_z":0.15592,"retract_after_place.retract_speed":0.09285,"transport_to_goal.transport_offset_z":0.11154,"transport_to_goal.transport_speed":0.12993,"transport_to_goal.transport_tolerance":0.03509},"optimized_scores":{"best_composite_score":-0.30088,"best_fitness_score":0.57912,"best_task_score":0.22531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.58027,0.18235,-0.0142],"force_p95":1.66743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72262,"mean_force":0.94428,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5785,0.18243,0.27041]},{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.50073,-0.0153,-0.00113],"force_p95":0.25135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42692,"mean_force":0.06705,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48966,-0.01539,0.04503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3615.0,"contact_point_centroid":[0.57671,0.19618,0.29674],"force_p95":0.08998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35489,"mean_force":0.06893,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57999,0.1774,0.29614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":887.0,"contact_point_centroid":[0.57759,0.20217,0.25222],"force_p95":0.08864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30931,"mean_force":0.05946,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58123,0.18341,0.25184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":953.0,"contact_point_centroid":[0.58908,0.16608,0.25043],"force_p95":0.08647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28432,"mean_force":0.05622,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58122,0.18341,0.25184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19007.0,"contact_point_centroid":[0.49313,0.00379,0.09146],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27042,"mean_force":0.05296,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49256,-0.01536,0.08907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20593.0,"contact_point_centroid":[0.49309,-0.03446,0.09158],"force_p95":0.07341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26544,"mean_force":0.04932,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4926,-0.01536,0.0894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3967.0,"contact_point_centroid":[0.58795,0.1601,0.2963],"force_p95":0.08602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26388,"mean_force":0.06314,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57995,0.1773,0.29684]},{"body_a":"world","body_b":"grasp_target","contact_count":1450.0,"contact_point_centroid":[0.56566,0.17791,-0.0023],"force_p95":0.21283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24882,"mean_force":0.12946,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58103,0.18437,0.33474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10660.0,"contact_point_centroid":[0.53927,0.05638,0.22997],"force_p95":0.08053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17301,"mean_force":0.05286,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53537,0.07486,0.22933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9340.0,"contact_point_centroid":[0.53368,0.09368,0.23033],"force_p95":0.08734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16798,"mean_force":0.05931,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53527,0.07465,0.22909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01562,-0.00203],"force_p95":0.1312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15711,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49223,-0.01543,0.04465]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49891,-0.00672,0.23809]},{"body_a":"world","body_b":"grasp_target","contact_count":3084.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4978,-0.01473,0.10935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5089.0,"contact_point_centroid":[0.49096,0.00384,0.04654],"force_p95":0.06563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09427,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01541,0.0434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5368.0,"contact_point_centroid":[0.49083,-0.03465,0.04605],"force_p95":0.06388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08125,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01541,0.0434]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56369,0.17729,0.02602],"final_tcp_position":[0.58476,0.18644,0.38436],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.72262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3084.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.49983,-0.01393,0.17521],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1304,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12257.0,"raw_peak_contact_force":0.15711,"subtask_id":"grasp_object","tcp_end":[0.49891,-0.01552,0.0519],"tcp_start":[0.49983,-0.01393,0.17521],"tcp_to_object_dist_end":0.02634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01545,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31222,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.07162,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":39794.0,"raw_peak_contact_force":0.42692,"subtask_id":"grasp_object","tcp_end":[0.49105,-0.01541,0.04337],"tcp_start":[0.49891,-0.01552,0.0519],"tcp_to_object_dist_end":0.0216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5031,-0.01533,0.11033],"object_pos_start":[0.50372,-0.01545,0.02587],"object_to_goal_dist_end":0.25909,"object_to_goal_dist_start":0.31222,"object_z_max":0.11025,"peak_contact_force":0.08778,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20000.0,"raw_peak_contact_force":0.17301,"subtask_id":"lift_object","tcp_end":[0.49779,-0.01538,0.13453],"tcp_start":[0.49105,-0.01541,0.04337],"tcp_to_object_dist_end":0.02477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.59034,0.17561,0.31055],"object_pos_start":[0.5031,-0.01533,0.11033],"object_to_goal_dist_end":0.06364,"object_to_goal_dist_start":0.25909,"object_z_max":0.31022,"peak_contact_force":0.08257,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7582.0,"raw_peak_contact_force":0.35489,"subtask_id":"place_at_goal","tcp_end":[0.57879,0.17182,0.33544],"tcp_start":[0.49779,-0.01538,0.13453],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.58914,0.18685,0.2275],"object_pos_start":[0.59034,0.17561,0.31055],"object_to_goal_dist_end":0.02074,"object_to_goal_dist_start":0.06364,"object_z_max":0.31085,"peak_contact_force":0.2658,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1923.0,"raw_peak_contact_force":1.72262,"subtask_id":"place_at_goal","tcp_end":[0.58273,0.18383,0.25571],"tcp_start":[0.57879,0.17182,0.33544],"tcp_to_object_dist_end":0.02908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57914,0.18247,0.01145],"object_pos_start":[0.58914,0.18685,0.2275],"object_to_goal_dist_end":0.23685,"object_to_goal_dist_start":0.02074,"object_z_max":0.2275,"peak_contact_force":0.12266,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1450.0,"raw_peak_contact_force":0.24882,"subtask_id":"place_at_goal","tcp_end":[0.57847,0.18242,0.27683],"tcp_start":[0.58273,0.18383,0.25571],"tcp_to_object_dist_end":0.26538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":870.0,"object_pos_end":[0.56369,0.17729,0.02602],"object_pos_start":[0.57914,0.18247,0.01145],"object_to_goal_dist_end":0.22354,"object_to_goal_dist_start":0.23685,"object_z_max":0.03054,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.58476,0.18644,0.38436],"tcp_start":[0.57847,0.18242,0.27683],"tcp_to_object_dist_end":0.35907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42045,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.0959,"approach_object.approach_speed":0.07746,"descend.descend_offset_z":0.02215,"descend.descend_speed":0.05537,"descend_to_place.place_offset_z":0.00414,"descend_to_place.place_speed":0.03203,"descend_to_place.place_tolerance":0.01936,"lift.lift_offset_z":0.19982,"lift.lift_speed":0.05672,"retract_after_place.retract_offset_z":0.16956,"retract_after_place.retract_speed":0.0927,"transport_to_goal.transport_offset_z":0.12671,"transport_to_goal.transport_speed":0.09872,"transport_to_goal.transport_tolerance":0.02685},"optimized_scores":{"best_composite_score":-0.18369,"best_fitness_score":0.69631,"best_task_score":0.44482},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.61368,0.16709,-0.00703],"force_p95":1.14701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32659,"mean_force":0.38248,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61544,0.16766,0.16582]},{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.50872,0.03776,-0.0012],"force_p95":0.32573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51159,"mean_force":0.08231,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49802,0.03842,0.03787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4481.0,"contact_point_centroid":[0.61473,0.18239,0.20663],"force_p95":0.09042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33748,"mean_force":0.06405,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61597,0.16357,0.20386]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1155.0,"contact_point_centroid":[0.62401,0.15031,0.15167],"force_p95":0.07576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33231,"mean_force":0.04833,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61941,0.16884,0.15203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1045.0,"contact_point_centroid":[0.61834,0.18781,0.15532],"force_p95":0.08719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3137,"mean_force":0.05182,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61943,0.16885,0.15208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19577.0,"contact_point_centroid":[0.49923,0.05735,0.08412],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30193,"mean_force":0.05191,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49886,0.03825,0.08225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4536.0,"contact_point_centroid":[0.62124,0.14529,0.20379],"force_p95":0.08829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29696,"mean_force":0.06385,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61604,0.16366,0.20299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19237.0,"contact_point_centroid":[0.49939,0.01913,0.08624],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29611,"mean_force":0.05213,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49898,0.03825,0.08407]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03951,-0.0021],"force_p95":0.15196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.217,"mean_force":0.13041,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50085,0.03868,0.03746]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.60394,0.16656,-0.00199],"force_p95":0.15836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.209,"mean_force":0.12355,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61855,0.1692,0.23573]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7614.0,"contact_point_centroid":[0.5574,0.07785,0.18733],"force_p95":0.08617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16654,"mean_force":0.057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55472,0.09669,0.186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7211.0,"contact_point_centroid":[0.55528,0.11696,0.18966],"force_p95":0.08563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14936,"mean_force":0.05877,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5559,0.09796,0.18729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4082.0,"contact_point_centroid":[0.50011,0.01932,0.03897],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14424,"mean_force":0.05209,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49966,0.03858,0.03616]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50264,0.01783,0.21652]},{"body_a":"world","body_b":"grasp_target","contact_count":2832.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50618,0.03796,0.08007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5345.0,"contact_point_centroid":[0.49957,0.05768,0.03863],"force_p95":0.0685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04158,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49966,0.03858,0.03616]}],"total_contact_groups":16},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60373,0.16664,0.02602],"final_tcp_position":[0.62422,0.17137,0.2949],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.32659,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2832.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50757,0.03638,0.13363],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14726,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11227.0,"raw_peak_contact_force":0.217,"subtask_id":"grasp_object","tcp_end":[0.50754,0.03923,0.04485],"tcp_start":[0.50757,0.03638,0.13363],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03863,0.02565],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21315,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.06813,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":39015.0,"raw_peak_contact_force":0.51159,"subtask_id":"grasp_object","tcp_end":[0.49963,0.03858,0.03613],"tcp_start":[0.50754,0.03923,0.04485],"tcp_to_object_dist_end":0.01654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50901,0.03827,0.11143],"object_pos_start":[0.51243,0.03863,0.02565],"object_to_goal_dist_end":0.18224,"object_to_goal_dist_start":0.21315,"object_z_max":0.11133,"peak_contact_force":0.08658,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14825.0,"raw_peak_contact_force":0.16654,"subtask_id":"lift_object","tcp_end":[0.50215,0.03827,0.12945],"tcp_start":[0.49963,0.03858,0.03613],"tcp_to_object_dist_end":0.01928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.62454,0.16164,0.23155],"object_pos_start":[0.50901,0.03827,0.11143],"object_to_goal_dist_end":0.08726,"object_to_goal_dist_start":0.18224,"object_z_max":0.23129,"peak_contact_force":0.08417,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9017.0,"raw_peak_contact_force":0.33748,"subtask_id":"place_at_goal","tcp_end":[0.61292,0.15873,0.24979],"tcp_start":[0.50215,0.03827,0.12945],"tcp_to_object_dist_end":0.02182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.62986,0.17222,0.13469],"object_pos_start":[0.62454,0.16164,0.23155],"object_to_goal_dist_end":0.01059,"object_to_goal_dist_start":0.08726,"object_z_max":0.23179,"peak_contact_force":0.17229,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2384.0,"raw_peak_contact_force":1.32659,"subtask_id":"place_at_goal","tcp_end":[0.6215,0.16938,0.15629],"tcp_start":[0.61292,0.15873,0.24979],"tcp_to_object_dist_end":0.02334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61077,0.16542,0.02686],"object_pos_start":[0.62986,0.17222,0.13469],"object_to_goal_dist_end":0.11957,"object_to_goal_dist_start":0.01059,"object_z_max":0.13469,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.209,"subtask_id":"place_at_goal","tcp_end":[0.61536,0.16764,0.17633],"tcp_start":[0.6215,0.16938,0.15629],"tcp_to_object_dist_end":0.14957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":471.0,"n_steps_budget":930.0,"object_pos_end":[0.60373,0.16664,0.02602],"object_pos_start":[0.61077,0.16542,0.02686],"object_to_goal_dist_end":0.12151,"object_to_goal_dist_start":0.11957,"object_z_max":0.02701,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.62422,0.17137,0.2949],"tcp_start":[0.61536,0.16764,0.17633],"tcp_to_object_dist_end":0.26971,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```