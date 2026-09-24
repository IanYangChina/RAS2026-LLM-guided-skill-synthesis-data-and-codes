## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.0900 | 0.40 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2159 | 0.40 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1612 | 0.41 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0840 | 0.36 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1692 | 0.39 | ✅ accepted |

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

## Current Skill (Q=-0.090) — your mutation base

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

- **Composite score**: -0.090
- **task_score** (E): 0.396
- **fitness_score**: 0.665  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0768 |
| descend_to_grasp | 1.00 | 0.1765 |
| grasp_1 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 0.1517 |
| approach_goal | 1.00 | 0.2176 |
| descend_to_goal | 1.00 | 0.0026 |
| release_goal | 1.00 | 0.0203 |
| retract_goal | 1.00 | 0.1068 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.228) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.228)→(0.511, 0.018, 0.052) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.052)→(0.502, 0.017, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.042)→(0.499, 0.017, 0.194) | (0.516, 0.018, 0.026)→(0.510, 0.017, 0.172) | 0.237→0.206 |
| approach_goal | approach | 1.00 / step_budget | (0.499, 0.017, 0.194)→(0.597, 0.169, 0.303) | (0.510, 0.017, 0.172)→(0.604, 0.169, 0.277) | 0.206→0.110 |
| descend_to_goal | descend | 1.00 / force_exceeded | (0.597, 0.169, 0.303)→(0.597, 0.170, 0.301) | (0.604, 0.169, 0.277)→(0.604, 0.170, 0.274) | 0.110→0.108 |
| release_goal | release | 1.00 / step_budget | (0.597, 0.170, 0.301)→(0.594, 0.169, 0.321) | (0.604, 0.170, 0.274)→(0.600, 0.168, 0.001) | 0.108→0.167 |
| retract_goal | retract | 1.00 / step_budget | (0.594, 0.169, 0.321)→(0.604, 0.178, 0.427) | (0.600, 0.168, 0.001)→(0.601, 0.167, 0.019) | 0.167→0.150 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.554
- phase_score: 0.349
- phase_breakdown.reach_object_score: 0.854
- phase_breakdown.reach_goal_score: 0.219
- phase_breakdown.place_done_score: 0.066
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.554
- **Median Q (composite search score)**: -0.076
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_to_grasp.grasp_offset_z
- **Parameters at upper bound**: descend_to_goal.contact_force_threshold
- **Final σ (mean)**: 0.321


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40191,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.14653,"approach_goal.approach_goal_speed":0.09153,"approach_object.approach_height":0.15531,"approach_object.approach_speed":0.12091,"descend_to_goal.contact_force_threshold":5.46598,"descend_to_goal.descend_goal_speed":0.03204,"descend_to_goal.place_contact_offset":0.00617,"descend_to_grasp.descend_speed":0.06124,"descend_to_grasp.grasp_offset_z":0.01458,"grasp_1.grip_force":20.69185,"lift_1.lift_height":0.1852,"lift_1.lift_speed":0.05626,"retract_goal.retract_goal_height":0.24999,"retract_goal.retract_speed":0.16194},"optimized_scores":{"best_composite_score":-0.01414,"best_fitness_score":0.74086,"best_task_score":0.55444},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.57601,0.1639,-0.01043],"force_p95":1.58627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67196,"mean_force":0.54039,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58707,0.16485,0.25678]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.52812,0.02876,-0.00148],"force_p95":0.36215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44273,"mean_force":0.10142,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51536,0.02911,0.04592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12262.0,"contact_point_centroid":[0.5137,0.04804,0.12673],"force_p95":0.0794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29633,"mean_force":0.0527,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51291,0.02895,0.1248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10866.0,"contact_point_centroid":[0.51374,0.00979,0.12727],"force_p95":0.08171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26899,"mean_force":0.05749,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51292,0.02895,0.12528]},{"body_a":"world","body_b":"grasp_target","contact_count":1105.0,"contact_point_centroid":[0.57351,0.16384,-0.0022],"force_p95":0.18816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23563,"mean_force":0.12406,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59244,0.17097,0.30267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.59347,0.18488,0.24257],"force_p95":0.14798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22221,"mean_force":0.07444,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59163,0.16599,0.24285]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03066,-0.00213],"force_p95":0.1589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2196,"mean_force":0.13244,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51775,0.02928,0.04593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.59405,0.14711,0.24229],"force_p95":0.13597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20669,"mean_force":0.07227,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59163,0.16599,0.24285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":886.0,"contact_point_centroid":[0.59244,0.14695,0.2379],"force_p95":0.08955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19051,"mean_force":0.05781,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58999,0.16593,0.23849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1077.0,"contact_point_centroid":[0.59213,0.1849,0.23796],"force_p95":0.08262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17875,"mean_force":0.04952,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59001,0.16594,0.23855]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.5305,0.03079,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51001,0.01172,0.2521]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52216,0.02707,0.12798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4717.0,"contact_point_centroid":[0.51749,0.00998,0.04716],"force_p95":0.07225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11053,"mean_force":0.04584,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51657,0.0292,0.04458]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8299.0,"contact_point_centroid":[0.55171,0.07638,0.22473],"force_p95":0.08885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10291,"mean_force":0.05826,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55031,0.09543,0.22414]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9103.0,"contact_point_centroid":[0.55319,0.11658,0.2253],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09876,"mean_force":0.05277,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55161,0.09766,0.2247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5318.0,"contact_point_centroid":[0.51695,0.04846,0.04694],"force_p95":0.0708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07527,"mean_force":0.04205,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51658,0.0292,0.04458]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.572,0.16378,0.02602],"final_tcp_position":[0.59826,0.17631,0.33855],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52178,0.02459,0.20195],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17626,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52499,0.02974,0.05447],"tcp_start":[0.52178,0.02459,0.20195],"tcp_to_object_dist_end":0.029,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.0297,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18448,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51655,0.0292,0.04454],"tcp_start":[0.52499,0.02974,0.05447],"tcp_to_object_dist_end":0.02357,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.52164,0.02921,0.18609],"object_pos_start":[0.53046,0.0297,0.02552],"object_to_goal_dist_end":0.18649,"object_to_goal_dist_start":0.18448,"object_z_max":0.18583,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.5133,0.02898,0.21026],"tcp_start":[0.51655,0.0292,0.04454],"tcp_to_object_dist_end":0.02557,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.5965,0.16574,0.21579],"object_pos_start":[0.52164,0.02921,0.18609],"object_to_goal_dist_end":0.10858,"object_to_goal_dist_start":0.18649,"object_z_max":0.21573,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.59171,0.16564,0.24307],"tcp_start":[0.5133,0.02898,0.21026],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.5967,0.16669,0.21494],"object_pos_start":[0.5965,0.16574,0.21579],"object_to_goal_dist_end":0.10762,"object_to_goal_dist_start":0.10858,"object_z_max":0.21579,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.5915,0.16628,0.24229],"tcp_start":[0.59171,0.16564,0.24307],"tcp_to_object_dist_end":0.02784,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58479,0.16423,0.01595],"object_pos_start":[0.5967,0.16669,0.21494],"object_to_goal_dist_end":0.09474,"object_to_goal_dist_start":0.10762,"object_z_max":0.21494,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58704,0.16485,0.2627],"tcp_start":[0.5915,0.16628,0.24229],"tcp_to_object_dist_end":0.24677,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.572,0.16378,0.02602],"object_pos_start":[0.58479,0.16423,0.01595],"object_to_goal_dist_end":0.08847,"object_to_goal_dist_start":0.09474,"object_z_max":0.02876,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.59826,0.17631,0.33855],"tcp_start":[0.58704,0.16485,0.2627],"tcp_to_object_dist_end":0.31388,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3007,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.11629,"approach_goal.approach_goal_speed":0.06132,"approach_object.approach_height":0.2298,"approach_object.approach_speed":0.10464,"descend_to_goal.contact_force_threshold":9.99999,"descend_to_goal.descend_goal_speed":0.02453,"descend_to_goal.place_contact_offset":-0.00628,"descend_to_grasp.descend_speed":0.06447,"descend_to_grasp.grasp_offset_z":0.01,"grasp_1.grip_force":15.4113,"lift_1.lift_height":0.13728,"lift_1.lift_speed":0.05934,"retract_goal.retract_goal_height":0.25965,"retract_goal.retract_speed":0.09082},"optimized_scores":{"best_composite_score":-0.17999,"best_fitness_score":0.57501,"best_task_score":0.2117},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":30.0,"contact_point_centroid":[0.58496,0.17154,-0.01243],"force_p95":2.13914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20653,"mean_force":1.75901,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57858,0.17757,0.36278]},{"body_a":"world","body_b":"grasp_target","contact_count":1737.0,"contact_point_centroid":[0.60005,0.17458,-0.00267],"force_p95":0.17648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58557,"mean_force":0.14061,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58234,0.18207,0.42763]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.50106,-0.01458,-0.00142],"force_p95":0.40147,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47833,"mean_force":0.1292,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48999,-0.01487,0.04213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7454.0,"contact_point_centroid":[0.48779,0.00435,0.09978],"force_p95":0.08255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29326,"mean_force":0.05756,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48753,-0.01482,0.09712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8195.0,"contact_point_centroid":[0.48773,-0.03389,0.09899],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28576,"mean_force":0.05356,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48751,-0.01482,0.09688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1018.0,"contact_point_centroid":[0.58386,0.15935,0.34219],"force_p95":0.09295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26151,"mean_force":0.06128,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57985,0.17828,0.34063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1130.0,"contact_point_centroid":[0.58416,0.19723,0.34244],"force_p95":0.08459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24059,"mean_force":0.05517,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57988,0.1783,0.34078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":272.0,"contact_point_centroid":[0.58527,0.19756,0.34798],"force_p95":0.12747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21462,"mean_force":0.07033,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58099,0.17858,0.3467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":238.0,"contact_point_centroid":[0.58501,0.15983,0.34787],"force_p95":0.10398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21284,"mean_force":0.07047,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58099,0.17858,0.3467]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01554,-0.00207],"force_p95":0.14486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19193,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49223,-0.01489,0.04212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4103.0,"contact_point_centroid":[0.49147,0.00441,0.04367],"force_p95":0.07968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13928,"mean_force":0.0522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49109,-0.01488,0.0409]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.50382,-0.01567,-0.00141],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12482,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50008,-0.00312,0.29048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19555.0,"contact_point_centroid":[0.53517,0.06411,0.25441],"force_p95":0.07413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13186,"mean_force":0.05074,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53332,0.08313,0.25247]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12536,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49879,-0.01121,0.16274]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18050.0,"contact_point_centroid":[0.53622,0.1042,0.25652],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12236,"mean_force":0.05472,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53428,0.08507,0.25441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5412.0,"contact_point_centroid":[0.49082,-0.03395,0.04355],"force_p95":0.06585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07337,"mean_force":0.04073,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49109,-0.01488,0.0409]}],"total_contact_groups":16},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.60081,0.17427,0.01602],"final_tcp_position":[0.58687,0.18648,0.48787],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02586],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31235,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50042,-0.0075,0.27724],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25154,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02586],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31235,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49926,-0.01496,0.04983],"tcp_start":[0.50042,-0.0075,0.27724],"tcp_to_object_dist_end":0.02425,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01491,0.02573],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31196,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49106,-0.01488,0.04087],"tcp_start":[0.49926,-0.01496,0.04983],"tcp_to_object_dist_end":0.01975,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.49746,-0.01494,0.14015],"object_pos_start":[0.50374,-0.01491,0.02573],"object_to_goal_dist_end":0.24621,"object_to_goal_dist_start":0.31196,"object_z_max":0.13988,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48748,-0.01481,0.15861],"tcp_start":[0.49106,-0.01488,0.04087],"tcp_to_object_dist_end":0.02099,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.5897,0.17829,0.32325],"object_pos_start":[0.49746,-0.01494,0.14015],"object_to_goal_dist_end":0.07574,"object_to_goal_dist_start":0.24621,"object_z_max":0.3231,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58112,0.17819,0.34767],"tcp_start":[0.48748,-0.01481,0.15861],"tcp_to_object_dist_end":0.02588,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.58984,0.17883,0.32006],"object_pos_start":[0.5897,0.17829,0.32325],"object_to_goal_dist_end":0.07252,"object_to_goal_dist_start":0.07574,"object_z_max":0.32328,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.5808,0.17867,0.34481],"tcp_start":[0.58112,0.17819,0.34767],"tcp_to_object_dist_end":0.02635,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58731,0.17651,-0.00522],"object_pos_start":[0.58984,0.17883,0.32006],"object_to_goal_dist_end":0.25358,"object_to_goal_dist_start":0.07252,"object_z_max":0.32006,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.57857,0.17757,0.36524],"tcp_start":[0.5808,0.17867,0.34481],"tcp_to_object_dist_end":0.37057,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":454.0,"n_steps_budget":990.0,"object_pos_end":[0.60081,0.17427,0.01602],"object_pos_start":[0.58731,0.17651,-0.00522],"object_to_goal_dist_end":0.23289,"object_to_goal_dist_start":0.25358,"object_z_max":0.01743,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.58687,0.18648,0.48787],"tcp_start":[0.57857,0.17757,0.36524],"tcp_to_object_dist_end":0.47222,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23675,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.18991,"approach_goal.approach_goal_speed":0.04664,"approach_object.approach_height":0.15761,"approach_object.approach_speed":0.11438,"descend_to_goal.contact_force_threshold":6.52736,"descend_to_goal.descend_goal_speed":0.03609,"descend_to_goal.place_contact_offset":0.01537,"descend_to_grasp.descend_speed":0.05336,"descend_to_grasp.grasp_offset_z":0.01067,"grasp_1.grip_force":11.97728,"lift_1.lift_height":0.19098,"lift_1.lift_speed":0.06267,"retract_goal.retract_goal_height":0.32827,"retract_goal.retract_speed":0.10009},"optimized_scores":{"best_composite_score":-0.076,"best_fitness_score":0.679,"best_task_score":0.42217},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.6205,0.16334,-0.01356],"force_p95":1.93985,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99605,"mean_force":1.19079,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61522,0.16336,0.33098]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.63012,0.16342,-0.00241],"force_p95":0.12522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52473,"mean_force":0.12138,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.6206,0.16734,0.39261]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50922,0.03743,-0.0015],"force_p95":0.41386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4743,"mean_force":0.13593,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49811,0.03765,0.04271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10026.0,"contact_point_centroid":[0.49741,0.05641,0.11736],"force_p95":0.10426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30832,"mean_force":0.06283,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49559,0.03745,0.11562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9391.0,"contact_point_centroid":[0.49746,0.01846,0.12058],"force_p95":0.10491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29962,"mean_force":0.06571,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49561,0.03746,0.11833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.62452,0.18323,0.31839],"force_p95":0.1568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25036,"mean_force":0.09243,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61825,0.16451,0.31791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.62463,0.14597,0.31861],"force_p95":0.14841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.242,"mean_force":0.08568,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61825,0.16451,0.31791]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03947,-0.00216],"force_p95":0.16853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23124,"mean_force":0.13467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50044,0.03786,0.04256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":761.0,"contact_point_centroid":[0.62323,0.14545,0.31181],"force_p95":0.09664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17311,"mean_force":0.06622,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61695,0.16414,0.31105]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.62315,0.18293,0.31127],"force_p95":0.09789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1728,"mean_force":0.06495,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61693,0.16413,0.311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3892.0,"contact_point_centroid":[0.50021,0.01856,0.04419],"force_p95":0.08432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15593,"mean_force":0.05411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03776,0.04129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9645.0,"contact_point_centroid":[0.56295,0.08334,0.26677],"force_p95":0.09544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14014,"mean_force":0.07255,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55705,0.10201,0.26498]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50305,0.01492,0.25373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9541.0,"contact_point_centroid":[0.56397,0.12187,0.26773],"force_p95":0.09693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13397,"mean_force":0.07311,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55814,0.10312,0.26594]},{"body_a":"world","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50625,0.03482,0.12759]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.49993,0.05691,0.04312],"force_p95":0.07575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07999,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49929,0.03776,0.0413]}],"total_contact_groups":16},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63007,0.16341,0.01602],"final_tcp_position":[0.62709,0.1716,0.45336],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5073,0.03146,0.20482],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17907,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50753,0.03841,0.05055],"tcp_start":[0.5073,0.03146,0.20482],"tcp_to_object_dist_end":0.02507,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03816,0.02545],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21353,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49926,0.03776,0.04126],"tcp_start":[0.50753,0.03841,0.05055],"tcp_to_object_dist_end":0.02061,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.50952,0.03774,0.19072],"object_pos_start":[0.51247,0.03816,0.02545],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.21353,"object_z_max":0.19045,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49596,0.03748,0.21268],"tcp_start":[0.49926,0.03776,0.04126],"tcp_to_object_dist_end":0.02581,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.62581,0.1641,0.29182],"object_pos_start":[0.50952,0.03774,0.19072],"object_to_goal_dist_end":0.14705,"object_to_goal_dist_start":0.18491,"object_z_max":0.29171,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61839,0.16419,0.31934],"tcp_start":[0.49596,0.03748,0.21268],"tcp_to_object_dist_end":0.0285,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.62568,0.16465,0.28747],"object_pos_start":[0.62581,0.1641,0.29182],"object_to_goal_dist_end":0.14267,"object_to_goal_dist_start":0.14705,"object_z_max":0.29182,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.61801,0.16453,0.31539],"tcp_start":[0.61839,0.16419,0.31934],"tcp_to_object_dist_end":0.02896,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62694,0.1629,-0.00702],"object_pos_start":[0.62568,0.16465,0.28747],"object_to_goal_dist_end":0.15235,"object_to_goal_dist_start":0.14267,"object_z_max":0.28747,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61522,0.16336,0.33453],"tcp_start":[0.61801,0.16453,0.31539],"tcp_to_object_dist_end":0.34175,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":458.0,"n_steps_budget":870.0,"object_pos_end":[0.63007,0.16341,0.01602],"object_pos_start":[0.62694,0.1629,-0.00702],"object_to_goal_dist_end":0.12935,"object_to_goal_dist_start":0.15235,"object_z_max":0.01686,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.62709,0.1716,0.45336],"tcp_start":[0.61522,0.16336,0.33453],"tcp_to_object_dist_end":0.43742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```