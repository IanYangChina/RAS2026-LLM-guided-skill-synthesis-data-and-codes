## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1079 | 0.41 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.0900 | 0.40 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2159 | 0.40 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1612 | 0.41 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0840 | 0.36 | ❌ rejected |

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

## Current Skill (Q=-0.108) — your mutation base

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
  control: position_control
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
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

- **Composite score**: -0.108
- **task_score** (E): 0.411
- **fitness_score**: 0.672  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0851 |
| descend_to_grasp | 1.00 | 0.1688 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1500 |
| approach_goal | 1.00 | 0.2317 |
| descend_to_goal | 1.00 | 0.1504 |
| release_goal | 1.00 | 0.0205 |
| retract_goal | 0.67 | 0.2357 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.013, 0.220) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.509, 0.013, 0.220)→(0.511, 0.018, 0.052) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.052)→(0.502, 0.017, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.042)→(0.499, 0.017, 0.192) | (0.516, 0.017, 0.026)→(0.508, 0.017, 0.172) | 0.237→0.197 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.192)→(0.598, 0.170, 0.331) | (0.508, 0.017, 0.172)→(0.603, 0.170, 0.305) | 0.197→0.139 |
| descend_to_goal | descend | 1.00 / step_budget | (0.598, 0.170, 0.331)→(0.601, 0.177, 0.181) | (0.603, 0.170, 0.305)→(0.607, 0.177, 0.152) | 0.139→0.015 |
| release_goal | release | 1.00 / step_budget | (0.601, 0.177, 0.181)→(0.595, 0.175, 0.200) | (0.607, 0.177, 0.152)→(0.593, 0.173, 0.021) | 0.015→0.147 |
| retract_goal | retract | 0.67 / step_budget | (0.595, 0.175, 0.200)→(0.604, 0.179, 0.436) | (0.593, 0.173, 0.021)→(0.583, 0.171, 0.026) | 0.147→0.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.567
- phase_score: 0.461
- phase_breakdown.reach_object_score: 0.791
- phase_breakdown.reach_goal_score: 0.746
- phase_breakdown.place_done_score: 0.000
- grasp_place_fitness: 0.752

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.752
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: -0.091
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39024,"average_solve_count":328.0,"average_success_count":328.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.17149,"approach_goal.approach_goal_speed":0.05131,"approach_object.approach_height":0.20818,"approach_object.approach_speed":0.09341,"descend_to_goal.descend_goal_speed":0.04357,"descend_to_grasp.descend_speed":0.07853,"descend_to_grasp.grasp_offset_z":0.01005,"grasp_1.grip_force":6.53456,"lift_1.lift_height":0.15711,"lift_1.lift_speed":0.05074,"retract_goal.retract_goal_height":0.30122,"retract_goal.retract_speed":0.15846},"optimized_scores":{"best_composite_score":-0.02787,"best_fitness_score":0.75213,"best_task_score":0.56659},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":283.0,"contact_point_centroid":[0.58301,0.17198,-0.00411],"force_p95":0.86674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9781,"mean_force":0.25161,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58937,0.17363,0.12954]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.52628,0.02863,-0.0015],"force_p95":0.46058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48047,"mean_force":0.15529,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51535,0.02902,0.04109]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9902.0,"contact_point_centroid":[0.51304,0.04794,0.10706],"force_p95":0.07996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30024,"mean_force":0.05406,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51276,0.02885,0.10495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9221.0,"contact_point_centroid":[0.51315,0.0097,0.10898],"force_p95":0.08296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2949,"mean_force":0.05662,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51278,0.02885,0.10634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1055.0,"contact_point_centroid":[0.59727,0.15606,0.11873],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24823,"mean_force":0.05121,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59382,0.17511,0.11697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1122.0,"contact_point_centroid":[0.59681,0.19423,0.11779],"force_p95":0.07852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23351,"mean_force":0.04934,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59381,0.1751,0.11695]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03057,-0.00214],"force_p95":0.16355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22732,"mean_force":0.13344,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51769,0.02918,0.04115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6015.0,"contact_point_centroid":[0.5967,0.19052,0.19693],"force_p95":0.07762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17533,"mean_force":0.05512,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59383,0.17143,0.19581]},{"body_a":"world","body_b":"grasp_target","contact_count":3392.0,"contact_point_centroid":[0.57902,0.17416,-0.00199],"force_p95":0.12598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17396,"mean_force":0.12267,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59306,0.17521,0.26441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5761.0,"contact_point_centroid":[0.59705,0.15237,0.19854],"force_p95":0.08138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16487,"mean_force":0.05609,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59381,0.17139,0.1966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.51736,0.0099,0.04256],"force_p95":0.08132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15444,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02911,0.0398]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.5305,0.03079,-0.00174],"force_p95":0.13798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12365,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50878,0.00998,0.27681]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52088,0.02543,0.15017]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12187.0,"contact_point_centroid":[0.55629,0.12342,0.22515],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10076,"mean_force":0.05202,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55515,0.10428,0.22277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12885.0,"contact_point_centroid":[0.5539,0.08099,0.22227],"force_p95":0.07194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09885,"mean_force":0.04955,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55262,0.10003,0.21999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5018.0,"contact_point_centroid":[0.51731,0.04827,0.0416],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07863,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51651,0.02911,0.03981]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57902,0.17416,0.02602],"final_tcp_position":[0.60044,0.17793,0.38943],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.51908,0.02138,0.25149],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22595,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52499,0.02964,0.04969],"tcp_start":[0.51908,0.02138,0.25149],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.0294,0.02551],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18473,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51647,0.0291,0.03977],"tcp_start":[0.52499,0.02964,0.04969],"tcp_to_object_dist_end":0.01997,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.52267,0.02906,0.15914],"object_pos_start":[0.53045,0.0294,0.02551],"object_to_goal_dist_end":0.17658,"object_to_goal_dist_start":0.18473,"object_z_max":0.15887,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51292,0.02887,0.1774],"tcp_start":[0.51647,0.0291,0.03977],"tcp_to_object_dist_end":0.02071,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.59922,0.16786,0.24253],"object_pos_start":[0.52267,0.02906,0.15914],"object_to_goal_dist_end":0.13489,"object_to_goal_dist_start":0.17658,"object_z_max":0.24242,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59327,0.16802,0.26482],"tcp_start":[0.51292,0.02887,0.1774],"tcp_to_object_dist_end":0.02307,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.60312,0.17559,0.09729],"object_pos_start":[0.59922,0.16786,0.24253],"object_to_goal_dist_end":0.01131,"object_to_goal_dist_start":0.13489,"object_z_max":0.24255,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59629,0.1758,0.12152],"tcp_start":[0.59327,0.16802,0.26482],"tcp_to_object_dist_end":0.02517,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57965,0.17414,0.02641],"object_pos_start":[0.60312,0.17559,0.09729],"object_to_goal_dist_end":0.08468,"object_to_goal_dist_start":0.01131,"object_z_max":0.09729,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58924,0.17359,0.14135],"tcp_start":[0.59629,0.1758,0.12152],"tcp_to_object_dist_end":0.11535,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.57902,0.17416,0.02602],"object_pos_start":[0.57965,0.17414,0.02641],"object_to_goal_dist_end":0.08522,"object_to_goal_dist_start":0.08468,"object_z_max":0.02641,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.60044,0.17793,0.38943],"tcp_start":[0.58924,0.17359,0.14135],"tcp_to_object_dist_end":0.36406,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14963,"average_solve_count":401.0,"average_success_count":401.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.16172,"approach_goal.approach_goal_speed":0.04567,"approach_object.approach_height":0.1467,"approach_object.approach_speed":0.10603,"descend_to_goal.descend_goal_speed":0.03255,"descend_to_grasp.descend_speed":0.05945,"descend_to_grasp.grasp_offset_z":0.01557,"grasp_1.grip_force":6.12393,"lift_1.lift_height":0.18216,"lift_1.lift_speed":0.06045,"retract_goal.retract_goal_height":0.27086,"retract_goal.retract_speed":0.09697},"optimized_scores":{"best_composite_score":-0.20468,"best_fitness_score":0.57532,"best_task_score":0.22596},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.57082,0.18496,-0.01127],"force_p95":1.63894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02305,"mean_force":0.63609,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57974,0.18353,0.27725]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.50133,-0.01499,-0.00141],"force_p95":0.34936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4042,"mean_force":0.11161,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48998,-0.0151,0.04794]},{"body_a":"world","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.56655,0.18543,-0.00213],"force_p95":0.16509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34061,"mean_force":0.1246,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58259,0.185,0.39256]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10117.0,"contact_point_centroid":[0.48796,0.00409,0.12782],"force_p95":0.08326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28202,"mean_force":0.0587,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48757,-0.01506,0.1264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11260.0,"contact_point_centroid":[0.4879,-0.03413,0.12739],"force_p95":0.08011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27356,"mean_force":0.05379,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48757,-0.01506,0.12617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2331.0,"contact_point_centroid":[0.58676,0.19952,0.32686],"force_p95":0.13586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25831,"mean_force":0.11202,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5825,0.18127,0.33082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":598.0,"contact_point_centroid":[0.58716,0.16628,0.25426],"force_p95":0.11844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24328,"mean_force":0.08384,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58222,0.18459,0.25777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.58733,0.20304,0.25426],"force_p95":0.11955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23119,"mean_force":0.08241,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.5822,0.18458,0.25772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2676.0,"contact_point_centroid":[0.58606,0.16316,0.32879],"force_p95":0.12565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23105,"mean_force":0.0984,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58248,0.18119,0.33236]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01561,-0.00205],"force_p95":0.13749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17143,"mean_force":0.12657,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49221,-0.01513,0.04801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14964.0,"contact_point_centroid":[0.53041,0.09215,0.29056],"force_p95":0.10894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1439,"mean_force":0.06481,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5291,0.07316,0.29093]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49974,-0.00591,0.24958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17492.0,"contact_point_centroid":[0.53138,0.05697,0.29324],"force_p95":0.09145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13263,"mean_force":0.05504,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53039,0.07574,0.29344]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49857,-0.0138,0.12568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4355.0,"contact_point_centroid":[0.49157,0.00407,0.04844],"force_p95":0.07329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11261,"mean_force":0.04941,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01511,0.04679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.49152,-0.03425,0.04823],"force_p95":0.06929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01511,0.04679]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56576,0.18546,0.02602],"final_tcp_position":[0.58757,0.18723,0.49901],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50036,-0.01247,0.19606],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1701,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49918,-0.01521,0.05574],"tcp_start":[0.50036,-0.01247,0.19606],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01524,0.02581],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49105,-0.01511,0.04676],"tcp_start":[0.49918,-0.01521,0.05574],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.49545,-0.01513,0.18405],"object_pos_start":[0.50374,-0.01524,0.02581],"object_to_goal_dist_end":0.23132,"object_to_goal_dist_start":0.31212,"object_z_max":0.18378,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48789,-0.01505,0.20936],"tcp_start":[0.49105,-0.01511,0.04676],"tcp_to_object_dist_end":0.02642,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.58499,0.17771,0.3614],"object_pos_start":[0.49545,-0.01513,0.18405],"object_to_goal_dist_end":0.11372,"object_to_goal_dist_start":0.23132,"object_z_max":0.36126,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58179,0.17812,0.39317],"tcp_start":[0.48789,-0.01505,0.20936],"tcp_to_object_dist_end":0.03193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.58871,0.18445,0.22731],"object_pos_start":[0.58499,0.17771,0.3614],"object_to_goal_dist_end":0.0211,"object_to_goal_dist_start":0.11372,"object_z_max":0.36143,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.58382,0.18511,0.26232],"tcp_start":[0.58179,0.17812,0.39317],"tcp_to_object_dist_end":0.03535,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58082,0.18249,0.01044],"object_pos_start":[0.58871,0.18445,0.22731],"object_to_goal_dist_end":0.2378,"object_to_goal_dist_start":0.0211,"object_z_max":0.22731,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.57972,0.18352,0.28234],"tcp_start":[0.58382,0.18511,0.26232],"tcp_to_object_dist_end":0.2719,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.56576,0.18546,0.02602],"object_pos_start":[0.58082,0.18249,0.01044],"object_to_goal_dist_end":0.22311,"object_to_goal_dist_start":0.2378,"object_z_max":0.02996,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.58757,0.18723,0.49901],"tcp_start":[0.57972,0.18352,0.28234],"tcp_to_object_dist_end":0.47349,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11132,"average_solve_count":530.0,"average_success_count":530.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.20736,"approach_goal.approach_goal_speed":0.0504,"approach_object.approach_height":0.16702,"approach_object.approach_speed":0.05104,"descend_to_goal.descend_goal_speed":0.01302,"descend_to_grasp.descend_speed":0.03132,"descend_to_grasp.grasp_offset_z":0.01039,"grasp_1.grip_force":12.52559,"lift_1.lift_height":0.16915,"lift_1.lift_speed":0.046,"retract_goal.retract_goal_height":0.36543,"retract_goal.retract_speed":0.07088},"optimized_scores":{"best_composite_score":-0.09119,"best_fitness_score":0.68881,"best_task_score":0.44102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.61933,0.15589,-0.00789],"force_p95":1.25389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43977,"mean_force":0.47333,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.6166,0.1685,0.16734]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.50874,0.03702,-0.00155],"force_p95":0.4455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46011,"mean_force":0.16546,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49816,0.03765,0.04213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.62482,0.18876,0.15369],"force_p95":0.10325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37805,"mean_force":0.0686,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62056,0.1698,0.154]},{"body_a":"world","body_b":"grasp_target","contact_count":3838.0,"contact_point_centroid":[0.60524,0.153,-0.00207],"force_p95":0.17161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30341,"mean_force":0.12741,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.61895,0.16934,0.30235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10818.0,"contact_point_centroid":[0.49561,0.05656,0.11458],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2912,"mean_force":0.05245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49565,0.03745,0.11265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10081.0,"contact_point_centroid":[0.49574,0.01827,0.11482],"force_p95":0.08028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28273,"mean_force":0.05483,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49566,0.03745,0.11226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1014.0,"contact_point_centroid":[0.62448,0.15102,0.15429],"force_p95":0.11172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27209,"mean_force":0.06126,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.62054,0.1698,0.15397]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03947,-0.00217],"force_p95":0.16976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23626,"mean_force":0.13497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,0.03784,0.04218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5443.0,"contact_point_centroid":[0.62367,0.14857,0.25227],"force_p95":0.10289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19893,"mean_force":0.06984,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62064,0.1675,0.25187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6190.0,"contact_point_centroid":[0.62347,0.18621,0.25425],"force_p95":0.08883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19463,"mean_force":0.06069,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62058,0.16742,0.25404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3850.0,"contact_point_centroid":[0.50029,0.01855,0.04386],"force_p95":0.08592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15756,"mean_force":0.05467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49927,0.03775,0.04092]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50277,0.01446,0.25848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16838.0,"contact_point_centroid":[0.55881,0.08318,0.26455],"force_p95":0.07258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13818,"mean_force":0.05014,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55721,0.10227,0.26214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17137.0,"contact_point_centroid":[0.56254,0.12543,0.26906],"force_p95":0.07545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12819,"mean_force":0.04896,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56116,0.10628,0.26681]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.506,0.03449,0.13215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.49995,0.0569,0.04275],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08032,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49928,0.03775,0.04092]}],"total_contact_groups":16},"final_pose_error":0.09096,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60446,0.15293,0.02602],"final_tcp_position":[0.62463,0.17118,0.41955],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50698,0.03085,0.21389],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18816,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50752,0.0384,0.05017],"tcp_start":[0.50698,0.03085,0.21389],"tcp_to_object_dist_end":0.0247,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03815,0.02544],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21355,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49924,0.03775,0.04088],"tcp_start":[0.50752,0.0384,0.05017],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.50487,0.03767,0.17137],"object_pos_start":[0.51248,0.03815,0.02544],"object_to_goal_dist_end":0.18421,"object_to_goal_dist_start":0.21355,"object_z_max":0.1711,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49588,0.03747,0.19056],"tcp_start":[0.49924,0.03775,0.04088],"tcp_to_object_dist_end":0.02119,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.62513,0.16506,0.31186],"object_pos_start":[0.50487,0.03767,0.17137],"object_to_goal_dist_end":0.16702,"object_to_goal_dist_start":0.18421,"object_z_max":0.31172,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61963,0.16528,0.33572],"tcp_start":[0.49588,0.03747,0.19056],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.6297,0.17063,0.13252],"object_pos_start":[0.62513,0.16506,0.31186],"object_to_goal_dist_end":0.01282,"object_to_goal_dist_start":0.16702,"object_z_max":0.31187,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62294,0.17048,0.15914],"tcp_start":[0.61963,0.16528,0.33572],"tcp_to_object_dist_end":0.02746,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61969,0.16275,0.0265],"object_pos_start":[0.6297,0.17063,0.13252],"object_to_goal_dist_end":0.11919,"object_to_goal_dist_start":0.01282,"object_z_max":0.13252,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61653,0.16848,0.17779],"tcp_start":[0.62294,0.17048,0.15914],"tcp_to_object_dist_end":0.15144,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60446,0.15293,0.02602],"object_pos_start":[0.61969,0.16275,0.0265],"object_to_goal_dist_end":0.1228,"object_to_goal_dist_start":0.11919,"object_z_max":0.02879,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.62463,0.17118,0.41955],"tcp_start":[0.61653,0.16848,0.17779],"tcp_to_object_dist_end":0.39447,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```