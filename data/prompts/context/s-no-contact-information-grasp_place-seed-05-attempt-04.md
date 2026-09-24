## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1612 | 0.41 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0840 | 0.36 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1692 | 0.39 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

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

## Current Skill (Q=-0.161) — your mutation base

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
  - 0.03
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.06
  weight: 0.3
- id: place_done
  target_entity: object
  metric: goal_progress
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
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
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: duration.max_time
        mode: replace
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
    - -0.005
- id: lift_1
  type: lift
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
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
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
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
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
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_goal
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
    - 0.06
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_goal_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release_goal
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  subtask_id: place_done
- id: retract_goal
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
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_goal_height:
      type: scalar
      range:
      - 0.2
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_done

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - grip_force: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.06], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_goal** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_goal** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_goal_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.161
- **task_score** (E): 0.409
- **fitness_score**: 0.669  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0629 |
| descend_to_grasp | 1.00 | 0.1897 |
| grasp_1 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 0.1480 |
| approach_goal | 1.00 | 0.2323 |
| descend_to_goal | 1.00 | 0.0791 |
| release_goal | 1.00 | 0.0200 |
| retract_goal | 1.00 | 0.2126 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.012, 0.243) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.509, 0.012, 0.243)→(0.511, 0.018, 0.054) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.054)→(0.502, 0.017, 0.044) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.044)→(0.499, 0.017, 0.192) | (0.516, 0.018, 0.026)→(0.508, 0.017, 0.169) | 0.237→0.200 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.192)→(0.598, 0.170, 0.333) | (0.508, 0.017, 0.169)→(0.603, 0.171, 0.304) | 0.200→0.138 |
| descend_to_goal | descend | 1.00 / step_budget | (0.598, 0.170, 0.333)→(0.601, 0.176, 0.254) | (0.603, 0.171, 0.304)→(0.607, 0.176, 0.224) | 0.138→0.057 |
| release_goal | release | 1.00 / step_budget | (0.601, 0.176, 0.254)→(0.597, 0.175, 0.273) | (0.607, 0.176, 0.224)→(0.599, 0.174, 0.008) | 0.057→0.159 |
| retract_goal | retract | 1.00 / step_budget | (0.597, 0.175, 0.273)→(0.606, 0.179, 0.486) | (0.599, 0.174, 0.008)→(0.590, 0.176, 0.023) | 0.159→0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.567
- phase_score: 0.385
- phase_breakdown.reach_object_score: 0.848
- phase_breakdown.reach_goal_score: 0.322
- phase_breakdown.place_done_score: 0.085
- grasp_place_fitness: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: -0.147
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.291


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21726,"average_solve_count":336.0,"average_success_count":336.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.22546,"approach_goal.approach_goal_speed":0.05799,"approach_object.approach_height":0.19286,"approach_object.approach_speed":0.09581,"descend_to_goal.descend_goal_speed":0.03256,"descend_to_goal.place_z_offset":0.10261,"descend_to_grasp.descend_speed":0.06644,"descend_to_grasp.grasp_offset_z":0.01406,"grasp_1.grip_force":12.37263,"lift_1.lift_height":0.18808,"lift_1.lift_speed":0.05195,"retract_goal.retract_goal_height":0.348,"retract_goal.retract_speed":0.11563},"optimized_scores":{"best_composite_score":-0.08201,"best_fitness_score":0.74799,"best_task_score":0.56739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.58731,0.1691,-0.01006],"force_p95":1.48556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64367,"mean_force":0.56536,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59232,0.17386,0.2383]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.52677,0.02927,-0.00151],"force_p95":0.42757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44723,"mean_force":0.14438,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51549,0.02905,0.04528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12917.0,"contact_point_centroid":[0.513,0.04801,0.12635],"force_p95":0.07679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29544,"mean_force":0.05075,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51296,0.02889,0.12404]},{"body_a":"world","body_b":"grasp_target","contact_count":2765.0,"contact_point_centroid":[0.58207,0.16922,-0.00207],"force_p95":0.15167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27611,"mean_force":0.12312,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59554,0.17559,0.34123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11352.0,"contact_point_centroid":[0.51313,0.00969,0.12708],"force_p95":0.07988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26384,"mean_force":0.05585,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51297,0.02889,0.12453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.5991,0.19374,0.21839],"force_p95":0.10414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24226,"mean_force":0.06468,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59534,0.175,0.21971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":890.0,"contact_point_centroid":[0.59865,0.15624,0.21837],"force_p95":0.1159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23896,"mean_force":0.06838,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59531,0.17499,0.21966]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03064,-0.00214],"force_p95":0.15916,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22148,"mean_force":0.13264,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5178,0.02921,0.04538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3038.0,"contact_point_centroid":[0.59852,0.19042,0.2729],"force_p95":0.10165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21886,"mean_force":0.07112,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59512,0.17165,0.27388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2908.0,"contact_point_centroid":[0.59791,0.15291,0.27376],"force_p95":0.10092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19425,"mean_force":0.07168,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59509,0.17159,0.27483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12592.0,"contact_point_centroid":[0.55404,0.11782,0.26403],"force_p95":0.08,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15281,"mean_force":0.05374,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55248,0.09877,0.26289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12664.0,"contact_point_centroid":[0.55346,0.07997,0.26389],"force_p95":0.08093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15234,"mean_force":0.05351,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55262,0.09901,0.26307]},{"body_a":"world","body_b":"grasp_target","contact_count":568.0,"contact_point_centroid":[0.5305,0.03079,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12349,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50929,0.01057,0.27003]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52143,0.026,0.14548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4920.0,"contact_point_centroid":[0.51746,0.00997,0.0469],"force_p95":0.07069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11291,"mean_force":0.04385,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51662,0.02914,0.04403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.51739,0.04845,0.04583],"force_p95":0.07374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0758,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51663,0.02914,0.04404]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58152,0.1691,0.02602],"final_tcp_position":[0.60109,0.17803,0.43611],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5202,0.0225,0.23781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2122,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52505,0.02967,0.05393],"tcp_start":[0.5202,0.0225,0.23781],"tcp_to_object_dist_end":0.02846,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02969,0.02551],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1845,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51659,0.02914,0.044],"tcp_start":[0.52505,0.02967,0.05393],"tcp_to_object_dist_end":0.02311,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.52154,0.02907,0.1893],"object_pos_start":[0.53046,0.02969,0.02551],"object_to_goal_dist_end":0.18801,"object_to_goal_dist_start":0.1845,"object_z_max":0.18904,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51337,0.02892,0.21235],"tcp_start":[0.51659,0.02914,0.044],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.59864,0.16863,0.29069],"object_pos_start":[0.52154,0.02907,0.1893],"object_to_goal_dist_end":0.18289,"object_to_goal_dist_start":0.18801,"object_z_max":0.29056,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59424,0.16858,0.31785],"tcp_start":[0.51337,0.02892,0.21235],"tcp_to_object_dist_end":0.02752,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.60372,0.17551,0.1956],"object_pos_start":[0.59864,0.16863,0.29069],"object_to_goal_dist_end":0.08759,"object_to_goal_dist_start":0.18289,"object_z_max":0.29071,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59723,0.17554,0.22448],"tcp_start":[0.59424,0.16858,0.31785],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59457,0.1729,0.01567],"object_pos_start":[0.60372,0.17551,0.1956],"object_to_goal_dist_end":0.09286,"object_to_goal_dist_start":0.08759,"object_z_max":0.1956,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.59229,0.17385,0.24409],"tcp_start":[0.59723,0.17554,0.22448],"tcp_to_object_dist_end":0.22843,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.58152,0.1691,0.02602],"object_pos_start":[0.59457,0.1729,0.01567],"object_to_goal_dist_end":0.08501,"object_to_goal_dist_start":0.09286,"object_z_max":0.02817,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.60109,0.17803,0.43611],"tcp_start":[0.59229,0.17385,0.24409],"tcp_to_object_dist_end":0.41066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24518,"average_solve_count":363.0,"average_success_count":363.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.14642,"approach_goal.approach_goal_speed":0.04988,"approach_object.approach_height":0.18297,"approach_object.approach_speed":0.1135,"descend_to_goal.descend_goal_speed":0.02542,"descend_to_goal.place_z_offset":0.059,"descend_to_grasp.descend_speed":0.07482,"descend_to_grasp.grasp_offset_z":0.01045,"grasp_1.grip_force":14.51076,"lift_1.lift_height":0.17926,"lift_1.lift_speed":0.04576,"retract_goal.retract_goal_height":0.31798,"retract_goal.retract_speed":0.15374},"optimized_scores":{"best_composite_score":-0.25506,"best_fitness_score":0.57494,"best_task_score":0.21274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":42.0,"contact_point_centroid":[0.58016,0.17257,-0.01422],"force_p95":2.38389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43354,"mean_force":1.60898,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58101,0.18265,0.33709]},{"body_a":"world","body_b":"grasp_target","contact_count":2650.0,"contact_point_centroid":[0.58288,0.19057,-0.00239],"force_p95":0.13099,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17715,"mean_force":0.1273,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.5842,0.18482,0.44257]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.49967,-0.01488,-0.00145],"force_p95":0.42979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45434,"mean_force":0.17078,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48997,-0.01508,0.04249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11071.0,"contact_point_centroid":[0.48724,0.00416,0.11926],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2836,"mean_force":0.05281,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48746,-0.01503,0.11715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11694.0,"contact_point_centroid":[0.48715,-0.03417,0.12007],"force_p95":0.07452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26874,"mean_force":0.05071,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48745,-0.01503,0.11836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":973.0,"contact_point_centroid":[0.58541,0.20249,0.31718],"force_p95":0.08542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1963,"mean_force":0.05327,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58271,0.18355,0.317]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2361.0,"contact_point_centroid":[0.58454,0.19956,0.35359],"force_p95":0.08182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18812,"mean_force":0.05822,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58222,0.18045,0.35247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1085.0,"contact_point_centroid":[0.58438,0.16448,0.31696],"force_p95":0.08792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1866,"mean_force":0.05174,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58266,0.18353,0.31683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01556,-0.00206],"force_p95":0.13998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17811,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49215,-0.01511,0.04265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2406.0,"contact_point_centroid":[0.58362,0.16151,0.35358],"force_p95":0.08351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15219,"mean_force":0.05526,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5822,0.18041,0.3529]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.50382,-0.01567,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49999,-0.00526,0.26759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.49143,0.00419,0.04419],"force_p95":0.07858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13419,"mean_force":0.0522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49101,-0.01509,0.04143]},{"body_a":"world","body_b":"grasp_target","contact_count":1724.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49869,-0.01322,0.14058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21624.0,"contact_point_centroid":[0.53459,0.06589,0.29254],"force_p95":0.06695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10264,"mean_force":0.04459,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5348,0.08497,0.29069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18624.0,"contact_point_centroid":[0.53456,0.10216,0.29116],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10165,"mean_force":0.051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53377,0.08295,0.28878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5393.0,"contact_point_centroid":[0.49077,-0.03415,0.04412],"force_p95":0.06507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08302,"mean_force":0.04074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49101,-0.01509,0.04143]}],"total_contact_groups":16},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58287,0.19048,0.01602],"final_tcp_position":[0.58948,0.18788,0.54643],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50053,-0.01132,0.23176],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20581,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49918,-0.01518,0.05036],"tcp_start":[0.50053,-0.01132,0.23176],"tcp_to_object_dist_end":0.02478,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01507,0.02579],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31202,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49098,-0.01509,0.04139],"tcp_start":[0.49918,-0.01518,0.05036],"tcp_to_object_dist_end":0.02015,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.49639,-0.01513,0.18175],"object_pos_start":[0.50374,-0.01507,0.02579],"object_to_goal_dist_end":0.23159,"object_to_goal_dist_start":0.31202,"object_z_max":0.18148,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48773,-0.01503,0.20109],"tcp_start":[0.49098,-0.01509,0.04139],"tcp_to_object_dist_end":0.02119,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.58562,0.17785,0.35384],"object_pos_start":[0.49639,-0.01513,0.18175],"object_to_goal_dist_end":0.10616,"object_to_goal_dist_start":0.23159,"object_z_max":0.35368,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58144,0.17781,0.37792],"tcp_start":[0.48773,-0.01503,0.20109],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.58989,0.18372,0.29589],"object_pos_start":[0.58562,0.17785,0.35384],"object_to_goal_dist_end":0.04801,"object_to_goal_dist_start":0.10616,"object_z_max":0.35388,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58376,0.18385,0.32123],"tcp_start":[0.58144,0.17781,0.37792],"tcp_to_object_dist_end":0.02607,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58447,0.18207,-0.0133],"object_pos_start":[0.58989,0.18372,0.29589],"object_to_goal_dist_end":0.26149,"object_to_goal_dist_start":0.04801,"object_z_max":0.29589,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.581,0.18265,0.34125],"tcp_start":[0.58376,0.18385,0.32123],"tcp_to_object_dist_end":0.35457,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":664.0,"n_steps_budget":930.0,"object_pos_end":[0.58287,0.19048,0.01602],"object_pos_start":[0.58447,0.18207,-0.0133],"object_to_goal_dist_end":0.23215,"object_to_goal_dist_start":0.26149,"object_z_max":0.01754,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.58948,0.18788,0.54643],"tcp_start":[0.581,0.18265,0.34125],"tcp_to_object_dist_end":0.53046,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30792,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.17439,"approach_goal.approach_goal_speed":0.05436,"approach_object.approach_height":0.21698,"approach_object.approach_speed":0.05349,"descend_to_goal.descend_goal_speed":0.03144,"descend_to_goal.place_z_offset":0.05785,"descend_to_grasp.descend_speed":0.07564,"descend_to_grasp.grasp_offset_z":0.01669,"grasp_1.grip_force":18.89062,"lift_1.lift_height":0.13515,"lift_1.lift_speed":0.06091,"retract_goal.retract_goal_height":0.34974,"retract_goal.retract_speed":0.10441},"optimized_scores":{"best_composite_score":-0.14654,"best_fitness_score":0.68346,"best_task_score":0.44538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.60872,0.16806,-0.0084],"force_p95":1.38804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49761,"mean_force":0.43201,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61767,0.16822,0.22752]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.5097,0.03715,-0.00153],"force_p95":0.33775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41801,"mean_force":0.10405,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49826,0.03741,0.04879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7882.0,"contact_point_centroid":[0.49657,0.05631,0.10415],"force_p95":0.08788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29874,"mean_force":0.05681,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49582,0.03721,0.10297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1555.0,"contact_point_centroid":[0.62532,0.18553,0.25439],"force_p95":0.14045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28862,"mean_force":0.11292,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62045,0.16735,0.25884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1705.0,"contact_point_centroid":[0.62502,0.14921,0.25749],"force_p95":0.1234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28491,"mean_force":0.10044,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62033,0.16723,0.26091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7369.0,"contact_point_centroid":[0.49617,0.01808,0.10544],"force_p95":0.08641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26812,"mean_force":0.05894,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4958,0.03721,0.10454]},{"body_a":"world","body_b":"grasp_target","contact_count":3617.0,"contact_point_centroid":[0.60476,0.1685,-0.00203],"force_p95":0.13639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25921,"mean_force":0.12388,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62154,0.16983,0.35535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.62573,0.15082,0.20733],"force_p95":0.1163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23393,"mean_force":0.08449,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62087,0.16936,0.21144]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03959,-0.00218],"force_p95":0.17146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22906,"mean_force":0.13547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50059,0.03761,0.04867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":661.0,"contact_point_centroid":[0.62604,0.18774,0.2069],"force_p95":0.11044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22828,"mean_force":0.07704,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62086,0.16935,0.21143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10419.0,"contact_point_centroid":[0.55252,0.11248,0.22172],"force_p95":0.12368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16628,"mean_force":0.07652,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54905,0.09413,0.22316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9411.0,"contact_point_centroid":[0.55062,0.07423,0.21962],"force_p95":0.13282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15351,"mean_force":0.08546,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54775,0.09277,0.22168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4322.0,"contact_point_centroid":[0.49969,0.01835,0.04854],"force_p95":0.07732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14031,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03752,0.0474]},{"body_a":"world","body_b":"grasp_target","contact_count":428.0,"contact_point_centroid":[0.51251,0.03972,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12379,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5025,0.01185,0.28131]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50573,0.03199,0.15801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.50023,0.05675,0.04866],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0797,"mean_force":0.0454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49946,0.03752,0.04741]}],"total_contact_groups":16},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6043,0.1685,0.02602],"final_tcp_position":[0.62837,0.1724,0.47495],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":108.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50607,0.02606,0.26005],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23452,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50763,0.03814,0.05669],"tcp_start":[0.50607,0.02606,0.26005],"tcp_to_object_dist_end":0.0311,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03828,0.02537],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21349,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49942,0.03751,0.04737],"tcp_start":[0.50763,0.03814,0.05669],"tcp_to_object_dist_end":0.0256,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50635,0.03783,0.13741],"object_pos_start":[0.5125,0.03828,0.02537],"object_to_goal_dist_end":0.18137,"object_to_goal_dist_start":0.21349,"object_z_max":0.13714,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49578,0.03721,0.16307],"tcp_start":[0.49942,0.03751,0.04737],"tcp_to_object_dist_end":0.02776,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.62389,0.16562,0.26845],"object_pos_start":[0.50635,0.03783,0.13741],"object_to_goal_dist_end":0.12368,"object_to_goal_dist_start":0.18137,"object_z_max":0.26833,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61908,0.1651,0.30294],"tcp_start":[0.49578,0.03721,0.16307],"tcp_to_object_dist_end":0.03482,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.62773,0.16987,0.17984],"object_pos_start":[0.62389,0.16562,0.26845],"object_to_goal_dist_end":0.03492,"object_to_goal_dist_start":0.12368,"object_z_max":0.26848,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62279,0.1699,0.2165],"tcp_start":[0.61908,0.1651,0.30294],"tcp_to_object_dist_end":0.03699,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61692,0.16725,0.02224],"object_pos_start":[0.62773,0.16987,0.17984],"object_to_goal_dist_end":0.12336,"object_to_goal_dist_start":0.03492,"object_z_max":0.17984,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61765,0.16821,0.23509],"tcp_start":[0.62279,0.1699,0.2165],"tcp_to_object_dist_end":0.21285,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.6043,0.1685,0.02602],"object_pos_start":[0.61692,0.16725,0.02224],"object_to_goal_dist_end":0.12132,"object_to_goal_dist_start":0.12336,"object_z_max":0.0287,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.62837,0.1724,0.47495],"tcp_start":[0.61765,0.16821,0.23509],"tcp_to_object_dist_end":0.44959,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```