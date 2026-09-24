## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0840 | 0.36 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.1692 | 0.39 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.084) — your mutation base

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
  control: position_control
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
      - 0.05
      - 0.15
      default: 0.1
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
  control: position_control
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
      - 0.05
      - 0.15
      default: 0.1
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
      - 0.02
      - 0.1
      default: 0.05
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

- **Composite score**: -0.084
- **task_score** (E): 0.356
- **fitness_score**: 0.646  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0951 |
| descend_to_grasp | 1.00 | 0.1606 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1350 |
| approach_goal | 1.00 | 0.0968 |
| descend_to_goal | 1.00 | 0.1329 |
| release_goal | 1.00 | 0.0205 |
| retract_goal | 1.00 | 0.2422 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.013, 0.211) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.508, 0.013, 0.211)→(0.511, 0.018, 0.051) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.051)→(0.502, 0.017, 0.041) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.041)→(0.499, 0.017, 0.176) | (0.516, 0.017, 0.026)→(0.515, 0.017, 0.155) | 0.237→0.198 |
| approach_goal | approach | 1.00 / step_budget | (0.567, 0.106, 0.253)→(0.600, 0.173, 0.314) | (0.515, 0.017, 0.155)→(0.583, 0.141, 0.099) | 0.198→0.094 |
| descend_to_goal | descend | 1.00 / step_budget | (0.600, 0.173, 0.314)→(0.601, 0.177, 0.181) | (0.583, 0.141, 0.099)→(0.591, 0.149, 0.016) | 0.094→0.166 |
| release_goal | release | 1.00 / step_budget | (0.601, 0.177, 0.181)→(0.595, 0.175, 0.200) | (0.591, 0.149, 0.016)→(0.591, 0.149, 0.016) | 0.166→0.166 |
| retract_goal | retract | 1.00 / step_budget | (0.595, 0.175, 0.200)→(0.605, 0.179, 0.442) | (0.591, 0.149, 0.016)→(0.591, 0.149, 0.016) | 0.166→0.166 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.533
- phase_score: 0.356
- phase_breakdown.reach_object_score: 0.790
- phase_breakdown.reach_goal_score: 0.395
- phase_breakdown.place_done_score: 0.000
- grasp_place_fitness: 0.735

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.735
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.533
- **Median Q (composite search score)**: -0.099
- **K-run variance**: 0.0046
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.388


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35991,"average_solve_count":439.0,"average_success_count":439.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.2136,"approach_goal.approach_goal_speed":0.07085,"approach_object.approach_height":0.23148,"approach_object.approach_speed":0.11614,"descend_to_goal.descend_goal_speed":0.03978,"descend_to_grasp.descend_speed":0.02014,"descend_to_grasp.grasp_offset_z":0.01012,"lift_1.lift_height":0.14362,"lift_1.lift_speed":0.08694,"retract_goal.retract_goal_height":0.30007,"retract_goal.retract_speed":0.07639},"optimized_scores":{"best_composite_score":0.0053,"best_fitness_score":0.7353,"best_task_score":0.53324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.59271,0.16027,-0.0035],"force_p95":0.70633,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75636,"mean_force":0.18159,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58792,0.15909,0.29417]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.52777,0.02854,-0.00147],"force_p95":0.43602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5038,"mean_force":0.11283,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51509,0.02892,0.04123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6162.0,"contact_point_centroid":[0.51573,0.0476,0.09452],"force_p95":0.11196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3209,"mean_force":0.0729,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51261,0.02876,0.09259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5882.0,"contact_point_centroid":[0.51581,0.00991,0.09768],"force_p95":0.11257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32041,"mean_force":0.07498,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51258,0.02876,0.09547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4842.0,"contact_point_centroid":[0.5399,0.05081,0.20077],"force_p95":0.15992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25467,"mean_force":0.09322,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53412,0.06919,0.20148]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03056,-0.00215],"force_p95":0.16564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22932,"mean_force":0.13398,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51762,0.02909,0.04121]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4749.0,"contact_point_centroid":[0.54234,0.09196,0.20488],"force_p95":0.12931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1756,"mean_force":0.09402,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53673,0.0736,0.20597]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.51731,0.0098,0.04261],"force_p95":0.08162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1545,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51644,0.02902,0.03986]},{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.5305,0.03079,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12404,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5079,0.00887,0.28639]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52001,0.02437,0.16001]},{"body_a":"world","body_b":"grasp_target","contact_count":1684.0,"contact_point_centroid":[0.59264,0.16014,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59628,0.17508,0.21889]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59264,0.16014,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.59179,0.17513,0.12197]},{"body_a":"world","body_b":"grasp_target","contact_count":3908.0,"contact_point_centroid":[0.59264,0.16014,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.59319,0.17561,0.2645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5029.0,"contact_point_centroid":[0.51726,0.04819,0.04166],"force_p95":0.07453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07751,"mean_force":0.04441,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51644,0.02902,0.03986]},{"body_a":"left_finger","body_b":"right_finger","contact_count":770.0,"contact_point_centroid":[0.59038,0.16237,0.29971],"force_p95":0.01251,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01087,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58989,0.16235,0.29759]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1790.0,"contact_point_centroid":[0.5969,0.17511,0.22118],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59628,0.17508,0.2189]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59264,0.16014,0.01602],"final_tcp_position":[0.60018,0.17789,0.38842],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.026],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18337,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.51741,0.01937,0.27088],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24549,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.026],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18337,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52491,0.02955,0.04972],"tcp_start":[0.51741,0.01937,0.27088],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02934,0.02548],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51641,0.02901,0.03982],"tcp_start":[0.52491,0.02955,0.04972],"tcp_to_object_dist_end":0.02008,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.52903,0.02913,0.14389],"object_pos_start":[0.53046,0.02934,0.02548],"object_to_goal_dist_end":0.16993,"object_to_goal_dist_start":0.18479,"object_z_max":0.14364,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51264,0.02876,0.16402],"tcp_start":[0.51641,0.02901,0.03982],"tcp_to_object_dist_end":0.02596,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.59264,0.16014,0.01601],"object_pos_start":[0.52903,0.02913,0.14389],"object_to_goal_dist_end":0.09433,"object_to_goal_dist_start":0.16993,"object_z_max":0.22552,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.5969,0.17398,0.31299],"tcp_start":[0.59466,0.16998,0.30524],"tcp_to_object_dist_end":0.29733,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.59264,0.16014,0.01602],"object_pos_start":[0.59264,0.16014,0.01602],"object_to_goal_dist_end":0.09432,"object_to_goal_dist_start":0.09432,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.59698,0.17677,0.12195],"tcp_start":[0.5969,0.17398,0.31299],"tcp_to_object_dist_end":0.10732,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59264,0.16014,0.01602],"object_pos_start":[0.59264,0.16014,0.01602],"object_to_goal_dist_end":0.09432,"object_to_goal_dist_start":0.09432,"object_z_max":0.01602,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.58997,0.17452,0.14176],"tcp_start":[0.59698,0.17677,0.12195],"tcp_to_object_dist_end":0.12659,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.59264,0.16014,0.01602],"object_pos_start":[0.59264,0.16014,0.01602],"object_to_goal_dist_end":0.09432,"object_to_goal_dist_start":0.09432,"object_z_max":0.01602,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.60018,0.17789,0.38842],"tcp_start":[0.58997,0.17452,0.14176],"tcp_to_object_dist_end":0.3729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09819,"average_solve_count":387.0,"average_success_count":387.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.10268,"approach_goal.approach_goal_speed":0.06157,"approach_object.approach_height":0.12237,"approach_object.approach_speed":0.08731,"descend_to_goal.descend_goal_speed":0.02023,"descend_to_grasp.descend_speed":0.09811,"descend_to_grasp.grasp_offset_z":0.01187,"lift_1.lift_height":0.14239,"lift_1.lift_speed":0.09206,"retract_goal.retract_goal_height":0.31286,"retract_goal.retract_speed":0.05161},"optimized_scores":{"best_composite_score":-0.15841,"best_fitness_score":0.57159,"best_task_score":0.20965},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":389.0,"contact_point_centroid":[0.61571,0.20202,-0.006],"force_p95":1.1726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1474,"mean_force":0.27297,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58201,0.182,0.28332]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50175,-0.01487,-0.00138],"force_p95":0.41078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45353,"mean_force":0.1048,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48987,-0.01512,0.04431]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5883.0,"contact_point_centroid":[0.4897,0.00393,0.09907],"force_p95":0.11002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30785,"mean_force":0.07054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48743,-0.01508,0.09661]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6510.0,"contact_point_centroid":[0.48974,-0.03393,0.09729],"force_p95":0.10646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28364,"mean_force":0.06552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48743,-0.01508,0.09559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10144.0,"contact_point_centroid":[0.53436,0.05468,0.24088],"force_p95":0.12341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26654,"mean_force":0.08293,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52836,0.07315,0.24084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9772.0,"contact_point_centroid":[0.53596,0.09506,0.24387],"force_p95":0.12415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20359,"mean_force":0.08526,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53001,0.07653,0.24382]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01557,-0.00205],"force_p95":0.13884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17592,"mean_force":0.12687,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49218,-0.01515,0.04425]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49964,-0.00619,0.23747]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.49145,0.00415,0.0458],"force_p95":0.07835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13429,"mean_force":0.0522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49104,-0.01513,0.04304]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61591,0.20184,-0.00198],"force_p95":0.12553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12687,"mean_force":0.12307,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.57998,0.18306,0.26216]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49868,-0.01408,0.11171]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.61591,0.20184,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.58212,0.18445,0.40324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5388.0,"contact_point_centroid":[0.49079,-0.03419,0.0457],"force_p95":0.06489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08217,"mean_force":0.04074,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49104,-0.01513,0.04304]},{"body_a":"left_finger","body_b":"right_finger","contact_count":296.0,"contact_point_centroid":[0.58267,0.18256,0.28],"force_p95":0.01484,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.01149,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58227,0.18254,0.2777]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.58236,0.18381,0.26041],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01107,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.58176,0.18379,0.258]}],"total_contact_groups":15},"final_pose_error":0.03224,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.61591,0.20184,0.01602],"final_tcp_position":[0.58763,0.18716,0.52875],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50033,-0.01299,0.17169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14573,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.4992,-0.01523,0.05198],"tcp_start":[0.50033,-0.01299,0.17169],"tcp_to_object_dist_end":0.02637,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01511,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49101,-0.01513,0.043],"tcp_start":[0.4992,-0.01523,0.05198],"tcp_to_object_dist_end":0.0214,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":392.0,"n_steps_budget":960.0,"object_pos_end":[0.50319,-0.01507,0.14426],"object_pos_start":[0.50374,-0.01511,0.0258],"object_to_goal_dist_end":0.2425,"object_to_goal_dist_start":0.31204,"object_z_max":0.14399,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48742,-0.01506,0.16595],"tcp_start":[0.49101,-0.01513,0.043],"tcp_to_object_dist_end":0.02681,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.59409,0.17938,0.26429],"object_pos_start":[0.50319,-0.01507,0.14426],"object_to_goal_dist_end":0.01945,"object_to_goal_dist_start":0.2425,"object_z_max":0.29617,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.58081,0.17778,0.33468],"tcp_start":[0.48742,-0.01506,0.16595],"tcp_to_object_dist_end":0.07165,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.61591,0.20194,0.01649],"object_pos_start":[0.59409,0.17938,0.26429],"object_to_goal_dist_end":0.23388,"object_to_goal_dist_start":0.01945,"object_z_max":0.26429,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.5831,0.18416,0.26185],"tcp_start":[0.58081,0.17778,0.33468],"tcp_to_object_dist_end":0.24818,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61591,0.20184,0.01602],"object_pos_start":[0.61591,0.20194,0.01649],"object_to_goal_dist_end":0.23435,"object_to_goal_dist_start":0.23388,"object_z_max":0.01649,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.57901,0.18263,0.28197],"tcp_start":[0.5831,0.18416,0.26185],"tcp_to_object_dist_end":0.26918,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61591,0.20184,0.01602],"object_pos_start":[0.61591,0.20184,0.01602],"object_to_goal_dist_end":0.23435,"object_to_goal_dist_start":0.23435,"object_z_max":0.01602,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.58763,0.18716,0.52875],"tcp_start":[0.57901,0.18263,0.28197],"tcp_to_object_dist_end":0.51372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55973,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_height":0.15645,"approach_goal.approach_goal_speed":0.06903,"approach_object.approach_height":0.14241,"approach_object.approach_speed":0.09384,"descend_to_goal.descend_goal_speed":0.05516,"descend_to_grasp.descend_speed":0.07364,"descend_to_grasp.grasp_offset_z":0.01002,"lift_1.lift_height":0.1771,"lift_1.lift_speed":0.0938,"retract_goal.retract_goal_height":0.28478,"retract_goal.retract_speed":0.12451},"optimized_scores":{"best_composite_score":-0.09877,"best_fitness_score":0.63123,"best_task_score":0.32506},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1739.0,"contact_point_centroid":[0.56371,0.08478,-0.00266],"force_p95":0.27844,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03998,"mean_force":0.15002,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58809,0.13409,0.26494]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.5102,0.03738,-0.00145],"force_p95":0.42948,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47836,"mean_force":0.10459,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49801,0.03766,0.04205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7269.0,"contact_point_centroid":[0.49877,0.01863,0.11318],"force_p95":0.11165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31132,"mean_force":0.07337,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49561,0.03747,0.11102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7585.0,"contact_point_centroid":[0.49861,0.05633,0.10913],"force_p95":0.11149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30871,"mean_force":0.07161,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49563,0.03747,0.10724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1550.0,"contact_point_centroid":[0.51826,0.07435,0.20584],"force_p95":0.19005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23245,"mean_force":0.11843,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51224,0.05606,0.20854]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03946,-0.00216],"force_p95":0.16866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23182,"mean_force":0.13467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,0.03787,0.04183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1907.0,"contact_point_centroid":[0.51872,0.03861,0.20622],"force_p95":0.14832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21875,"mean_force":0.0987,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51276,0.05657,0.20894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3893.0,"contact_point_centroid":[0.5002,0.01857,0.04347],"force_p95":0.08416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15584,"mean_force":0.05409,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49928,0.03778,0.04057]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50309,0.01536,0.24639]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50628,0.03522,0.11978]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.5637,0.08482,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62143,0.16894,0.22751]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5637,0.08482,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.61821,0.16918,0.15801]},{"body_a":"world","body_b":"grasp_target","contact_count":3580.0,"contact_point_centroid":[0.5637,0.08482,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.62009,0.16981,0.29239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.49992,0.05693,0.0424],"force_p95":0.07569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07998,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49928,0.03778,0.04058]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1664.0,"contact_point_centroid":[0.59294,0.13852,0.27042],"force_p95":0.01178,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59243,0.1385,0.26822]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1228.0,"contact_point_centroid":[0.62191,0.16896,0.22992],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62142,0.16893,0.22773]}],"total_contact_groups":17},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5637,0.08482,0.01602],"final_tcp_position":[0.62699,0.17203,0.41003],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50747,0.03224,0.19017],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1644,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.50753,0.03842,0.04983],"tcp_start":[0.50747,0.03224,0.19017],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03815,0.02545],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21354,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49925,0.03777,0.04054],"tcp_start":[0.50753,0.03842,0.04983],"tcp_to_object_dist_end":0.02006,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.5119,0.03778,0.17629],"object_pos_start":[0.51247,0.03815,0.02545],"object_to_goal_dist_end":0.18031,"object_to_goal_dist_start":0.21354,"object_z_max":0.17603,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.4959,0.03749,0.19816],"tcp_start":[0.49925,0.03777,0.04054],"tcp_to_object_dist_end":0.0271,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":730.0,"n_steps_budget":1000.0,"object_pos_end":[0.5637,0.08482,0.01602],"object_pos_start":[0.5119,0.03778,0.17629],"object_to_goal_dist_end":0.16856,"object_to_goal_dist_start":0.18031,"object_z_max":0.19425,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.62118,0.16778,0.29327],"tcp_start":[0.61743,0.16372,0.28674],"tcp_to_object_dist_end":0.29505,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.5637,0.08482,0.01602],"object_pos_start":[0.5637,0.08482,0.01602],"object_to_goal_dist_end":0.16856,"object_to_goal_dist_start":0.16856,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62295,0.17064,0.15875],"tcp_start":[0.62118,0.16778,0.29327],"tcp_to_object_dist_end":0.17677,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5637,0.08482,0.01602],"object_pos_start":[0.5637,0.08482,0.01602],"object_to_goal_dist_end":0.16856,"object_to_goal_dist_start":0.16856,"object_z_max":0.01602,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.61657,0.16864,0.17745],"tcp_start":[0.62295,0.17064,0.15875],"tcp_to_object_dist_end":0.18942,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.5637,0.08482,0.01602],"object_pos_start":[0.5637,0.08482,0.01602],"object_to_goal_dist_end":0.16856,"object_to_goal_dist_start":0.16856,"object_z_max":0.01602,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"place_done","tcp_end":[0.62699,0.17203,0.41003],"tcp_start":[0.61657,0.16864,0.17745],"tcp_to_object_dist_end":0.40848,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```