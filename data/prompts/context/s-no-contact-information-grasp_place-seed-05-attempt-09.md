## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 13 | -0.0441 | 0.39 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1074 | 0.41 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1079 | 0.41 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.0900 | 0.40 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2159 | 0.40 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.044) — your mutation base

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

- **Composite score**: -0.044
- **task_score** (E): 0.387
- **fitness_score**: 0.661  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0746 |
| descend_to_grasp | 1.00 | 0.1794 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1638 |
| approach_goal | 1.00 | 0.2172 |
| descend_and_place | 1.00 | 0.0009 |
| release_goal | 1.00 | 0.0204 |
| retract_goal | 1.00 | 0.0847 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.015, 0.231) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.509, 0.015, 0.231)→(0.511, 0.018, 0.051) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.051)→(0.502, 0.017, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.042)→(0.499, 0.017, 0.206) | (0.516, 0.018, 0.026)→(0.510, 0.017, 0.185) | 0.237→0.200 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.206)→(0.597, 0.170, 0.319) | (0.510, 0.017, 0.185)→(0.607, 0.170, 0.293) | 0.200→0.126 |
| descend_and_place | descend | 1.00 / force_exceeded | (0.597, 0.170, 0.319)→(0.597, 0.170, 0.318) | (0.607, 0.170, 0.293)→(0.607, 0.170, 0.292) | 0.126→0.125 |
| release_goal | release | 1.00 / step_budget | (0.597, 0.170, 0.318)→(0.594, 0.169, 0.338) | (0.607, 0.170, 0.292)→(0.602, 0.164, 0.002) | 0.125→0.166 |
| retract_goal | retract | 1.00 / step_budget | (0.594, 0.169, 0.338)→(0.604, 0.178, 0.422) | (0.602, 0.164, 0.002)→(0.605, 0.166, 0.016) | 0.166→0.153 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.528
- phase_score: 0.437
- phase_breakdown.reach_object_score: 0.806
- phase_breakdown.reach_goal_score: 0.581
- phase_breakdown.place_done_score: 0.053
- grasp_place_fitness: 0.731

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.731
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.528
- **Median Q (composite search score)**: -0.029
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12705,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.14088,"approach_goal.approach_goal_speed":0.05377,"approach_object.approach_height":0.1924,"approach_object.approach_speed":0.05612,"descend_and_place.descent_distance":0.12068,"descend_and_place.descent_force_threshold":15.0608,"descend_and_place.descent_speed":0.01713,"descend_to_grasp.descend_speed":0.0522,"descend_to_grasp.grasp_offset_z":0.01121,"lift_1.lift_height":0.13325,"lift_1.lift_speed":0.09659,"retract_goal.retract_goal_height":0.23171,"retract_goal.retract_speed":0.08435},"optimized_scores":{"best_composite_score":0.02647,"best_fitness_score":0.73147,"best_task_score":0.52761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.58885,0.15339,-0.00893],"force_p95":1.84924,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00618,"mean_force":0.63047,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58794,0.16684,0.24915]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.52796,0.02882,-0.00143],"force_p95":0.45786,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47392,"mean_force":0.10055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51524,0.02907,0.04244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":677.0,"contact_point_centroid":[0.5963,0.18596,0.22707],"force_p95":0.14991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3826,"mean_force":0.09484,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59081,0.16787,0.2295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":601.0,"contact_point_centroid":[0.59583,0.14925,0.22746],"force_p95":0.24465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32779,"mean_force":0.11083,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59072,0.16784,0.22932]},{"body_a":"world","body_b":"grasp_target","contact_count":1067.0,"contact_point_centroid":[0.59144,0.15365,-0.00218],"force_p95":0.13851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32121,"mean_force":0.11938,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59232,0.17158,0.28697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5455.0,"contact_point_centroid":[0.51564,0.01002,0.09409],"force_p95":0.11086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31157,"mean_force":0.07284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51274,0.0289,0.09181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5758.0,"contact_point_centroid":[0.51561,0.04776,0.09105],"force_p95":0.11056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30626,"mean_force":0.07045,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51278,0.02891,0.08916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.59771,0.14968,0.23311],"force_p95":0.21489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24775,"mean_force":0.11912,"phase_index":5.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.59275,0.16819,0.23441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.59841,0.18623,0.23323],"force_p95":0.19555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24688,"mean_force":0.10197,"phase_index":5.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.59275,0.16819,0.23441]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03058,-0.00214],"force_p95":0.16162,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22474,"mean_force":0.13298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51772,0.02924,0.04231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7217.0,"contact_point_centroid":[0.55579,0.07765,0.19253],"force_p95":0.11108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16263,"mean_force":0.08258,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54999,0.09617,0.19129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.51738,0.00995,0.04371],"force_p95":0.08106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15267,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51653,0.02916,0.04095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7127.0,"contact_point_centroid":[0.55796,0.11843,0.19473],"force_p95":0.1083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15028,"mean_force":0.08285,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55219,0.09986,0.19352]},{"body_a":"world","body_b":"grasp_target","contact_count":608.0,"contact_point_centroid":[0.5305,0.03079,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12343,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50902,0.01055,0.26976]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52135,0.02608,0.14359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51733,0.04832,0.04276],"force_p95":0.07391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07774,"mean_force":0.0444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51654,0.02916,0.04096]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5917,0.15357,0.01602],"final_tcp_position":[0.59788,0.17632,0.32037],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52006,0.02265,0.23693],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21133,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52498,0.0297,0.05083],"tcp_start":[0.52006,0.02265,0.23693],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02946,0.02553],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18468,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.5165,0.02916,0.04092],"tcp_start":[0.52498,0.0297,0.05083],"tcp_to_object_dist_end":0.02078,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":375.0,"n_steps_budget":870.0,"object_pos_end":[0.5287,0.02927,0.13435],"object_pos_start":[0.53046,0.02946,0.02553],"object_to_goal_dist_end":0.16819,"object_to_goal_dist_start":0.18468,"object_z_max":0.13409,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51272,0.02891,0.15478],"tcp_start":[0.5165,0.02916,0.04092],"tcp_to_object_dist_end":0.02594,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.60007,0.16747,0.20723],"object_pos_start":[0.5287,0.02927,0.13435],"object_to_goal_dist_end":0.09977,"object_to_goal_dist_start":0.16819,"object_z_max":0.20713,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59284,0.16786,0.23471],"tcp_start":[0.51272,0.02891,0.15478],"tcp_to_object_dist_end":0.02841,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.59996,0.16815,0.20613],"object_pos_start":[0.60007,0.16747,0.20723],"object_to_goal_dist_end":0.09861,"object_to_goal_dist_start":0.09977,"object_z_max":0.20725,"phase_name":"descend_and_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_done","tcp_end":[0.59254,0.16837,0.23368],"tcp_start":[0.59284,0.16786,0.23471],"tcp_to_object_dist_end":0.02853,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58893,0.1607,0.00288],"object_pos_start":[0.59996,0.16815,0.20613],"object_to_goal_dist_end":0.10746,"object_to_goal_dist_start":0.09861,"object_z_max":0.20613,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58791,0.16683,0.25403],"tcp_start":[0.59254,0.16837,0.23368],"tcp_to_object_dist_end":0.25122,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":269.0,"n_steps_budget":660.0,"object_pos_end":[0.5917,0.15357,0.01602],"object_pos_start":[0.58893,0.1607,0.00288],"object_to_goal_dist_end":0.09591,"object_to_goal_dist_start":0.10746,"object_z_max":0.01704,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.59788,0.17632,0.32037],"tcp_start":[0.58791,0.16683,0.25403],"tcp_to_object_dist_end":0.30526,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2291,"average_solve_count":323.0,"average_success_count":323.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16072,"approach_goal.approach_goal_speed":0.06205,"approach_object.approach_height":0.20734,"approach_object.approach_speed":0.09838,"descend_and_place.descent_distance":0.18706,"descend_and_place.descent_force_threshold":9.97692,"descend_and_place.descent_speed":0.02443,"descend_to_grasp.descend_speed":0.06093,"descend_to_grasp.grasp_offset_z":0.01003,"lift_1.lift_height":0.1873,"lift_1.lift_speed":0.03581,"retract_goal.retract_goal_height":0.25924,"retract_goal.retract_speed":0.15328},"optimized_scores":{"best_composite_score":-0.12982,"best_fitness_score":0.57518,"best_task_score":0.21254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":13.0,"contact_point_centroid":[0.58176,0.16494,-0.00499],"force_p95":2.69717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.71154,"mean_force":1.92212,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58047,0.17775,0.41185]},{"body_a":"world","body_b":"grasp_target","contact_count":1007.0,"contact_point_centroid":[0.59456,0.18149,-0.00374],"force_p95":0.514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4042,"mean_force":0.17963,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58364,0.18215,0.45129]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.50005,-0.01466,-0.00151],"force_p95":0.41113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4325,"mean_force":0.1844,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48997,-0.015,0.04196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.58573,0.19731,0.38985],"force_p95":0.10465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27325,"mean_force":0.06441,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58098,0.17833,0.38831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11945.0,"contact_point_centroid":[0.4871,0.00426,0.12148],"force_p95":0.0772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26814,"mean_force":0.0513,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48749,-0.01495,0.11956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12615.0,"contact_point_centroid":[0.48706,-0.0341,0.12495],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25409,"mean_force":0.04935,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4875,-0.01495,0.12344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.58529,0.19721,0.39298],"force_p95":0.19402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23139,"mean_force":0.10892,"phase_index":5.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.58161,0.17828,0.39221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.58612,0.15978,0.39343],"force_p95":0.18472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22241,"mean_force":0.08974,"phase_index":5.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.58161,0.17828,0.39221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":979.0,"contact_point_centroid":[0.58541,0.15962,0.38967],"force_p95":0.09541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1989,"mean_force":0.06051,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58098,0.17834,0.38833]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01556,-0.00206],"force_p95":0.14217,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18803,"mean_force":0.12779,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4922,-0.01502,0.04235]},{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.50382,-0.01567,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12404,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50005,-0.00441,0.27984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.49146,0.00428,0.0439],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13756,"mean_force":0.05221,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49106,-0.01501,0.04113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19521.0,"contact_point_centroid":[0.53481,0.06282,0.30063],"force_p95":0.07503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13548,"mean_force":0.04909,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53337,0.08186,0.29859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17652.0,"contact_point_centroid":[0.53661,0.10401,0.30402],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12396,"mean_force":0.05372,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53485,0.08484,0.30149]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49872,-0.01241,0.15257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5400.0,"contact_point_centroid":[0.49081,-0.03407,0.04378],"force_p95":0.0654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08012,"mean_force":0.04074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49106,-0.01501,0.04113]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59444,0.18154,0.01602],"final_tcp_position":[0.58676,0.18606,0.48743],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.026],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31225,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50038,-0.00979,0.25608],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23018,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.026],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31225,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49924,-0.01509,0.05007],"tcp_start":[0.50038,-0.00979,0.25608],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01501,0.02576],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49103,-0.01501,0.0411],"tcp_start":[0.49924,-0.01509,0.05007],"tcp_to_object_dist_end":0.01992,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.49631,-0.01471,0.19001],"object_pos_start":[0.50374,-0.01501,0.02576],"object_to_goal_dist_end":0.22903,"object_to_goal_dist_start":0.312,"object_z_max":0.18973,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48785,-0.01495,0.20881],"tcp_start":[0.49103,-0.01501,0.0411],"tcp_to_object_dist_end":0.02062,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.59165,0.17847,0.3685],"object_pos_start":[0.49631,-0.01471,0.19001],"object_to_goal_dist_end":0.12081,"object_to_goal_dist_start":0.22903,"object_z_max":0.36835,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58165,0.17814,0.39221],"tcp_start":[0.48785,-0.01495,0.20881],"tcp_to_object_dist_end":0.02573,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.59174,0.17896,0.36841],"object_pos_start":[0.59165,0.17847,0.3685],"object_to_goal_dist_end":0.12069,"object_to_goal_dist_start":0.12081,"object_z_max":0.36853,"phase_name":"descend_and_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_done","tcp_end":[0.58157,0.17847,0.3921],"tcp_start":[0.58165,0.17814,0.39221],"tcp_to_object_dist_end":0.02579,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58995,0.16989,0.01063],"object_pos_start":[0.59174,0.17896,0.36841],"object_to_goal_dist_end":0.23816,"object_to_goal_dist_start":0.12069,"object_z_max":0.36841,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58046,0.17775,0.4128],"tcp_start":[0.58157,0.17847,0.3921],"tcp_to_object_dist_end":0.40236,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":267.0,"n_steps_budget":600.0,"object_pos_end":[0.59444,0.18154,0.01602],"object_pos_start":[0.58995,0.16989,0.01063],"object_to_goal_dist_end":0.23229,"object_to_goal_dist_start":0.23816,"object_z_max":0.0182,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58676,0.18606,0.48743],"tcp_start":[0.58046,0.17775,0.4128],"tcp_to_object_dist_end":0.4715,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54772,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.19855,"approach_goal.approach_goal_speed":0.07311,"approach_object.approach_height":0.15116,"approach_object.approach_speed":0.10149,"descend_and_place.descent_distance":0.18611,"descend_and_place.descent_force_threshold":17.84952,"descend_and_place.descent_speed":0.02785,"descend_to_grasp.descend_speed":0.0771,"descend_to_grasp.grasp_offset_z":0.01321,"lift_1.lift_height":0.22948,"lift_1.lift_speed":0.0528,"retract_goal.retract_goal_height":0.33236,"retract_goal.retract_speed":0.14844},"optimized_scores":{"best_composite_score":-0.029,"best_fitness_score":0.676,"best_task_score":0.42183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.62219,0.16119,-0.01186],"force_p95":1.92072,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02941,"mean_force":1.11275,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61479,0.1626,0.34428]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.50936,0.03767,-0.00152],"force_p95":0.42383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45594,"mean_force":0.1243,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49814,0.03765,0.04508]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.62866,0.16159,-0.00251],"force_p95":0.12532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45358,"mean_force":0.12091,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62069,0.16703,0.40197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14345.0,"contact_point_centroid":[0.49628,0.05661,0.14835],"force_p95":0.0804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3018,"mean_force":0.05437,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49588,0.03747,0.14617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14164.0,"contact_point_centroid":[0.496,0.01835,0.14778],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26284,"mean_force":0.05437,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49587,0.03747,0.14541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.62349,0.1823,0.32944],"force_p95":0.20255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26066,"mean_force":0.10507,"phase_index":5.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.61737,0.16349,0.32891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.62342,0.14501,0.32949],"force_p95":0.18512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24341,"mean_force":0.08642,"phase_index":5.0,"phase_name":"descend_and_place","phase_type":"descend","tcp_position_centroid":[0.61737,0.16349,0.32891]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03955,-0.00216],"force_p95":0.16531,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22816,"mean_force":0.13429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50048,0.03785,0.04504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10401.0,"contact_point_centroid":[0.55497,0.07875,0.28818],"force_p95":0.09084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19569,"mean_force":0.05906,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55337,0.09766,0.28768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10343.0,"contact_point_centroid":[0.55626,0.11715,0.28872],"force_p95":0.09021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17631,"mean_force":0.05945,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55388,0.09818,0.28801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":835.0,"contact_point_centroid":[0.62221,0.18224,0.32421],"force_p95":0.09826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14459,"mean_force":0.06277,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61631,0.16336,0.32403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":831.0,"contact_point_centroid":[0.62222,0.14464,0.3244],"force_p95":0.0967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14443,"mean_force":0.06187,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61631,0.16336,0.32403]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.51251,0.03972,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50307,0.01512,0.25062]},{"body_a":"world","body_b":"grasp_target","contact_count":1384.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50626,0.03498,0.12581]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.49991,0.01858,0.04675],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11647,"mean_force":0.04354,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03776,0.04377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5044.0,"contact_point_centroid":[0.49989,0.05711,0.04558],"force_p95":0.07489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07741,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49934,0.03776,0.04378]}],"total_contact_groups":16},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6286,0.16159,0.01602],"final_tcp_position":[0.62718,0.17157,0.45753],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50737,0.03179,0.19869],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17293,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50755,0.0384,0.05304],"tcp_start":[0.50737,0.03179,0.19869],"tcp_to_object_dist_end":0.0275,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.0384,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21339,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4993,0.03776,0.04374],"tcp_start":[0.50755,0.0384,0.05304],"tcp_to_object_dist_end":0.02257,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.03771,0.22972],"object_pos_start":[0.51248,0.0384,0.02543],"object_to_goal_dist_end":0.20172,"object_to_goal_dist_start":0.21339,"object_z_max":0.22946,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49652,0.03752,0.25352],"tcp_start":[0.4993,0.03776,0.04374],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.6282,0.16358,0.30198],"object_pos_start":[0.5037,0.03771,0.22972],"object_to_goal_dist_end":0.15722,"object_to_goal_dist_start":0.20172,"object_z_max":0.3019,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61739,0.16324,0.32921],"tcp_start":[0.49652,0.03752,0.25352],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.62857,0.16428,0.30076],"object_pos_start":[0.6282,0.16358,0.30198],"object_to_goal_dist_end":0.15595,"object_to_goal_dist_start":0.15722,"object_z_max":0.30198,"phase_name":"descend_and_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_done","tcp_end":[0.61727,0.16365,0.32819],"tcp_start":[0.61739,0.16324,0.32921],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62617,0.1618,-0.00742],"object_pos_start":[0.62857,0.16428,0.30076],"object_to_goal_dist_end":0.15283,"object_to_goal_dist_start":0.15595,"object_z_max":0.30076,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61479,0.1626,0.34748],"tcp_start":[0.61727,0.16365,0.32819],"tcp_to_object_dist_end":0.35508,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.6286,0.16159,0.01602],"object_pos_start":[0.62617,0.1618,-0.00742],"object_to_goal_dist_end":0.12947,"object_to_goal_dist_start":0.15283,"object_z_max":0.01685,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62718,0.17157,0.45753],"tcp_start":[0.61479,0.1626,0.34748],"tcp_to_object_dist_end":0.44163,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```