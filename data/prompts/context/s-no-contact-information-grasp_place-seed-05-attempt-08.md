## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1074 | 0.41 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1079 | 0.41 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.0900 | 0.40 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2159 | 0.40 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1612 | 0.41 | ✅ accepted |

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

## Current Skill (Q=-0.107) — your mutation base

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

- **Composite score**: -0.107
- **task_score** (E): 0.412
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0867 |
| descend_to_grasp | 1.00 | 0.1665 |
| grasp_1 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 0.1095 |
| approach_goal | 0.67 | 0.2421 |
| descend_to_goal | 1.00 | 0.1276 |
| release_goal | 1.00 | 0.0205 |
| retract_goal | 1.00 | 0.2103 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.015, 0.218) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.015, 0.218)→(0.511, 0.018, 0.052) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.052)→(0.502, 0.017, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.042)→(0.499, 0.017, 0.152) | (0.516, 0.017, 0.026)→(0.508, 0.017, 0.133) | 0.237→0.205 |
| approach_goal | approach | 0.67 / step_budget | (0.499, 0.017, 0.152)→(0.594, 0.163, 0.317) | (0.508, 0.017, 0.133)→(0.599, 0.162, 0.293) | 0.205→0.130 |
| descend_to_goal | descend | 1.00 / step_budget | (0.594, 0.163, 0.317)→(0.600, 0.175, 0.192) | (0.599, 0.162, 0.293)→(0.606, 0.175, 0.165) | 0.130→0.011 |
| release_goal | release | 1.00 / step_budget | (0.600, 0.175, 0.192)→(0.594, 0.173, 0.211) | (0.606, 0.175, 0.165)→(0.589, 0.173, 0.019) | 0.011→0.150 |
| retract_goal | retract | 1.00 / step_budget | (0.594, 0.173, 0.211)→(0.605, 0.179, 0.421) | (0.589, 0.173, 0.019)→(0.580, 0.174, 0.026) | 0.150→0.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.566
- phase_score: 0.398
- phase_breakdown.reach_object_score: 0.799
- phase_breakdown.reach_goal_score: 0.102
- phase_breakdown.place_done_score: 0.319
- grasp_place_fitness: 0.751

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.751
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: -0.089
- **K-run variance**: 0.0053
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93886,"average_solve_count":458.0,"average_success_count":458.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.20196,"approach_goal.approach_goal_speed":0.03907,"approach_object.approach_height":0.11724,"approach_object.approach_speed":0.10018,"descend_to_goal.descend_goal_speed":0.01844,"descend_to_goal.descend_z_adjust":0.02218,"descend_to_grasp.descend_speed":0.04393,"descend_to_grasp.grasp_offset_z":0.01079,"lift_1.lift_height":0.13096,"lift_1.lift_speed":0.03007,"retract_goal.retract_goal_height":0.28431,"retract_goal.retract_speed":0.13155},"optimized_scores":{"best_composite_score":-0.02875,"best_fitness_score":0.75125,"best_task_score":0.56646},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.58579,0.17322,-0.00569],"force_p95":1.03751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3062,"mean_force":0.31762,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59027,0.17408,0.15262]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.52665,0.02882,-0.00161],"force_p95":0.38232,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39837,"mean_force":0.17225,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51513,0.02912,0.04133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8522.0,"contact_point_centroid":[0.51274,0.04804,0.09504],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25182,"mean_force":0.05263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51258,0.02896,0.09297]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7730.0,"contact_point_centroid":[0.51285,0.00978,0.09511],"force_p95":0.08369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24367,"mean_force":0.05618,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51259,0.02896,0.09235]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03058,-0.00213],"force_p95":0.16049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22396,"mean_force":0.13265,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51756,0.02929,0.04184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1011.0,"contact_point_centroid":[0.59763,0.15645,0.14108],"force_p95":0.08384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2211,"mean_force":0.05294,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59446,0.17549,0.13957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1117.0,"contact_point_centroid":[0.59731,0.1946,0.14033],"force_p95":0.07722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20758,"mean_force":0.04903,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59446,0.17549,0.13957]},{"body_a":"world","body_b":"grasp_target","contact_count":3080.0,"contact_point_centroid":[0.57875,0.17499,-0.00198],"force_p95":0.12831,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18736,"mean_force":0.12278,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59351,0.17544,0.26801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6374.0,"contact_point_centroid":[0.59755,0.19173,0.22319],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16514,"mean_force":0.05361,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59493,0.17263,0.22208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.51727,0.01,0.04324],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15086,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51637,0.02921,0.04049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6113.0,"contact_point_centroid":[0.59788,0.15358,0.2248],"force_p95":0.07704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14922,"mean_force":0.05463,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59491,0.1726,0.22288]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51045,0.01246,0.23342]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52254,0.02774,0.10753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15930.0,"contact_point_centroid":[0.55434,0.08225,0.22484],"force_p95":0.07252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10424,"mean_force":0.05002,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55312,0.10132,0.22241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15718.0,"contact_point_centroid":[0.55673,0.12474,0.22917],"force_p95":0.07663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10011,"mean_force":0.05055,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5557,0.1056,0.22683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.51722,0.04837,0.04229],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07715,"mean_force":0.04446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51638,0.02921,0.0405]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57874,0.17499,0.02602],"final_tcp_position":[0.6,0.17782,0.37266],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52282,0.02593,0.16454],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13882,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52484,0.02975,0.05036],"tcp_start":[0.52282,0.02593,0.16454],"tcp_to_object_dist_end":0.02501,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02949,0.02554],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18465,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51634,0.02921,0.04046],"tcp_start":[0.52484,0.02975,0.05036],"tcp_to_object_dist_end":0.02053,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.52283,0.02913,0.13417],"object_pos_start":[0.53045,0.02949,0.02554],"object_to_goal_dist_end":0.17091,"object_to_goal_dist_start":0.18465,"object_z_max":0.1339,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51255,0.02896,0.15184],"tcp_start":[0.51634,0.02921,0.04046],"tcp_to_object_dist_end":0.02044,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.60036,0.16983,0.27092],"object_pos_start":[0.52283,0.02913,0.13417],"object_to_goal_dist_end":0.16307,"object_to_goal_dist_start":0.17091,"object_z_max":0.27077,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59473,0.16999,0.29355],"tcp_start":[0.51255,0.02896,0.15184],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.6033,0.17595,0.11933],"object_pos_start":[0.60036,0.16983,0.27092],"object_to_goal_dist_end":0.01168,"object_to_goal_dist_start":0.16307,"object_z_max":0.27096,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59676,0.17616,0.14409],"tcp_start":[0.59473,0.16999,0.29355],"tcp_to_object_dist_end":0.0256,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58233,0.17391,0.02653],"object_pos_start":[0.6033,0.17595,0.11933],"object_to_goal_dist_end":0.08392,"object_to_goal_dist_start":0.01168,"object_z_max":0.11933,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.59017,0.17405,0.16388],"tcp_start":[0.59676,0.17616,0.14409],"tcp_to_object_dist_end":0.13757,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.57874,0.17499,0.02602],"object_pos_start":[0.58233,0.17391,0.02653],"object_to_goal_dist_end":0.08525,"object_to_goal_dist_start":0.08392,"object_z_max":0.02653,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.6,0.17782,0.37266],"tcp_start":[0.59017,0.17405,0.16388],"tcp_to_object_dist_end":0.3473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81798,"average_solve_count":445.0,"average_success_count":445.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.14508,"approach_goal.approach_goal_speed":0.03863,"approach_object.approach_height":0.20948,"approach_object.approach_speed":0.12081,"descend_to_goal.descend_goal_speed":0.01358,"descend_to_goal.descend_z_adjust":0.00735,"descend_to_grasp.descend_speed":0.05098,"descend_to_grasp.grasp_offset_z":0.01495,"lift_1.lift_height":0.10578,"lift_1.lift_speed":0.03128,"retract_goal.retract_goal_height":0.25354,"retract_goal.retract_speed":0.10272},"optimized_scores":{"best_composite_score":-0.20445,"best_fitness_score":0.57555,"best_task_score":0.22434},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.56821,0.1777,-0.01268],"force_p95":1.67745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72407,"mean_force":0.99783,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57651,0.17772,0.28216]},{"body_a":"world","body_b":"grasp_target","contact_count":2797.0,"contact_point_centroid":[0.55859,0.17735,-0.00224],"force_p95":0.14929,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55502,"mean_force":0.12351,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58079,0.18202,0.38445]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.50032,-0.01482,-0.00153],"force_p95":0.35291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38158,"mean_force":0.16378,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48996,-0.01498,0.0467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1089.0,"contact_point_centroid":[0.58002,0.15996,0.2607],"force_p95":0.1382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28504,"mean_force":0.06665,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57885,0.17875,0.26124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1135.0,"contact_point_centroid":[0.57964,0.19768,0.25994],"force_p95":0.15067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26691,"mean_force":0.06441,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57888,0.17876,0.2613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6113.0,"contact_point_centroid":[0.48701,0.00431,0.08879],"force_p95":0.07721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24137,"mean_force":0.05438,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48755,-0.01494,0.08738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7024.0,"contact_point_centroid":[0.48722,-0.03407,0.08863],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23272,"mean_force":0.04864,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48755,-0.01494,0.08703]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.0156,-0.00206],"force_p95":0.14187,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18683,"mean_force":0.12766,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49223,-0.015,0.04711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3624.0,"contact_point_centroid":[0.57365,0.18284,0.30572],"force_p95":0.09816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16588,"mean_force":0.06184,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57317,0.16381,0.30624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3838.0,"contact_point_centroid":[0.57465,0.14494,0.30682],"force_p95":0.08304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15454,"mean_force":0.05404,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57312,0.16372,0.30648]},{"body_a":"world","body_b":"grasp_target","contact_count":356.0,"contact_point_centroid":[0.50382,-0.01567,-0.00165],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1241,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50005,-0.00433,0.28083]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49879,-0.01233,0.15604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.4916,0.00427,0.04779],"force_p95":0.07469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11915,"mean_force":0.04967,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4911,-0.01499,0.04588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19928.0,"contact_point_centroid":[0.52718,0.05114,0.23741],"force_p95":0.07349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10691,"mean_force":0.05009,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52669,0.0702,0.23639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18225.0,"contact_point_centroid":[0.52753,0.09003,0.23827],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09865,"mean_force":0.05414,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52704,0.07089,0.23728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5399.0,"contact_point_centroid":[0.49201,-0.03411,0.04833],"force_p95":0.06577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08186,"mean_force":0.04071,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4911,-0.01499,0.04589]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55811,0.17731,0.02602],"final_tcp_position":[0.58701,0.18679,0.48172],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02599],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31225,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5004,-0.00966,0.25802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23213,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02599],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31225,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49921,-0.01508,0.05482],"tcp_start":[0.5004,-0.00966,0.25802],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.0151,0.02575],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49107,-0.01499,0.04585],"tcp_start":[0.49921,-0.01508,0.05482],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.49699,-0.0151,0.11064],"object_pos_start":[0.50374,-0.0151,0.02575],"object_to_goal_dist_end":0.26079,"object_to_goal_dist_start":0.31207,"object_z_max":0.11036,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48727,-0.01492,0.13214],"tcp_start":[0.49107,-0.01499,0.04585],"tcp_to_object_dist_end":0.02359,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57195,0.152,0.31345],"object_pos_start":[0.49699,-0.0151,0.11064],"object_to_goal_dist_end":0.07583,"object_to_goal_dist_start":0.26079,"object_z_max":0.31325,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.56824,0.15229,0.34102],"tcp_start":[0.48727,-0.01492,0.13214],"tcp_to_object_dist_end":0.02782,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.58397,0.17841,0.2368],"object_pos_start":[0.57195,0.152,0.31345],"object_to_goal_dist_end":0.01478,"object_to_goal_dist_start":0.07583,"object_z_max":0.31355,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58054,0.17905,0.26585],"tcp_start":[0.56824,0.15229,0.34102],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57171,0.1783,0.00201],"object_pos_start":[0.58397,0.17841,0.2368],"object_to_goal_dist_end":0.24674,"object_to_goal_dist_start":0.01478,"object_z_max":0.2368,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.57649,0.17772,0.28614],"tcp_start":[0.58054,0.17905,0.26585],"tcp_to_object_dist_end":0.28416,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.55811,0.17731,0.02602],"object_pos_start":[0.57171,0.1783,0.00201],"object_to_goal_dist_end":0.22419,"object_to_goal_dist_start":0.24674,"object_z_max":0.02829,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58701,0.18679,0.48172],"tcp_start":[0.57649,0.17772,0.28614],"tcp_to_object_dist_end":0.45671,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01274,"average_solve_count":471.0,"average_success_count":471.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.18945,"approach_goal.approach_goal_speed":0.05001,"approach_object.approach_height":0.18557,"approach_object.approach_speed":0.1092,"descend_to_goal.descend_goal_speed":0.04403,"descend_to_goal.descend_z_adjust":0.00697,"descend_to_grasp.descend_speed":0.05225,"descend_to_grasp.grasp_offset_z":0.01008,"lift_1.lift_height":0.15016,"lift_1.lift_speed":0.0316,"retract_goal.retract_goal_height":0.28581,"retract_goal.retract_speed":0.05062},"optimized_scores":{"best_composite_score":-0.08913,"best_fitness_score":0.69087,"best_task_score":0.44491},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.61753,0.16898,-0.0081],"force_p95":1.19135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35475,"mean_force":0.45407,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61667,0.16846,0.17409]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.50878,0.03735,-0.00163],"force_p95":0.39917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41179,"mean_force":0.17728,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49813,0.03759,0.04176]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9878.0,"contact_point_centroid":[0.4954,0.05652,0.10518],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26097,"mean_force":0.05089,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49566,0.03739,0.10341]},{"body_a":"world","body_b":"grasp_target","contact_count":3951.0,"contact_point_centroid":[0.60362,0.16938,-0.00201],"force_p95":0.12949,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25095,"mean_force":0.12384,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62013,0.16973,0.29725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9116.0,"contact_point_centroid":[0.49562,0.01819,0.10447],"force_p95":0.07975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24985,"mean_force":0.05348,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49566,0.03739,0.10201]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03946,-0.00217],"force_p95":0.17117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23753,"mean_force":0.13528,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50048,0.03778,0.0421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.62356,0.15074,0.1613],"force_p95":0.08604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19239,"mean_force":0.05683,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62067,0.16978,0.16075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.62355,0.18878,0.16115],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18675,"mean_force":0.0497,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62066,0.16977,0.16074]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6051.0,"contact_point_centroid":[0.62318,0.18657,0.24557],"force_p95":0.07686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18653,"mean_force":0.05546,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62049,0.16752,0.24459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5542.0,"contact_point_centroid":[0.62343,0.14849,0.2469],"force_p95":0.08248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17766,"mean_force":0.05908,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62047,0.1675,0.2453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3805.0,"contact_point_centroid":[0.50042,0.01849,0.04383],"force_p95":0.08632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15762,"mean_force":0.05524,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49932,0.03769,0.04084]},{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.51251,0.03972,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12345,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50301,0.01382,0.26711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17024.0,"contact_point_centroid":[0.55986,0.08456,0.24781],"force_p95":0.07223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12725,"mean_force":0.05008,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55838,0.10366,0.24527]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50616,0.03376,0.14066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17308.0,"contact_point_centroid":[0.56285,0.12609,0.2514],"force_p95":0.07531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11844,"mean_force":0.0493,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56162,0.10695,0.24913]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.50001,0.05683,0.04268],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08066,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03769,0.04085]}],"total_contact_groups":16},"final_pose_error":0.02108,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60336,0.1694,0.02602],"final_tcp_position":[0.62655,0.17191,0.40979],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50699,0.02941,0.23174],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20605,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50757,0.03833,0.0501],"tcp_start":[0.50699,0.02941,0.23174],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.0381,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21359,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4993,0.03769,0.0408],"tcp_start":[0.50757,0.03833,0.0501],"tcp_to_object_dist_end":0.02026,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.50512,0.0374,0.15315],"object_pos_start":[0.51247,0.0381,0.02543],"object_to_goal_dist_end":0.18253,"object_to_goal_dist_start":0.21359,"object_z_max":0.15288,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49576,0.0374,0.17132],"tcp_start":[0.4993,0.03769,0.0408],"tcp_to_object_dist_end":0.02043,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":869.0,"n_steps_budget":1000.0,"object_pos_end":[0.62517,0.16519,0.29465],"object_pos_start":[0.50512,0.0374,0.15315],"object_to_goal_dist_end":0.14983,"object_to_goal_dist_start":0.18253,"object_z_max":0.29452,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61948,0.16535,0.31788],"tcp_start":[0.49576,0.0374,0.17132],"tcp_to_object_dist_end":0.02392,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.62926,0.17011,0.14031],"object_pos_start":[0.62517,0.16519,0.29465],"object_to_goal_dist_end":0.00556,"object_to_goal_dist_start":0.14983,"object_z_max":0.29467,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62287,0.1704,0.16564],"tcp_start":[0.61948,0.16535,0.31788],"tcp_to_object_dist_end":0.02612,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61403,0.16687,0.02741],"object_pos_start":[0.62926,0.17011,0.14031],"object_to_goal_dist_end":0.11853,"object_to_goal_dist_start":0.00556,"object_z_max":0.14031,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61661,0.16844,0.18431],"tcp_start":[0.62287,0.1704,0.16564],"tcp_to_object_dist_end":0.15693,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60336,0.1694,0.02602],"object_pos_start":[0.61403,0.16687,0.02741],"object_to_goal_dist_end":0.12148,"object_to_goal_dist_start":0.11853,"object_z_max":0.02824,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62655,0.17191,0.40979],"tcp_start":[0.61661,0.16844,0.18431],"tcp_to_object_dist_end":0.38448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```