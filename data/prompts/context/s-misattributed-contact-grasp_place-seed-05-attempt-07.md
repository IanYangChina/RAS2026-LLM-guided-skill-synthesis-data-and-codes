## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.1377 | 0.35 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.33 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 3 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.138) — your mutation base

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
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.4
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
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.03
      - 0.06
      default: 0.04
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
  control: position_control
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
    lift_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
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
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: lift_object
- id: approach_goal_1
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal1_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    goal1_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: approach_goal_2
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal2_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    goal2_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: descend_to_place
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
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.04], tolerance=0.005
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal1_offset_z: status=consumed; consumers=target.offset.z (replace)
    - goal1_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal2_offset_z: status=consumed; consumers=target.offset.z (replace)
    - goal2_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.138
- **task_score** (E): 0.354
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1541 |
| descend | 1.00 | 1.00 | 0.0979 |
| grasp | 1.00 | 1.00 | 0.0118 |
| lift | 1.00 | 1.00 | 0.0972 |
| approach_goal_1 | 0.00 | 0.67 | 0.0773 |
| approach_goal_2 | 0.33 | 1.00 | 0.0732 |
| descend_to_place | 1.00 | 1.00 | 0.0464 |
| release | 1.00 | 1.00 | 0.0214 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.151) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend | descend | 1.00 / step_budget | (0.510, 0.016, 0.151)→(0.511, 0.018, 0.053) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 46.000 | 0.139 | 0.189 |
| grasp | grasp | 1.00 / step_budget | (0.511, 0.018, 0.053)→(0.503, 0.018, 0.044) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 32.000 | 0.093 | 0.429 |
| lift | lift | 1.00 / step_budget | (0.503, 0.018, 0.044)→(0.510, 0.018, 0.141) | (0.516, 0.018, 0.026)→(0.518, 0.018, 0.116) | 0.236→0.198 | 1.00 / 21.667 | 0.127 | 0.160 |
| approach_goal_1 | approach | 0.00 / step_budget | (0.510, 0.018, 0.141)→(0.539, 0.074, 0.183) | (0.518, 0.018, 0.116)→(0.543, 0.074, 0.151) | 0.198→0.131 | 0.67 / 5.667 | 91001.915 | 1.110 |
| approach_goal_2 | approach | 0.33 / step_budget | (0.539, 0.074, 0.183)→(0.571, 0.130, 0.209) | (0.543, 0.074, 0.151)→(0.573, 0.115, 0.057) | 0.131→0.143 | 1.00 / 8.333 | 94251.343 | 0.616 |
| descend_to_place | descend | 1.00 / step_budget | (0.571, 0.130, 0.209)→(0.593, 0.166, 0.199) | (0.573, 0.115, 0.057)→(0.575, 0.109, 0.016) | 0.143→0.170 | 1.00 / 4.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.593, 0.166, 0.199)→(0.588, 0.165, 0.219) | (0.575, 0.109, 0.016)→(0.575, 0.109, 0.016) | 0.170→0.170 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.524
- phase_score: 0.413
- phase_breakdown.approach_object_score: 0.159
- phase_breakdown.place_at_goal_score: 0.276
- phase_breakdown.grasp_object_score: 0.558
- phase_breakdown.lift_object_score: 0.797
- grasp_place_fitness: 0.727

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.727
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.524
- **Median Q (composite search score)**: -0.132
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.379


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.goal1_offset_z":0.11723,"approach_goal_1.goal1_speed":0.02697,"approach_goal_2.goal2_offset_z":0.07039,"approach_goal_2.goal2_speed":0.05304,"approach_object.approach_offset_z":0.18646,"approach_object.approach_speed":0.05091,"descend.descend_offset_z":0.03031,"descend.descend_speed":0.07937,"descend_to_place.place_offset_z":0.0504,"descend_to_place.place_speed":0.04393,"lift.lift_offset_z":0.12529,"lift.lift_speed":0.06853},"optimized_scores":{"best_composite_score":-0.05277,"best_fitness_score":0.72723,"best_task_score":0.52388},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.5819,0.15525,-0.00266],"force_p95":0.36436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27158,"mean_force":0.14995,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.57823,0.14237,0.16645]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.52841,0.0296,-0.0012],"force_p95":0.24514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44158,"mean_force":0.064,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51596,0.02974,0.04552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15816.0,"contact_point_centroid":[0.52121,0.04868,0.09116],"force_p95":0.08753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28614,"mean_force":0.05745,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51929,0.02967,0.08932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15725.0,"contact_point_centroid":[0.5206,0.01067,0.08976],"force_p95":0.09233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2721,"mean_force":0.05722,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51913,0.02966,0.08807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5146.0,"contact_point_centroid":[0.56641,0.09346,0.15969],"force_p95":0.12342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23887,"mean_force":0.10263,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.56154,0.11173,0.16367]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03068,-0.00208],"force_p95":0.14421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19968,"mean_force":0.12892,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51864,0.02994,0.04538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13162.0,"contact_point_centroid":[0.54207,0.07868,0.15134],"force_p95":0.11051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15701,"mean_force":0.07005,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.53757,0.06017,0.15181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12025.0,"contact_point_centroid":[0.54157,0.04134,0.15082],"force_p95":0.12013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15322,"mean_force":0.0769,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.53747,0.05998,0.15171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.51745,0.01068,0.04735],"force_p95":0.07078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13895,"mean_force":0.04408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51744,0.02986,0.04399]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51031,0.01283,0.26041]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5499.0,"contact_point_centroid":[0.56714,0.13078,0.15938],"force_p95":0.12129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13537,"mean_force":0.09599,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.56202,0.11267,0.16368]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52321,0.02864,0.12485]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.58192,0.15529,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58826,0.16338,0.15527]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58192,0.15529,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59206,0.17443,0.15161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.51798,0.04912,0.0458],"force_p95":0.07135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07557,"mean_force":0.04502,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51744,0.02986,0.04399]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1083.0,"contact_point_centroid":[0.57967,0.14423,0.16883],"force_p95":0.01249,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01619,"mean_force":0.0108,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.57926,0.14421,0.16665]}],"total_contact_groups":18},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58192,0.15529,0.01602],"final_tcp_position":[0.59641,0.1758,0.15068],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273005.62196,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.52319,0.02652,0.22158],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14159,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11619.0,"raw_peak_contact_force":0.19968,"subtask_id":"grasp_object","tcp_end":[0.52546,0.03039,0.05334],"tcp_start":[0.52319,0.02652,0.22158],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03005,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18413,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.10387,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":31733.0,"raw_peak_contact_force":0.44158,"subtask_id":"grasp_object","tcp_end":[0.51741,0.02986,0.04395],"tcp_start":[0.52546,0.03039,0.05334],"tcp_to_object_dist_end":0.02242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":883.0,"n_steps_budget":990.0,"object_pos_end":[0.53576,0.02993,0.11482],"object_pos_start":[0.53043,0.03005,0.0257],"object_to_goal_dist_end":0.16269,"object_to_goal_dist_start":0.18413,"object_z_max":0.11474,"peak_contact_force":0.13789,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25187.0,"raw_peak_contact_force":0.15701,"subtask_id":"lift_object","tcp_end":[0.5257,0.02977,0.14024],"tcp_start":[0.51741,0.02986,0.04395],"tcp_to_object_dist_end":0.02734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5569,0.08892,0.13361],"object_pos_start":[0.53576,0.02993,0.11482],"object_to_goal_dist_end":0.10336,"object_to_goal_dist_start":0.16269,"object_z_max":0.1336,"peak_contact_force":273005.62196,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13052.0,"raw_peak_contact_force":1.27158,"subtask_id":"place_at_goal","tcp_end":[0.55178,0.0881,0.16713],"tcp_start":[0.5257,0.02977,0.14024],"tcp_to_object_dist_end":0.03392,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58192,0.15529,0.01602],"object_pos_start":[0.5569,0.08892,0.13361],"object_to_goal_dist_end":0.09697,"object_to_goal_dist_start":0.10336,"object_z_max":0.13361,"peak_contact_force":0.12263,"phase_name":"approach_goal_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8253.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58262,0.15032,0.1673],"tcp_start":[0.55178,0.0881,0.16713],"tcp_to_object_dist_end":0.15137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58192,0.15529,0.01602],"object_pos_start":[0.58192,0.15529,0.01602],"object_to_goal_dist_end":0.09697,"object_to_goal_dist_start":0.09697,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.59641,0.1758,0.15068],"tcp_start":[0.58262,0.15032,0.1673],"tcp_to_object_dist_end":0.13698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58192,0.15529,0.01602],"object_pos_start":[0.58192,0.15529,0.01602],"object_to_goal_dist_end":0.09697,"object_to_goal_dist_start":0.09697,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.59036,0.17386,0.17127],"tcp_start":[0.59641,0.1758,0.15068],"tcp_to_object_dist_end":0.15659,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48293,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.goal1_offset_z":0.10478,"approach_goal_1.goal1_speed":0.07106,"approach_goal_2.goal2_offset_z":0.1007,"approach_goal_2.goal2_speed":0.07508,"approach_object.approach_offset_z":0.05645,"approach_object.approach_speed":0.06078,"descend.descend_offset_z":0.03113,"descend.descend_speed":0.04107,"descend_to_place.place_offset_z":0.04109,"descend_to_place.place_speed":0.07308,"lift.lift_offset_z":0.13231,"lift.lift_speed":0.06566},"optimized_scores":{"best_composite_score":-0.22813,"best_fitness_score":0.55187,"best_task_score":0.17437},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2679.0,"contact_point_centroid":[0.55149,0.07122,-0.0024],"force_p95":0.1309,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81352,"mean_force":0.1418,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.54156,0.09456,0.24758]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.50165,-0.01531,-0.0011],"force_p95":0.23673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40817,"mean_force":0.06003,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48998,-0.01543,0.04665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16503.0,"contact_point_centroid":[0.49446,0.00371,0.09371],"force_p95":0.09898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27028,"mean_force":0.05942,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49282,-0.01536,0.09213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18382.0,"contact_point_centroid":[0.49431,-0.03432,0.09365],"force_p95":0.08539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26851,"mean_force":0.05378,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49284,-0.01536,0.09228]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.53323,0.08092,0.21273],"force_p95":0.13421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21825,"mean_force":0.11071,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.52729,0.0627,0.21644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11088.0,"contact_point_centroid":[0.51489,0.03623,0.1753],"force_p95":0.13144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19365,"mean_force":0.08286,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.51001,0.01767,0.17601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12337.0,"contact_point_centroid":[0.51443,-0.00065,0.17517],"force_p95":0.11946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19212,"mean_force":0.07519,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.51009,0.01784,0.17618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2137.0,"contact_point_centroid":[0.53282,0.04489,0.21251],"force_p95":0.12363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18268,"mean_force":0.09823,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.52733,0.06282,0.21654]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0156,-0.00203],"force_p95":0.1311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16035,"mean_force":0.12524,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49239,-0.01547,0.04626]},{"body_a":"world","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49855,-0.00718,0.19721]},{"body_a":"world","body_b":"grasp_target","contact_count":2420.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49793,-0.01521,0.06631]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55154,0.07119,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56094,0.1393,0.26742]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55154,0.07119,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57113,0.16452,0.27627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5094.0,"contact_point_centroid":[0.49063,0.00386,0.04882],"force_p95":0.06539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08364,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49123,-0.01545,0.04501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5850.0,"contact_point_centroid":[0.49075,-0.03468,0.04821],"force_p95":0.06003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07746,"mean_force":0.038,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49123,-0.01545,0.04501]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2639.0,"contact_point_centroid":[0.54256,0.09596,0.25126],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01574,"mean_force":0.01054,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.54221,0.09595,0.24899]}],"total_contact_groups":18},"final_pose_error":0.0294,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55154,0.07119,0.01602],"final_tcp_position":[0.57383,0.16539,0.27483],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.73221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.4994,-0.01456,0.09533],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13015,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12744.0,"raw_peak_contact_force":0.16035,"subtask_id":"grasp_object","tcp_end":[0.49892,-0.01556,0.05339],"tcp_start":[0.4994,-0.01456,0.09533],"tcp_to_object_dist_end":0.02781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.0154,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31218,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.10142,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":35046.0,"raw_peak_contact_force":0.40817,"subtask_id":"grasp_object","tcp_end":[0.4912,-0.01545,0.04497],"tcp_start":[0.49892,-0.01556,0.05339],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.50846,-0.01543,0.1214],"object_pos_start":[0.50373,-0.0154,0.02587],"object_to_goal_dist_end":0.25174,"object_to_goal_dist_start":0.31218,"object_z_max":0.12133,"peak_contact_force":0.13531,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23425.0,"raw_peak_contact_force":0.19365,"subtask_id":"lift_object","tcp_end":[0.49924,-0.01533,0.14801],"tcp_start":[0.4912,-0.01545,0.04497],"tcp_to_object_dist_end":0.02816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53007,0.05275,0.17599],"object_pos_start":[0.50846,-0.01543,0.1214],"object_to_goal_dist_end":0.16303,"object_to_goal_dist_start":0.25174,"object_z_max":0.17594,"peak_contact_force":0.12263,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9359.0,"raw_peak_contact_force":1.81352,"subtask_id":"place_at_goal","tcp_end":[0.52531,0.05268,0.21085],"tcp_start":[0.49924,-0.01533,0.14801],"tcp_to_object_dist_end":0.03518,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55154,0.07119,0.01602],"object_pos_start":[0.53007,0.05275,0.17599],"object_to_goal_dist_end":0.26199,"object_to_goal_dist_start":0.16303,"object_z_max":0.18546,"peak_contact_force":9748.73221,"phase_name":"approach_goal_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8273.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.55007,0.11259,0.26583],"tcp_start":[0.52531,0.05268,0.21085],"tcp_to_object_dist_end":0.25322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55154,0.07119,0.01602],"object_pos_start":[0.55154,0.07119,0.01602],"object_to_goal_dist_end":0.26199,"object_to_goal_dist_start":0.26199,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.57383,0.16539,0.27483],"tcp_start":[0.55007,0.11259,0.26583],"tcp_to_object_dist_end":0.27632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55154,0.07119,0.01602],"object_pos_start":[0.55154,0.07119,0.01602],"object_to_goal_dist_end":0.26199,"object_to_goal_dist_start":0.26199,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2668.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.5702,0.16415,0.29614],"tcp_start":[0.57383,0.16539,0.27483],"tcp_to_object_dist_end":0.29573,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.004,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.goal1_offset_z":0.12461,"approach_goal_1.goal1_speed":0.04678,"approach_goal_2.goal2_offset_z":0.08515,"approach_goal_2.goal2_speed":0.0701,"approach_object.approach_offset_z":0.09753,"approach_object.approach_speed":0.04208,"descend.descend_offset_z":0.03028,"descend.descend_speed":0.03366,"descend_to_place.place_offset_z":0.02776,"descend_to_place.place_speed":0.05409,"lift.lift_offset_z":0.1369,"lift.lift_speed":0.05585},"optimized_scores":{"best_composite_score":-0.13234,"best_fitness_score":0.64766,"best_task_score":0.36265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3774.0,"contact_point_centroid":[0.59072,0.10085,-0.00225],"force_p95":0.12473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60264,"mean_force":0.13402,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59557,0.14354,0.17779]},{"body_a":"world","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.50947,0.03806,-0.00119],"force_p95":0.25357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43735,"mean_force":0.07134,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49836,0.03848,0.04508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20322.0,"contact_point_centroid":[0.50144,0.05754,0.09132],"force_p95":0.07378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28604,"mean_force":0.05017,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50102,0.03841,0.08917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19532.0,"contact_point_centroid":[0.50104,0.01927,0.09133],"force_p95":0.07547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25519,"mean_force":0.05155,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50102,0.03841,0.08915]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8771.0,"contact_point_centroid":[0.56383,0.12287,0.1766],"force_p95":0.13483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2459,"mean_force":0.10071,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.56038,0.10444,0.1804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10867.0,"contact_point_centroid":[0.56148,0.08526,0.17687],"force_p95":0.12544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23466,"mean_force":0.08094,"phase_index":5.0,"phase_name":"approach_goal_2","phase_type":"approach","tcp_position_centroid":[0.5594,0.10338,0.17982]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51253,0.0396,-0.00209],"force_p95":0.14759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2063,"mean_force":0.12949,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50105,0.03873,0.04467]},{"body_a":"world","body_b":"grasp_target","contact_count":2304.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50258,0.01777,0.21749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17748.0,"contact_point_centroid":[0.52405,0.08002,0.15272],"force_p95":0.08976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12847,"mean_force":0.05482,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.52291,0.06093,0.15205]},{"body_a":"world","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50652,0.03824,0.07765]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59069,0.10078,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6053,0.15616,0.17148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.49974,0.01939,0.04644],"force_p95":0.06827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1166,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49987,0.03863,0.04337]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19542.0,"contact_point_centroid":[0.52265,0.04276,0.1532],"force_p95":0.07477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09253,"mean_force":0.04948,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.52363,0.06173,0.15281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5445.0,"contact_point_centroid":[0.49957,0.05791,0.04587],"force_p95":0.06757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0702,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49988,0.03863,0.04337]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3741.0,"contact_point_centroid":[0.59709,0.1445,0.1794],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01057,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59649,0.14448,0.17723]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.60866,0.15703,0.17029],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00999,"phase_index":7.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60804,0.157,0.16784]}],"total_contact_groups":16},"final_pose_error":0.02373,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59069,0.10078,0.01602],"final_tcp_position":[0.60945,0.15733,0.17082],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273005.17374,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_object","tcp_end":[0.50758,0.03632,0.13545],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14432,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12308.0,"raw_peak_contact_force":0.2063,"subtask_id":"grasp_object","tcp_end":[0.50766,0.03927,0.05207],"tcp_start":[0.50758,0.03632,0.13545],"tcp_to_object_dist_end":0.0265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03893,0.02567],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.07363,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":40062.0,"raw_peak_contact_force":0.43735,"subtask_id":"grasp_object","tcp_end":[0.49985,0.03863,0.04333],"tcp_start":[0.50766,0.03927,0.05207],"tcp_to_object_dist_end":0.0217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51102,0.03856,0.11039],"object_pos_start":[0.51244,0.03893,0.02567],"object_to_goal_dist_end":0.1809,"object_to_goal_dist_start":0.21295,"object_z_max":0.1103,"peak_contact_force":0.1087,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37290.0,"raw_peak_contact_force":0.12847,"subtask_id":"lift_object","tcp_end":[0.50597,0.03854,0.13481],"tcp_start":[0.49985,0.03863,0.04333],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54211,0.08094,0.14195],"object_pos_start":[0.51102,0.03856,0.11039],"object_to_goal_dist_end":0.1253,"object_to_goal_dist_start":0.1809,"object_z_max":0.14191,"peak_contact_force":0.0,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19638.0,"raw_peak_contact_force":0.2459,"subtask_id":"place_at_goal","tcp_end":[0.5412,0.08105,0.17163],"tcp_start":[0.50597,0.03854,0.13481],"tcp_to_object_dist_end":0.0297,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58603,0.11765,0.13773],"object_pos_start":[0.54211,0.08094,0.14195],"object_to_goal_dist_end":0.06921,"object_to_goal_dist_start":0.1253,"object_z_max":0.15475,"peak_contact_force":273005.17374,"phase_name":"approach_goal_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7515.0,"raw_peak_contact_force":1.60264,"subtask_id":"place_at_goal","tcp_end":[0.58164,0.12696,0.19387],"tcp_start":[0.5412,0.08105,0.17163],"tcp_to_object_dist_end":0.05708,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59069,0.10078,0.01602],"object_pos_start":[0.58603,0.11765,0.13773],"object_to_goal_dist_end":0.15215,"object_to_goal_dist_start":0.06921,"object_z_max":0.13773,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.60945,0.15733,0.17082],"tcp_start":[0.58164,0.12696,0.19387],"tcp_to_object_dist_end":0.16587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59069,0.10078,0.01602],"object_pos_start":[0.59069,0.10078,0.01602],"object_to_goal_dist_end":0.15215,"object_to_goal_dist_start":0.15215,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.13845,"subtask_id":"place_at_goal","tcp_end":[0.6037,0.15566,0.19103],"tcp_start":[0.60945,0.15733,0.17082],"tcp_to_object_dist_end":0.18387,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```