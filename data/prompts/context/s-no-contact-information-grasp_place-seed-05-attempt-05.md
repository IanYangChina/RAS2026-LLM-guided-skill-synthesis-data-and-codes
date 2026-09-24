## Search State

- **Seed**: 5
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2159 | 0.40 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1612 | 0.41 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0840 | 0.36 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1692 | 0.39 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

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

## Current Skill (Q=-0.216) — your mutation base

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

- **Composite score**: -0.216
- **task_score** (E): 0.403
- **fitness_score**: 0.664  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0735 |
| descend_to_grasp | 1.00 | 0.1769 |
| grasp_1 | 1.00 | 0.0129 |
| lift_1 | 1.00 | 0.1613 |
| approach_goal | 1.00 | 0.2122 |
| descend_to_goal | 1.00 | 0.0724 |
| release_goal | 1.00 | 0.0199 |
| retract_goal | 0.67 | 0.1896 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.014, 0.232) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.509, 0.014, 0.232)→(0.511, 0.017, 0.056) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.017, 0.056)→(0.502, 0.017, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.046)→(0.499, 0.017, 0.207) | (0.516, 0.018, 0.026)→(0.509, 0.017, 0.182) | 0.237→0.200 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.207)→(0.595, 0.165, 0.302) | (0.509, 0.017, 0.182)→(0.598, 0.165, 0.272) | 0.200→0.106 |
| descend_to_goal | descend | 1.00 / step_budget | (0.595, 0.165, 0.302)→(0.600, 0.175, 0.230) | (0.598, 0.165, 0.272)→(0.605, 0.175, 0.198) | 0.106→0.032 |
| release_goal | release | 1.00 / step_budget | (0.600, 0.175, 0.230)→(0.595, 0.173, 0.250) | (0.605, 0.175, 0.198)→(0.600, 0.176, 0.013) | 0.032→0.154 |
| retract_goal | retract | 0.67 / step_budget | (0.595, 0.173, 0.250)→(0.605, 0.179, 0.439) | (0.600, 0.176, 0.013)→(0.591, 0.178, 0.023) | 0.154→0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.540
- phase_score: 0.480
- phase_breakdown.reach_object_score: 0.859
- phase_breakdown.reach_goal_score: 0.742
- phase_breakdown.place_done_score: 0.000
- grasp_place_fitness: 0.733

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: -0.196
- **K-run variance**: 0.0044
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10335,"average_solve_count":358.0,"average_success_count":358.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.13216,"approach_goal.approach_goal_speed":0.05555,"approach_object.approach_height":0.21951,"approach_object.approach_speed":0.09438,"descend_to_goal.descend_goal_speed":0.02246,"descend_to_goal.place_z_offset":0.05476,"descend_to_grasp.descend_speed":0.04891,"descend_to_grasp.grasp_offset_z":0.01021,"grasp_1.grasp_time":1.23161,"lift_1.lift_height":0.11908,"lift_1.lift_speed":0.07522,"release_goal.release_time":0.16523,"retract_goal.retract_goal_height":0.34429,"retract_goal.retract_speed":0.06502},"optimized_scores":{"best_composite_score":-0.14692,"best_fitness_score":0.73308,"best_task_score":0.5401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":470.0,"contact_point_centroid":[0.60691,0.18406,-0.00397],"force_p95":0.77857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72885,"mean_force":0.21331,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58967,0.17179,0.18417]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.52781,0.02838,-0.00151],"force_p95":0.39812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45732,"mean_force":0.10548,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51506,0.02875,0.04621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5959.0,"contact_point_centroid":[0.5149,0.04753,0.08974],"force_p95":0.1067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31061,"mean_force":0.06398,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51254,0.02859,0.08735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.60094,0.18943,0.17428],"force_p95":0.27423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30051,"mean_force":0.11932,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59427,0.1734,0.17789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5163.0,"contact_point_centroid":[0.51492,0.00956,0.08889],"force_p95":0.11414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2886,"mean_force":0.07059,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51253,0.02859,0.08703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1055.0,"contact_point_centroid":[0.59953,0.18854,0.20662],"force_p95":0.1365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26392,"mean_force":0.08541,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59342,0.17016,0.20824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":821.0,"contact_point_centroid":[0.5994,0.15155,0.20908],"force_p95":0.21751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25104,"mean_force":0.1042,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59332,0.16996,0.20993]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.60137,0.15584,0.17257],"force_p95":0.2053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23329,"mean_force":0.13784,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59488,0.17354,0.17917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03065,-0.00216],"force_p95":0.16727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22789,"mean_force":0.1345,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5175,0.02892,0.04614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8295.0,"contact_point_centroid":[0.5562,0.11618,0.18355],"force_p95":0.09769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1515,"mean_force":0.07384,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5506,0.09754,0.18255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7846.0,"contact_point_centroid":[0.55747,0.08102,0.18438],"force_p95":0.10006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14936,"mean_force":0.07715,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55187,0.09973,0.18385]},{"body_a":"world","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.5305,0.03079,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12382,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50841,0.00947,0.28165]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.60708,0.18407,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12458,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59356,0.17435,0.3154]},{"body_a":"world","body_b":"grasp_target","contact_count":1628.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52065,0.02481,0.15877]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4547.0,"contact_point_centroid":[0.5173,0.0096,0.04722],"force_p95":0.07476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11863,"mean_force":0.04749,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02884,0.04481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5540.0,"contact_point_centroid":[0.51672,0.04809,0.04743],"force_p95":0.07079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07376,"mean_force":0.04047,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02884,0.04482]}],"total_contact_groups":16},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60708,0.18407,0.01602],"final_tcp_position":[0.60075,0.17793,0.43253],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.51837,0.02047,0.26118],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2357,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52495,0.02937,0.05504],"tcp_start":[0.51837,0.02047,0.26118],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.02946,0.02542],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18471,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.5163,0.02884,0.04477],"tcp_start":[0.52495,0.02937,0.05504],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":337.0,"n_steps_budget":990.0,"object_pos_end":[0.52828,0.02903,0.12097],"object_pos_start":[0.53048,0.02946,0.02542],"object_to_goal_dist_end":0.16702,"object_to_goal_dist_start":0.18471,"object_z_max":0.12071,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51229,0.02857,0.14426],"tcp_start":[0.5163,0.02884,0.04477],"tcp_to_object_dist_end":0.02825,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.59983,0.16809,0.19616],"object_pos_start":[0.52828,0.02903,0.12097],"object_to_goal_dist_end":0.08871,"object_to_goal_dist_start":0.16702,"object_z_max":0.19605,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59276,0.16792,0.22593],"tcp_start":[0.51229,0.02857,0.14426],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.60275,0.17339,0.14925],"object_pos_start":[0.59983,0.16809,0.19616],"object_to_goal_dist_end":0.04151,"object_to_goal_dist_start":0.08871,"object_z_max":0.19618,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59539,0.17355,0.18076],"tcp_start":[0.59276,0.16792,0.22593],"tcp_to_object_dist_end":0.03236,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60706,0.18399,0.01606],"object_pos_start":[0.60275,0.17339,0.14925],"object_to_goal_dist_end":0.09236,"object_to_goal_dist_start":0.04151,"object_z_max":0.14925,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58942,0.1717,0.2002],"tcp_start":[0.59539,0.17355,0.18076],"tcp_to_object_dist_end":0.18539,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.60708,0.18407,0.01602],"object_pos_start":[0.60706,0.18399,0.01606],"object_to_goal_dist_end":0.0924,"object_to_goal_dist_start":0.09236,"object_z_max":0.01606,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.60075,0.17793,0.43253],"tcp_start":[0.58942,0.1717,0.2002],"tcp_to_object_dist_end":0.4166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.01456,"average_mean_iterations":5.94175,"average_solve_count":412.0,"average_success_count":406.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.20063,"approach_goal.approach_goal_speed":0.04889,"approach_object.approach_height":0.18413,"approach_object.approach_speed":0.09401,"descend_to_goal.descend_goal_speed":0.02952,"descend_to_goal.place_z_offset":0.04591,"descend_to_grasp.descend_speed":0.05594,"descend_to_grasp.grasp_offset_z":0.01074,"grasp_1.grasp_time":0.77053,"lift_1.lift_height":0.1909,"lift_1.lift_speed":0.05024,"release_goal.release_time":0.19185,"retract_goal.retract_goal_height":0.363,"retract_goal.retract_speed":0.14305},"optimized_scores":{"best_composite_score":-0.30488,"best_fitness_score":0.57512,"best_task_score":0.22604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.57939,0.18257,-0.01319],"force_p95":1.86359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96578,"mean_force":1.19801,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58041,0.18138,0.32831]},{"body_a":"world","body_b":"grasp_target","contact_count":2751.0,"contact_point_centroid":[0.5675,0.18286,-0.0023],"force_p95":0.17336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78921,"mean_force":0.12618,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58343,0.18375,0.44201]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50008,-0.01472,-0.00143],"force_p95":0.39283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40339,"mean_force":0.13893,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49003,-0.01495,0.0481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":594.0,"contact_point_centroid":[0.5868,0.16394,0.30443],"force_p95":0.12465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28117,"mean_force":0.08509,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58215,0.18228,0.30789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11100.0,"contact_point_centroid":[0.48751,0.00428,0.13061],"force_p95":0.08009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27968,"mean_force":0.05686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48758,-0.01491,0.12968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.58679,0.20064,0.30408],"force_p95":0.12356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27286,"mean_force":0.08421,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58215,0.18228,0.30789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12628.0,"contact_point_centroid":[0.48719,-0.034,0.13166],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27028,"mean_force":0.05112,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48758,-0.01491,0.13081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.58292,0.19252,0.36818],"force_p95":0.12983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24305,"mean_force":0.10009,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57975,0.17418,0.37206]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1973.0,"contact_point_centroid":[0.58253,0.156,0.36866],"force_p95":0.12791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21608,"mean_force":0.09461,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57974,0.17414,0.37233]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.0156,-0.00206],"force_p95":0.14067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18273,"mean_force":0.12746,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4922,-0.01498,0.04814]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.50382,-0.01567,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12355,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5,-0.00521,0.26823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16148.0,"contact_point_centroid":[0.52892,0.09044,0.31063],"force_p95":0.09878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12298,"mean_force":0.06083,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52844,0.07145,0.31086]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49907,-0.01311,0.14518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17995.0,"contact_point_centroid":[0.52941,0.05364,0.31199],"force_p95":0.09114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12125,"mean_force":0.05492,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52898,0.07251,0.31204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4350.0,"contact_point_centroid":[0.49156,0.00422,0.0485],"force_p95":0.07366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11675,"mean_force":0.04945,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49107,-0.01496,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.49151,-0.03411,0.04833],"force_p95":0.06974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07799,"mean_force":0.04453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01496,0.04693]}],"total_contact_groups":16},"final_pose_error":0.06253,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56672,0.18294,0.02602],"final_tcp_position":[0.58869,0.18697,0.54861],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50054,-0.01125,0.23303],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20708,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49938,-0.01505,0.05623],"tcp_start":[0.50054,-0.01125,0.23303],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01514,0.02576],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49105,-0.01496,0.0469],"tcp_start":[0.49938,-0.01505,0.05623],"tcp_to_object_dist_end":0.02466,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.49501,-0.01493,0.19286],"object_pos_start":[0.50374,-0.01514,0.02576],"object_to_goal_dist_end":0.22903,"object_to_goal_dist_start":0.31209,"object_z_max":0.19259,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48795,-0.0149,0.21827],"tcp_start":[0.49105,-0.01496,0.0469],"tcp_to_object_dist_end":0.02637,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57851,0.16752,0.38782],"object_pos_start":[0.49501,-0.01493,0.19286],"object_to_goal_dist_end":0.14136,"object_to_goal_dist_start":0.22903,"object_z_max":0.38763,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57709,0.16792,0.41921],"tcp_start":[0.48795,-0.0149,0.21827],"tcp_to_object_dist_end":0.03143,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.58806,0.18215,0.27883],"object_pos_start":[0.57851,0.16752,0.38782],"object_to_goal_dist_end":0.03119,"object_to_goal_dist_start":0.14136,"object_z_max":0.38787,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.5834,0.1826,0.31274],"tcp_start":[0.57709,0.16792,0.41921],"tcp_to_object_dist_end":0.03423,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58199,0.17988,-0.00109],"object_pos_start":[0.58806,0.18215,0.27883],"object_to_goal_dist_end":0.24937,"object_to_goal_dist_start":0.03119,"object_z_max":0.27883,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.5804,0.18138,0.33252],"tcp_start":[0.5834,0.1826,0.31274],"tcp_to_object_dist_end":0.33362,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.56672,0.18294,0.02602],"object_pos_start":[0.58199,0.17988,-0.00109],"object_to_goal_dist_end":0.22306,"object_to_goal_dist_start":0.24937,"object_z_max":0.02951,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.58869,0.18697,0.54861],"tcp_start":[0.5804,0.18138,0.33252],"tcp_to_object_dist_end":0.52307,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32039,"average_solve_count":309.0,"average_success_count":309.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.12461,"approach_goal.approach_goal_speed":0.0998,"approach_object.approach_height":0.15529,"approach_object.approach_speed":0.08896,"descend_to_goal.descend_goal_speed":0.04446,"descend_to_goal.place_z_offset":0.03517,"descend_to_grasp.descend_speed":0.06199,"descend_to_grasp.grasp_offset_z":0.01014,"grasp_1.grasp_time":1.18884,"lift_1.lift_height":0.23239,"lift_1.lift_speed":0.03964,"release_goal.release_time":0.18883,"retract_goal.retract_goal_height":0.20986,"retract_goal.retract_speed":0.10458},"optimized_scores":{"best_composite_score":-0.19602,"best_fitness_score":0.68398,"best_task_score":0.4428},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.60358,0.16599,-0.00691],"force_p95":1.25155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66618,"mean_force":0.3617,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61498,0.16606,0.20707]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.50881,0.0372,-0.00161],"force_p95":0.38534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41936,"mean_force":0.14794,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49814,0.03742,0.04692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":705.0,"contact_point_centroid":[0.61948,0.18599,0.189],"force_p95":0.12419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34057,"mean_force":0.07662,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61842,0.16726,0.1922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":717.0,"contact_point_centroid":[0.61864,0.14872,0.19],"force_p95":0.11544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29599,"mean_force":0.07315,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61845,0.16727,0.19224]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15253.0,"contact_point_centroid":[0.49611,0.05633,0.14821],"force_p95":0.08056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27413,"mean_force":0.05255,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49585,0.03723,0.14652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1769.0,"contact_point_centroid":[0.61657,0.18243,0.23112],"force_p95":0.11657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26617,"mean_force":0.07039,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61677,0.1637,0.23231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14144.0,"contact_point_centroid":[0.49556,0.01808,0.15235],"force_p95":0.08107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24974,"mean_force":0.05525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49587,0.03724,0.15125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1511.0,"contact_point_centroid":[0.61685,0.14506,0.22935],"force_p95":0.11371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24725,"mean_force":0.07927,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61679,0.16372,0.23212]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03958,-0.00218],"force_p95":0.17308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23171,"mean_force":0.13591,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50044,0.03761,0.04702]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.60082,0.16718,-0.00202],"force_p95":0.16339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2076,"mean_force":0.12391,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.61907,0.16849,0.27672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9004.0,"contact_point_centroid":[0.55476,0.07968,0.25801],"force_p95":0.08334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17041,"mean_force":0.05393,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55452,0.09879,0.25762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9058.0,"contact_point_centroid":[0.55575,0.11819,0.25843],"force_p95":0.07823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15901,"mean_force":0.05323,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55486,0.09913,0.25764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4321.0,"contact_point_centroid":[0.49962,0.01829,0.04744],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14496,"mean_force":0.04966,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03752,0.04577]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.51251,0.03972,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50309,0.01495,0.25273]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50657,0.03475,0.12977]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5439.0,"contact_point_centroid":[0.50039,0.05673,0.04827],"force_p95":0.07377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07628,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49931,0.03752,0.04578]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60034,0.16724,0.02602],"final_tcp_position":[0.6251,0.17137,0.33525],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5074,0.03156,0.20271],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17695,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50771,0.03817,0.05539],"tcp_start":[0.5074,0.03156,0.20271],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03818,0.02535],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21357,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49927,0.03752,0.04574],"tcp_start":[0.50771,0.03817,0.05539],"tcp_to_object_dist_end":0.02432,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.50267,0.03777,0.23289],"object_pos_start":[0.5125,0.03818,0.02535],"object_to_goal_dist_end":0.20366,"object_to_goal_dist_start":0.21357,"object_z_max":0.23262,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49653,0.03729,0.25851],"tcp_start":[0.49927,0.03752,0.04574],"tcp_to_object_dist_end":0.02635,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.61479,0.16023,0.23068],"object_pos_start":[0.50267,0.03777,0.23289],"object_to_goal_dist_end":0.08748,"object_to_goal_dist_start":0.20366,"object_z_max":0.23314,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61432,0.16034,0.26097],"tcp_start":[0.49653,0.03729,0.25851],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":122.0,"n_steps_budget":1000.0,"object_pos_end":[0.62302,0.1682,0.16629],"object_pos_start":[0.61479,0.16023,0.23068],"object_to_goal_dist_end":0.02217,"object_to_goal_dist_start":0.08748,"object_z_max":0.23068,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62063,0.16779,0.19778],"tcp_start":[0.61432,0.16034,0.26097],"tcp_to_object_dist_end":0.03158,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60977,0.16486,0.02505],"object_pos_start":[0.62302,0.1682,0.16629],"object_to_goal_dist_end":0.12153,"object_to_goal_dist_start":0.02217,"object_z_max":0.16629,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61494,0.16605,0.2161],"tcp_start":[0.62063,0.16779,0.19778],"tcp_to_object_dist_end":0.19112,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":478.0,"n_steps_budget":840.0,"object_pos_end":[0.60034,0.16724,0.02602],"object_pos_start":[0.60977,0.16486,0.02505],"object_to_goal_dist_end":0.1222,"object_to_goal_dist_start":0.12153,"object_z_max":0.0273,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.6251,0.17137,0.33525],"tcp_start":[0.61494,0.16605,0.2161],"tcp_to_object_dist_end":0.31025,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```