## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1121 | 0.40 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 13 | -0.0441 | 0.39 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1074 | 0.41 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1079 | 0.41 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.0900 | 0.40 | ❌ rejected |

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

## Current Skill (Q=-0.112) — your mutation base

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

- **Composite score**: -0.112
- **task_score** (E): 0.404
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.1162 |
| descend_to_grasp | 1.00 | 0.1361 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1908 |
| approach_goal | 1.00 | 0.1981 |
| descend_to_goal | 1.00 | 0.0476 |
| release_goal | 1.00 | 0.0199 |
| retract_goal | 1.00 | 0.1772 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.015, 0.188) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.015, 0.188)→(0.510, 0.018, 0.052) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.052)→(0.502, 0.017, 0.043) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.043)→(0.499, 0.017, 0.234) | (0.516, 0.018, 0.026)→(0.507, 0.017, 0.211) | 0.237→0.200 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.234)→(0.596, 0.168, 0.302) | (0.507, 0.017, 0.211)→(0.602, 0.168, 0.276) | 0.200→0.110 |
| descend_to_goal | descend | 1.00 / step_budget | (0.596, 0.168, 0.302)→(0.599, 0.173, 0.255) | (0.602, 0.168, 0.276)→(0.606, 0.173, 0.228) | 0.110→0.062 |
| release_goal | release | 1.00 / step_budget | (0.599, 0.173, 0.255)→(0.594, 0.171, 0.274) | (0.606, 0.173, 0.228)→(0.600, 0.169, 0.009) | 0.062→0.160 |
| retract_goal | retract | 1.00 / step_budget | (0.594, 0.171, 0.274)→(0.605, 0.179, 0.451) | (0.600, 0.169, 0.009)→(0.590, 0.172, 0.023) | 0.160→0.148 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.555
- phase_score: 0.378
- phase_breakdown.reach_object_score: 0.791
- phase_breakdown.reach_goal_score: 0.346
- phase_breakdown.place_done_score: 0.094
- grasp_place_fitness: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.555
- **Median Q (composite search score)**: -0.097
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38934,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10885,"approach_goal.approach_goal_speed":0.08921,"approach_object.approach_height":0.10979,"approach_object.approach_speed":0.12555,"descend_to_goal.descend_goal_speed":0.02614,"descend_to_goal.descend_goal_z_offset":0.09018,"descend_to_grasp.descend_speed":0.08542,"descend_to_grasp.grasp_offset_z":0.01021,"lift_1.lift_height":0.18501,"lift_1.lift_speed":0.04989,"retract_goal.retract_goal_height":0.27422,"retract_goal.retract_speed":0.06631},"optimized_scores":{"best_composite_score":-0.03392,"best_fitness_score":0.74608,"best_task_score":0.55514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.58879,0.16784,-0.01186],"force_p95":1.46362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78745,"mean_force":0.72207,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.5862,0.16529,0.21692]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.52628,0.02865,-0.00151],"force_p95":0.45246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4722,"mean_force":0.15543,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51517,0.02911,0.04119]},{"body_a":"world","body_b":"grasp_target","contact_count":2125.0,"contact_point_centroid":[0.5727,0.1666,-0.00213],"force_p95":0.2028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30567,"mean_force":0.12874,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59196,0.17132,0.29754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11586.0,"contact_point_centroid":[0.51303,0.04802,0.12025],"force_p95":0.08022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29573,"mean_force":0.05467,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51262,0.02894,0.11812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10978.0,"contact_point_centroid":[0.51316,0.00982,0.12393],"force_p95":0.08267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29056,"mean_force":0.05652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51264,0.02894,0.12139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.5916,0.18579,0.20167],"force_p95":0.10524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27925,"mean_force":0.05781,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58954,0.16652,0.20027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1158.0,"contact_point_centroid":[0.59166,0.14766,0.20123],"force_p95":0.08318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25464,"mean_force":0.05196,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58957,0.16653,0.20033]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03057,-0.00214],"force_p95":0.16129,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22516,"mean_force":0.13286,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5175,0.02927,0.0413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":355.0,"contact_point_centroid":[0.59272,0.18469,0.20847],"force_p95":0.09537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18214,"mean_force":0.0631,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59069,0.16544,0.2068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":378.0,"contact_point_centroid":[0.59279,0.14644,0.20842],"force_p95":0.08372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17951,"mean_force":0.05691,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5907,0.16547,0.20674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.51724,0.00998,0.0427],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15216,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51631,0.02919,0.03995]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51046,0.01256,0.22979]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52265,0.02782,0.10343]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8506.0,"contact_point_centroid":[0.55243,0.0781,0.20699],"force_p95":0.0767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09896,"mean_force":0.0523,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55104,0.09715,0.20475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8346.0,"contact_point_centroid":[0.55371,0.11863,0.20688],"force_p95":0.07754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09644,"mean_force":0.05327,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5524,0.09954,0.20481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5012.0,"contact_point_centroid":[0.51718,0.04835,0.04174],"force_p95":0.07383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07805,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02919,0.03996]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57133,0.16649,0.02602],"final_tcp_position":[0.59907,0.177,0.36261],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52284,0.02607,0.15742],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13171,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.5248,0.02974,0.04983],"tcp_start":[0.52284,0.02607,0.15742],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02947,0.02554],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18467,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51628,0.02919,0.03992],"tcp_start":[0.5248,0.02974,0.04983],"tcp_to_object_dist_end":0.02019,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.52209,0.02914,0.18617],"object_pos_start":[0.53045,0.02947,0.02554],"object_to_goal_dist_end":0.18639,"object_to_goal_dist_start":0.18467,"object_z_max":0.18591,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51299,0.02897,0.20539],"tcp_start":[0.51628,0.02919,0.03992],"tcp_to_object_dist_end":0.02126,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.59728,0.16434,0.18593],"object_pos_start":[0.52209,0.02914,0.18617],"object_to_goal_dist_end":0.07925,"object_to_goal_dist_start":0.18639,"object_z_max":0.1864,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59066,0.16448,0.20804],"tcp_start":[0.51299,0.02897,0.20539],"tcp_to_object_dist_end":0.02308,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.59923,0.16687,0.18251],"object_pos_start":[0.59728,0.16434,0.18593],"object_to_goal_dist_end":0.07537,"object_to_goal_dist_start":0.07925,"object_z_max":0.18593,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_done","tcp_end":[0.59151,0.16678,0.20456],"tcp_start":[0.59066,0.16448,0.20804],"tcp_to_object_dist_end":0.02337,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58807,0.16006,0.01959],"object_pos_start":[0.59923,0.16687,0.18251],"object_to_goal_dist_end":0.09141,"object_to_goal_dist_start":0.07537,"object_z_max":0.18251,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58616,0.16528,0.22477],"tcp_start":[0.59151,0.16678,0.20456],"tcp_to_object_dist_end":0.20525,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.57133,0.16649,0.02602],"object_pos_start":[0.58807,0.16006,0.01959],"object_to_goal_dist_end":0.08828,"object_to_goal_dist_start":0.09141,"object_z_max":0.02951,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.59907,0.177,0.36261],"tcp_start":[0.58616,0.16528,0.22477],"tcp_to_object_dist_end":0.33789,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.00723,"average_mean_iterations":4.67229,"average_solve_count":415.0,"average_success_count":412.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.17053,"approach_goal.approach_goal_speed":0.06733,"approach_object.approach_height":0.14269,"approach_object.approach_speed":0.08188,"descend_to_goal.descend_goal_speed":0.02482,"descend_to_goal.descend_goal_z_offset":0.02653,"descend_to_grasp.descend_speed":0.07688,"descend_to_grasp.grasp_offset_z":0.01003,"lift_1.lift_height":0.24923,"lift_1.lift_speed":0.03779,"retract_goal.retract_goal_height":0.34448,"retract_goal.retract_speed":0.18245},"optimized_scores":{"best_composite_score":-0.20492,"best_fitness_score":0.57508,"best_task_score":0.21242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.59232,0.18234,-0.01147],"force_p95":1.80719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88966,"mean_force":0.89042,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58061,0.18297,0.30965]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50018,-0.01481,-0.00145],"force_p95":0.4212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43806,"mean_force":0.17472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48983,-0.01512,0.04206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15956.0,"contact_point_centroid":[0.48742,0.00408,0.15464],"force_p95":0.07556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28428,"mean_force":0.05193,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4875,-0.01507,0.15263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16163.0,"contact_point_centroid":[0.48734,-0.03421,0.15291],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26334,"mean_force":0.05158,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48749,-0.01507,0.15108]},{"body_a":"world","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.59725,0.18272,-0.00215],"force_p95":0.12399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25876,"mean_force":0.12024,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58358,0.18475,0.42857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3082.0,"contact_point_centroid":[0.58799,0.19888,0.35515],"force_p95":0.08738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20644,"mean_force":0.06642,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58222,0.17997,0.35302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":785.0,"contact_point_centroid":[0.58871,0.16508,0.29041],"force_p95":0.09979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19229,"mean_force":0.06648,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58268,0.18395,0.28926]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":886.0,"contact_point_centroid":[0.5889,0.2028,0.29108],"force_p95":0.08991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19182,"mean_force":0.05902,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58268,0.18396,0.28927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2942.0,"contact_point_centroid":[0.58769,0.16127,0.35431],"force_p95":0.09,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18546,"mean_force":0.06819,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58225,0.18004,0.352]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01554,-0.00205],"force_p95":0.13732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17092,"mean_force":0.1266,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49203,-0.01515,0.04232]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17168.0,"contact_point_centroid":[0.53548,0.06244,0.33743],"force_p95":0.07016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14841,"mean_force":0.04684,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53387,0.08153,0.33526]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.50382,-0.01567,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49975,-0.00594,0.2478]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15550.0,"contact_point_centroid":[0.53637,0.10171,0.33845],"force_p95":0.07528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13239,"mean_force":0.05139,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53436,0.08252,0.33596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.49134,0.00408,0.04387],"force_p95":0.07727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12808,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49089,-0.01513,0.0411]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49848,-0.01385,0.12096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.49141,-0.03422,0.04294],"force_p95":0.06939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08804,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49089,-0.01513,0.0411]}],"total_contact_groups":16},"final_pose_error":0.04669,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59723,0.18272,0.01602],"final_tcp_position":[0.58905,0.18757,0.54596],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50032,-0.01256,0.19211],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16616,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49906,-0.01522,0.05004],"tcp_start":[0.50032,-0.01256,0.19211],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.0151,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31203,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49086,-0.01513,0.04107],"tcp_start":[0.49906,-0.01522,0.05004],"tcp_to_object_dist_end":0.01995,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.49578,-0.01508,0.2501],"object_pos_start":[0.50372,-0.0151,0.02582],"object_to_goal_dist_end":0.22209,"object_to_goal_dist_start":0.31203,"object_z_max":0.24982,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48824,-0.01509,0.27056],"tcp_start":[0.49086,-0.01513,0.04107],"tcp_to_object_dist_end":0.02181,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.58927,0.17649,0.37911],"object_pos_start":[0.49578,-0.01508,0.2501],"object_to_goal_dist_end":0.13147,"object_to_goal_dist_start":0.22209,"object_z_max":0.37899,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58099,0.17642,0.40309],"tcp_start":[0.48824,-0.01509,0.27056],"tcp_to_object_dist_end":0.02537,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.59385,0.18435,0.26779],"object_pos_start":[0.58927,0.17649,0.37911],"object_to_goal_dist_end":0.02109,"object_to_goal_dist_start":0.13147,"object_z_max":0.37911,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_done","tcp_end":[0.584,0.18436,0.29397],"tcp_start":[0.58099,0.17642,0.40309],"tcp_to_object_dist_end":0.02797,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59473,0.18317,-0.00188],"object_pos_start":[0.59385,0.18435,0.26779],"object_to_goal_dist_end":0.25015,"object_to_goal_dist_start":0.02109,"object_z_max":0.26779,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58059,0.18297,0.31373],"tcp_start":[0.584,0.18436,0.29397],"tcp_to_object_dist_end":0.31593,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":728.0,"n_steps_budget":960.0,"object_pos_end":[0.59723,0.18272,0.01602],"object_pos_start":[0.59473,0.18317,-0.00188],"object_to_goal_dist_end":0.23238,"object_to_goal_dist_start":0.25015,"object_z_max":0.01679,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58905,0.18757,0.54596],"tcp_start":[0.58059,0.18297,0.31373],"tcp_to_object_dist_end":0.53003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29137,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16333,"approach_goal.approach_goal_speed":0.05785,"approach_object.approach_height":0.16829,"approach_object.approach_speed":0.11396,"descend_to_goal.descend_goal_speed":0.03112,"descend_to_goal.descend_goal_z_offset":0.1028,"descend_to_grasp.descend_speed":0.08054,"descend_to_grasp.grasp_offset_z":0.017,"lift_1.lift_height":0.19692,"lift_1.lift_speed":0.05333,"retract_goal.retract_goal_height":0.31898,"retract_goal.retract_speed":0.11972},"optimized_scores":{"best_composite_score":-0.09741,"best_fitness_score":0.68259,"best_task_score":0.44379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.6082,0.16633,-0.01179],"force_p95":1.64976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79523,"mean_force":0.70858,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61672,0.1659,0.27931]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.51001,0.03744,-0.00153],"force_p95":0.37673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41712,"mean_force":0.096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49817,0.03762,0.04879]},{"body_a":"world","body_b":"grasp_target","contact_count":2335.0,"contact_point_centroid":[0.60285,0.16652,-0.00218],"force_p95":0.16915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3966,"mean_force":0.12385,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62126,0.16872,0.3655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.62332,0.18519,0.25654],"force_p95":0.13657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35113,"mean_force":0.09347,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61912,0.16687,0.2602]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.62339,0.14865,0.25691],"force_p95":0.13472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33371,"mean_force":0.09392,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61914,0.16688,0.26026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12052.0,"contact_point_centroid":[0.49656,0.05651,0.13471],"force_p95":0.08456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29552,"mean_force":0.05576,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49589,0.03744,0.13369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.62141,0.18353,0.27953],"force_p95":0.13404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27112,"mean_force":0.10037,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61842,0.16485,0.28314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11466.0,"contact_point_centroid":[0.49614,0.01832,0.1371],"force_p95":0.0857,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26963,"mean_force":0.05786,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49588,0.03744,0.13643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":623.0,"contact_point_centroid":[0.62092,0.14662,0.27965],"force_p95":0.12567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25464,"mean_force":0.08953,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61841,0.16483,0.28323]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.0396,-0.00216],"force_p95":0.16737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22474,"mean_force":0.13437,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03782,0.04877]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.51251,0.03972,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12332,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50305,0.01459,0.25875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4323.0,"contact_point_centroid":[0.49966,0.01854,0.04866],"force_p95":0.07701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13682,"mean_force":0.04955,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49941,0.03773,0.0475]},{"body_a":"world","body_b":"grasp_target","contact_count":1492.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50627,0.0345,0.13566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9497.0,"contact_point_centroid":[0.55099,0.11294,0.25357],"force_p95":0.10578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1179,"mean_force":0.06473,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54964,0.0942,0.25412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9645.0,"contact_point_centroid":[0.55186,0.07712,0.25407],"force_p95":0.10225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11382,"mean_force":0.06499,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55132,0.09592,0.25511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.49992,0.05695,0.04869],"force_p95":0.07465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07689,"mean_force":0.04398,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49942,0.03773,0.04751]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60202,0.16658,0.02602],"final_tcp_position":[0.62732,0.17192,0.44402],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5072,0.03084,0.21499],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18925,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50758,0.03837,0.05678],"tcp_start":[0.5072,0.03084,0.21499],"tcp_to_object_dist_end":0.03118,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03839,0.02542],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21339,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49938,0.03773,0.04747],"tcp_start":[0.50758,0.03837,0.05678],"tcp_to_object_dist_end":0.02566,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.50262,0.03798,0.1975],"object_pos_start":[0.51249,0.03839,0.02542],"object_to_goal_dist_end":0.19096,"object_to_goal_dist_start":0.21339,"object_z_max":0.19724,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49633,0.03747,0.22488],"tcp_start":[0.49938,0.03773,0.04747],"tcp_to_object_dist_end":0.02809,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.61906,0.16332,0.2626],"object_pos_start":[0.50262,0.03798,0.1975],"object_to_goal_dist_end":0.11824,"object_to_goal_dist_start":0.19096,"object_z_max":0.26252,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61702,0.16303,0.29438],"tcp_start":[0.49633,0.03747,0.22488],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.62601,0.16763,0.23336],"object_pos_start":[0.61906,0.16332,0.2626],"object_to_goal_dist_end":0.08848,"object_to_goal_dist_start":0.11824,"object_z_max":0.2626,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_done","tcp_end":[0.62081,0.16727,0.26589],"tcp_start":[0.61702,0.16303,0.29438],"tcp_to_object_dist_end":0.03295,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61635,0.16326,0.0084],"object_pos_start":[0.62601,0.16763,0.23336],"object_to_goal_dist_end":0.13739,"object_to_goal_dist_start":0.08848,"object_z_max":0.23336,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.6167,0.1659,0.28411],"tcp_start":[0.62081,0.16727,0.26589],"tcp_to_object_dist_end":0.27572,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":608.0,"n_steps_budget":960.0,"object_pos_end":[0.60202,0.16658,0.02602],"object_pos_start":[0.61635,0.16326,0.0084],"object_to_goal_dist_end":0.12186,"object_to_goal_dist_start":0.13739,"object_z_max":0.02925,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62732,0.17192,0.44402],"tcp_start":[0.6167,0.1659,0.28411],"tcp_to_object_dist_end":0.4188,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```