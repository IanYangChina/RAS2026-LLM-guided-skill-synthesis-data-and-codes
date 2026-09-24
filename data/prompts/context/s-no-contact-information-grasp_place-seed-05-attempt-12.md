## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1095 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0727 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1121 | 0.40 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 13 | -0.0441 | 0.39 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1074 | 0.41 | ✅ accepted |

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
  - 0.03
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_done
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
    - 0.0
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
    descend_z_adjust:
      type: scalar
      range:
      - -0.03
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: add
  guards:
  - id: descend_check
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: reach_goal
- id: release_goal
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
  - parameter_bindings: none
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_adjust: status=consumed; consumers=target.offset.z (add)
  - guards:
    - id=descend_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=reduce_speed
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

- **Composite score**: -0.110
- **task_score** (E): 0.407
- **fitness_score**: 0.670  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0839 |
| descend_to_grasp | 1.00 | 0.1706 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1380 |
| approach_goal | 1.00 | 0.2145 |
| descend_to_goal | 1.00 | 0.1185 |
| release_goal | 1.00 | 0.0206 |
| retract_goal | 1.00 | 0.2592 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.012, 0.222) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.509, 0.012, 0.222)→(0.511, 0.018, 0.052) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.052)→(0.502, 0.017, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.042)→(0.499, 0.017, 0.180) | (0.516, 0.018, 0.026)→(0.508, 0.017, 0.160) | 0.237→0.193 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.180)→(0.597, 0.170, 0.290) | (0.508, 0.017, 0.160)→(0.604, 0.170, 0.265) | 0.193→0.098 |
| descend_to_goal | descend | 1.00 / step_budget | (0.597, 0.170, 0.290)→(0.600, 0.177, 0.171) | (0.604, 0.170, 0.265)→(0.608, 0.177, 0.144) | 0.098→0.026 |
| release_goal | release | 1.00 / step_budget | (0.600, 0.177, 0.171)→(0.594, 0.175, 0.191) | (0.608, 0.177, 0.144)→(0.596, 0.175, 0.020) | 0.026→0.148 |
| retract_goal | retract | 1.00 / step_budget | (0.594, 0.175, 0.191)→(0.606, 0.179, 0.450) | (0.596, 0.175, 0.020)→(0.594, 0.172, 0.023) | 0.148→0.147 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.567
- phase_score: 0.538
- phase_breakdown.reach_object_score: 0.795
- phase_breakdown.reach_goal_score: 0.039
- phase_breakdown.place_done_score: 0.720
- grasp_place_fitness: 0.752

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.752
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: -0.096
- **K-run variance**: 0.0053
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41137,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12302,"approach_goal.approach_goal_speed":0.08236,"approach_object.approach_height":0.16151,"approach_object.approach_speed":0.14726,"descend_to_goal.descend_goal_speed":0.02818,"descend_to_goal.descend_z_adjust":-0.02533,"descend_to_grasp.descend_speed":0.08394,"descend_to_grasp.grasp_offset_z":0.01008,"lift_1.lift_height":0.13253,"lift_1.lift_speed":0.05274,"retract_goal.retract_goal_height":0.31196,"retract_goal.retract_speed":0.16625},"optimized_scores":{"best_composite_score":-0.02797,"best_fitness_score":0.75203,"best_task_score":0.56695},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":272.0,"contact_point_centroid":[0.58785,0.17348,-0.00394],"force_p95":0.66585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72427,"mean_force":0.25038,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58829,0.17314,0.10385]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.52646,0.02887,-0.0015],"force_p95":0.4619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48206,"mean_force":0.15642,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51536,0.02912,0.04135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.59821,0.1937,0.09288],"force_p95":0.09354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35572,"mean_force":0.05804,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59294,0.17466,0.0912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1007.0,"contact_point_centroid":[0.59764,0.15585,0.0931],"force_p95":0.0929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3537,"mean_force":0.0571,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59293,0.17466,0.09119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8247.0,"contact_point_centroid":[0.51297,0.04803,0.09586],"force_p95":0.07974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30252,"mean_force":0.05364,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51275,0.02895,0.0938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7490.0,"contact_point_centroid":[0.51308,0.00977,0.09633],"force_p95":0.08389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29811,"mean_force":0.05727,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51277,0.02895,0.09359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3725.0,"contact_point_centroid":[0.59725,0.18975,0.15806],"force_p95":0.10379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26955,"mean_force":0.07459,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59279,0.17093,0.15694]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03057,-0.00213],"force_p95":0.16086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22465,"mean_force":0.13276,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51768,0.02928,0.04145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.59762,0.15232,0.16005],"force_p95":0.10972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1888,"mean_force":0.07636,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5928,0.17088,0.1584]},{"body_a":"world","body_b":"grasp_target","contact_count":3836.0,"contact_point_centroid":[0.57944,0.17386,-0.00199],"force_p95":0.1255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17246,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59243,0.17494,0.25704]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.51735,0.01,0.04285],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15107,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51649,0.0292,0.0401]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.5305,0.03079,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50992,0.01158,0.25505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10215.0,"contact_point_centroid":[0.55294,0.07998,0.18588],"force_p95":0.07899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12837,"mean_force":0.05415,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55165,0.09902,0.18372]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52207,0.02694,0.12866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10242.0,"contact_point_centroid":[0.55282,0.118,0.18554],"force_p95":0.07868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12178,"mean_force":0.05429,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55155,0.09892,0.18362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5012.0,"contact_point_centroid":[0.5173,0.04836,0.04189],"force_p95":0.07378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07773,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02921,0.0401]}],"total_contact_groups":16},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57944,0.17386,0.02602],"final_tcp_position":[0.60064,0.17799,0.40019],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52156,0.02431,0.20796],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18227,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52499,0.02975,0.05],"tcp_start":[0.52156,0.02431,0.20796],"tcp_to_object_dist_end":0.02463,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02947,0.02554],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18466,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51647,0.0292,0.04006],"tcp_start":[0.52499,0.02975,0.05],"tcp_to_object_dist_end":0.02016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.5231,0.02916,0.13524],"object_pos_start":[0.53045,0.02947,0.02554],"object_to_goal_dist_end":0.17093,"object_to_goal_dist_start":0.18466,"object_z_max":0.13498,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51271,0.02895,0.15301],"tcp_start":[0.51647,0.0292,0.04006],"tcp_to_object_dist_end":0.02059,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.60194,0.16766,0.19552],"object_pos_start":[0.5231,0.02916,0.13524],"object_to_goal_dist_end":0.08811,"object_to_goal_dist_start":0.17093,"object_z_max":0.19542,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59211,0.16725,0.2176],"tcp_start":[0.51271,0.02895,0.15301],"tcp_to_object_dist_end":0.02418,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.60456,0.17554,0.07109],"object_pos_start":[0.60194,0.16766,0.19552],"object_to_goal_dist_end":0.03725,"object_to_goal_dist_start":0.08811,"object_z_max":0.19554,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59564,0.17541,0.09582],"tcp_start":[0.59211,0.16725,0.2176],"tcp_to_object_dist_end":0.02629,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57816,0.17386,0.02615],"object_pos_start":[0.60456,0.17554,0.07109],"object_to_goal_dist_end":0.08534,"object_to_goal_dist_start":0.03725,"object_z_max":0.07109,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58811,0.17308,0.11576],"tcp_start":[0.59564,0.17541,0.09582],"tcp_to_object_dist_end":0.09016,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":959.0,"n_steps_budget":1000.0,"object_pos_end":[0.57944,0.17386,0.02602],"object_pos_start":[0.57816,0.17386,0.02615],"object_to_goal_dist_end":0.08512,"object_to_goal_dist_start":0.08534,"object_z_max":0.02615,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.60064,0.17799,0.40019],"tcp_start":[0.58811,0.17308,0.11576],"tcp_to_object_dist_end":0.37479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1671,"average_solve_count":383.0,"average_success_count":383.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12131,"approach_goal.approach_goal_speed":0.07112,"approach_object.approach_height":0.14238,"approach_object.approach_speed":0.10796,"descend_to_goal.descend_goal_speed":0.01792,"descend_to_goal.descend_z_adjust":-0.02417,"descend_to_grasp.descend_speed":0.06301,"descend_to_grasp.grasp_offset_z":0.01009,"lift_1.lift_height":0.20007,"lift_1.lift_speed":0.05358,"retract_goal.retract_goal_height":0.22628,"retract_goal.retract_speed":0.13343},"optimized_scores":{"best_composite_score":-0.20497,"best_fitness_score":0.57503,"best_task_score":0.21222},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.57764,0.18363,-0.01283],"force_p95":1.56531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65437,"mean_force":0.81987,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57859,0.1829,0.25131]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.59924,0.18099,-0.00202],"force_p95":0.12456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53071,"mean_force":0.12237,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.5815,0.18453,0.35517]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50086,-0.01481,-0.0014],"force_p95":0.4049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46089,"mean_force":0.13098,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48975,-0.01513,0.0422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11572.0,"contact_point_centroid":[0.48785,0.00403,0.13165],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30346,"mean_force":0.05626,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48739,-0.01508,0.12921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11964.0,"contact_point_centroid":[0.48783,-0.03416,0.12954],"force_p95":0.07977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2823,"mean_force":0.0549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48738,-0.01508,0.12733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.58575,0.16528,0.23395],"force_p95":0.09261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20903,"mean_force":0.05688,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58146,0.18407,0.23355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":910.0,"contact_point_centroid":[0.58612,0.20303,0.23402],"force_p95":0.09447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20508,"mean_force":0.06091,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58144,0.18406,0.23351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4240.0,"contact_point_centroid":[0.58539,0.19892,0.30142],"force_p95":0.08936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19694,"mean_force":0.06335,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58127,0.18002,0.30012]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01554,-0.00205],"force_p95":0.13693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17044,"mean_force":0.12652,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49204,-0.01515,0.04228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.58503,0.16132,0.29962],"force_p95":0.09131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16475,"mean_force":0.06433,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58132,0.18013,0.29875]},{"body_a":"world","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4997,-0.00599,0.24726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.49135,0.00407,0.04383],"force_p95":0.07722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12842,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4909,-0.01514,0.04106]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49852,-0.01388,0.12058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15822.0,"contact_point_centroid":[0.53642,0.0651,0.29029],"force_p95":0.07351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11973,"mean_force":0.05043,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5345,0.08417,0.28813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15399.0,"contact_point_centroid":[0.53565,0.10205,0.28913],"force_p95":0.076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10122,"mean_force":0.05181,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53387,0.08295,0.28723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.49142,-0.03422,0.04291],"force_p95":0.06932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08863,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4909,-0.01514,0.04106]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59929,0.18102,0.01602],"final_tcp_position":[0.58674,0.18697,0.45441],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50032,-0.0126,0.19147],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16552,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49907,-0.01523,0.04999],"tcp_start":[0.50032,-0.0126,0.19147],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.0151,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31203,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49087,-0.01514,0.04103],"tcp_start":[0.49907,-0.01523,0.04999],"tcp_to_object_dist_end":0.01991,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.4964,-0.01505,0.2014],"object_pos_start":[0.50372,-0.0151,0.02582],"object_to_goal_dist_end":0.22667,"object_to_goal_dist_start":0.31203,"object_z_max":0.20113,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48781,-0.01508,0.22155],"tcp_start":[0.49087,-0.01514,0.04103],"tcp_to_object_dist_end":0.02191,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.58609,0.1764,0.32967],"object_pos_start":[0.4964,-0.01505,0.2014],"object_to_goal_dist_end":0.0823,"object_to_goal_dist_start":0.22667,"object_z_max":0.32954,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58054,0.17652,0.35402],"tcp_start":[0.48781,-0.01508,0.22155],"tcp_to_object_dist_end":0.02498,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.59084,0.18458,0.21157],"object_pos_start":[0.58609,0.1764,0.32967],"object_to_goal_dist_end":0.03687,"object_to_goal_dist_start":0.0823,"object_z_max":0.32968,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58317,0.18459,0.23798],"tcp_start":[0.58054,0.17652,0.35402],"tcp_to_object_dist_end":0.0275,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59318,0.18076,0.01025],"object_pos_start":[0.59084,0.18458,0.21157],"object_to_goal_dist_end":0.23805,"object_to_goal_dist_start":0.03687,"object_z_max":0.21157,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.57856,0.1829,0.25808],"tcp_start":[0.58317,0.18459,0.23798],"tcp_to_object_dist_end":0.24828,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.59929,0.18102,0.01602],"object_pos_start":[0.59318,0.18076,0.01025],"object_to_goal_dist_end":0.23252,"object_to_goal_dist_start":0.23805,"object_z_max":0.01655,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58674,0.18697,0.45441],"tcp_start":[0.57856,0.1829,0.25808],"tcp_to_object_dist_end":0.43861,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.00244,"average_mean_iterations":3.56235,"average_solve_count":409.0,"average_success_count":408.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16821,"approach_goal.approach_goal_speed":0.0596,"approach_object.approach_height":0.22504,"approach_object.approach_speed":0.12879,"descend_to_goal.descend_goal_speed":0.0294,"descend_to_goal.descend_z_adjust":0.02124,"descend_to_grasp.descend_speed":0.03882,"descend_to_grasp.grasp_offset_z":0.01496,"lift_1.lift_height":0.13984,"lift_1.lift_speed":0.04545,"retract_goal.retract_goal_height":0.37919,"retract_goal.retract_speed":0.19358},"optimized_scores":{"best_composite_score":-0.09559,"best_fitness_score":0.68441,"best_task_score":0.44296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.61137,0.1643,-0.00769],"force_p95":1.28231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55634,"mean_force":0.42056,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61674,0.16826,0.18984]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50893,0.03691,-0.00158],"force_p95":0.39906,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42794,"mean_force":0.14609,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49827,0.0374,0.04681]},{"body_a":"world","body_b":"grasp_target","contact_count":3570.0,"contact_point_centroid":[0.60278,0.16179,-0.00206],"force_p95":0.15124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39901,"mean_force":0.12736,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62131,0.16992,0.35173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.62551,0.18768,0.17458],"force_p95":0.10182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29296,"mean_force":0.0619,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62049,0.16952,0.1752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9126.0,"contact_point_centroid":[0.49578,0.0563,0.10426],"force_p95":0.08058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28345,"mean_force":0.05164,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49581,0.0372,0.10241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.62491,0.15081,0.17255],"force_p95":0.13899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2788,"mean_force":0.0866,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62045,0.1695,0.17512]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7921.0,"contact_point_centroid":[0.49532,0.01799,0.10556],"force_p95":0.08357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.257,"mean_force":0.05718,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49581,0.0372,0.10412]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3305.0,"contact_point_centroid":[0.62476,0.18555,0.24],"force_p95":0.10605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24714,"mean_force":0.07417,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61995,0.16723,0.24049]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03958,-0.00218],"force_p95":0.17333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23208,"mean_force":0.13598,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50056,0.03759,0.04682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2735.0,"contact_point_centroid":[0.6239,0.1485,0.24131],"force_p95":0.13474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23206,"mean_force":0.0914,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61988,0.16714,0.24287]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15493.0,"contact_point_centroid":[0.55866,0.12176,0.23218],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15105,"mean_force":0.05228,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55745,0.1027,0.23116]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15399.0,"contact_point_centroid":[0.55755,0.08328,0.23131],"force_p95":0.07994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14219,"mean_force":0.05328,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55712,0.10236,0.2308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4322.0,"contact_point_centroid":[0.4997,0.01828,0.0473],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14197,"mean_force":0.04957,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49941,0.0375,0.04555]},{"body_a":"world","body_b":"grasp_target","contact_count":376.0,"contact_point_centroid":[0.51251,0.03972,-0.00167],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.124,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50259,0.01153,0.28437]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50568,0.03157,0.16057]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5155.0,"contact_point_centroid":[0.50029,0.05671,0.04771],"force_p95":0.07519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07782,"mean_force":0.04331,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49942,0.0375,0.04556]}],"total_contact_groups":16},"final_pose_error":0.02945,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60241,0.16142,0.02602],"final_tcp_position":[0.63001,0.17292,0.49487],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02601],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21223,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50599,0.02526,0.26652],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24104,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02601],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.5076,0.03812,0.05482],"tcp_start":[0.50599,0.02526,0.26652],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03818,0.02534],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21357,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49938,0.0375,0.04552],"tcp_start":[0.5076,0.03812,0.05482],"tcp_to_object_dist_end":0.02407,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.50459,0.0378,0.14259],"object_pos_start":[0.5125,0.03818,0.02534],"object_to_goal_dist_end":0.18243,"object_to_goal_dist_start":0.21357,"object_z_max":0.14232,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49582,0.0372,0.16584],"tcp_start":[0.49938,0.0375,0.04552],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":823.0,"n_steps_budget":1000.0,"object_pos_end":[0.62405,0.16572,0.26855],"object_pos_start":[0.50459,0.0378,0.14259],"object_to_goal_dist_end":0.12376,"object_to_goal_dist_start":0.18243,"object_z_max":0.26843,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61877,0.16502,0.29713],"tcp_start":[0.49582,0.0372,0.16584],"tcp_to_object_dist_end":0.02908,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.62908,0.17094,0.14894],"object_pos_start":[0.62405,0.16572,0.26855],"object_to_goal_dist_end":0.00448,"object_to_goal_dist_start":0.12376,"object_z_max":0.26857,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62263,0.17012,0.18017],"tcp_start":[0.61877,0.16502,0.29713],"tcp_to_object_dist_end":0.03191,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61743,0.17181,0.02482],"object_pos_start":[0.62908,0.17094,0.14894],"object_to_goal_dist_end":0.12064,"object_to_goal_dist_start":0.00448,"object_z_max":0.14894,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61669,0.16824,0.19883],"tcp_start":[0.62263,0.17012,0.18017],"tcp_to_object_dist_end":0.17405,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.60241,0.16142,0.02602],"object_pos_start":[0.61743,0.17181,0.02482],"object_to_goal_dist_end":0.12214,"object_to_goal_dist_start":0.12064,"object_z_max":0.02886,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.63001,0.17292,0.49487],"tcp_start":[0.61669,0.16824,0.19883],"tcp_to_object_dist_end":0.4698,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```