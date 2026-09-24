## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0727 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1121 | 0.40 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 13 | -0.0441 | 0.39 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1074 | 0.41 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1079 | 0.41 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.073) — your mutation base

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

- **Composite score**: -0.073
- **task_score** (E): 0.219
- **fitness_score**: 0.577  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object | 1.00 | 0.0899 |
| descend_to_grasp | 1.00 | 0.1643 |
| grasp_1 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 0.1810 |
| approach_goal | 0.00 | 0.0002 |
| release_goal | 1.00 | 0.0253 |
| retract_goal | 0.67 | 0.2634 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.014, 0.215) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.014, 0.215)→(0.511, 0.018, 0.051) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.051)→(0.502, 0.017, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.042)→(0.499, 0.017, 0.223) | (0.516, 0.018, 0.026)→(0.509, 0.017, 0.202) | 0.237→0.215 |
| approach_goal | approach | 0.00 / guard_failure | (0.499, 0.017, 0.223)→(0.499, 0.017, 0.223) | (0.509, 0.017, 0.202)→(0.509, 0.017, 0.202) | 0.215→0.215 |
| release_goal | release | 1.00 / step_budget | (0.499, 0.017, 0.223)→(0.495, 0.017, 0.248) | (0.509, 0.017, 0.202)→(0.502, 0.016, 0.015) | 0.215→0.250 |
| retract_goal | retract | 0.67 / step_budget | (0.495, 0.017, 0.248)→(0.591, 0.154, 0.445) | (0.502, 0.016, 0.015)→(0.525, 0.020, 0.016) | 0.250→0.237 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.292
- phase_score: 0.253
- phase_breakdown.reach_object_score: 0.822
- phase_breakdown.reach_goal_score: 0.012
- phase_breakdown.place_done_score: 0.008
- grasp_place_fitness: 0.613

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.613
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.292
- **Median Q (composite search score)**: -0.061
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2521,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.03297,"approach_goal.approach_goal_z_adj":0.03306,"approach_object.approach_height":0.14976,"approach_object.approach_speed":0.08523,"descend_to_grasp.descend_speed":0.0417,"descend_to_grasp.grasp_offset_z":0.01211,"lift_1.lift_height":0.22242,"lift_1.lift_speed":0.05027,"retract_goal.retract_goal_height":0.33574,"retract_goal.retract_speed":0.13773},"optimized_scores":{"best_composite_score":-0.03743,"best_fitness_score":0.61257,"best_task_score":0.29235},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":107.0,"contact_point_centroid":[0.50666,0.03095,-0.01096],"force_p95":1.61825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97914,"mean_force":0.73077,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.50943,0.02871,0.26217]},{"body_a":"world","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.53746,0.03138,-0.00216],"force_p95":0.17851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54348,"mean_force":0.12834,"phase_index":6.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.55477,0.1043,0.35147]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.5265,0.0289,-0.00152],"force_p95":0.43537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45349,"mean_force":0.14883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51536,0.02913,0.04331]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14663.0,"contact_point_centroid":[0.51346,0.04808,0.14414],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29422,"mean_force":0.05287,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51292,0.02897,0.14196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13766.0,"contact_point_centroid":[0.51364,0.00983,0.14562],"force_p95":0.08043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29032,"mean_force":0.0552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51293,0.02897,0.14296]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03059,-0.00213],"force_p95":0.16004,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.222,"mean_force":0.13255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51767,0.02929,0.04345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4080.0,"contact_point_centroid":[0.51735,0.01,0.04485],"force_p95":0.08085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1497,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51649,0.02921,0.0421]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51002,0.01185,0.24938]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52207,0.0272,0.12408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1222.0,"contact_point_centroid":[0.51292,0.00975,0.24544],"force_p95":0.07238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11508,"mean_force":0.04294,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.51247,0.02894,0.24297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1215.0,"contact_point_centroid":[0.51358,0.04813,0.2453],"force_p95":0.07224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11166,"mean_force":0.04372,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.51251,0.02895,0.24306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18.0,"contact_point_centroid":[0.51448,0.00983,0.24748],"force_p95":0.08362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08863,"mean_force":0.06496,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51355,0.02901,0.24495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.51471,0.04813,0.24739],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07686,"mean_force":0.05025,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51355,0.02901,0.24495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5004.0,"contact_point_centroid":[0.5173,0.04837,0.04389],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07592,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02921,0.04211]}],"total_contact_groups":14},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53935,0.03132,0.01602],"final_tcp_position":[0.59631,0.17003,0.42659],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"phases":[{"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52179,0.02485,0.19633],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17064,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.52493,0.02975,0.05197],"tcp_start":[0.52179,0.02485,0.19633],"tcp_to_object_dist_end":0.02656,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.02952,0.02555],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18462,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.51646,0.02921,0.04207],"tcp_start":[0.52493,0.02975,0.05197],"tcp_to_object_dist_end":0.02165,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.52152,0.02895,0.22304],"object_pos_start":[0.53046,0.02952,0.02555],"object_to_goal_dist_end":0.20495,"object_to_goal_dist_start":0.18462,"object_z_max":0.22278,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.51355,0.02901,0.24495],"tcp_start":[0.51646,0.02921,0.04207],"tcp_to_object_dist_end":0.02331,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52158,0.02895,0.22317],"object_pos_start":[0.52152,0.02895,0.22304],"object_to_goal_dist_end":0.205,"object_to_goal_dist_start":0.20495,"object_z_max":0.22304,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.51361,0.02901,0.24513],"tcp_start":[0.51355,0.02901,0.24495],"tcp_to_object_dist_end":0.02336,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,0.02732,0.01586],"object_pos_start":[0.52158,0.02895,0.22317],"object_to_goal_dist_end":0.19779,"object_to_goal_dist_start":0.205,"object_z_max":0.22322,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.50937,0.02871,0.26949],"tcp_start":[0.51361,0.02901,0.24513],"tcp_to_object_dist_end":0.25366,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.53935,0.03132,0.01602],"object_pos_start":[0.51359,0.02732,0.01586],"object_to_goal_dist_end":0.18447,"object_to_goal_dist_start":0.19779,"object_z_max":0.02933,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.59631,0.17003,0.42659],"tcp_start":[0.50937,0.02871,0.26949],"tcp_to_object_dist_end":0.4371,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40722,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.11698,"approach_goal.approach_goal_z_adj":0.02036,"approach_object.approach_height":0.16207,"approach_object.approach_speed":0.11361,"descend_to_grasp.descend_speed":0.05312,"descend_to_grasp.grasp_offset_z":0.01105,"lift_1.lift_height":0.15203,"lift_1.lift_speed":0.06097,"retract_goal.retract_goal_height":0.35883,"retract_goal.retract_speed":0.13117},"optimized_scores":{"best_composite_score":-0.12008,"best_fitness_score":0.52992,"best_task_score":0.12475},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.48882,-0.01148,-0.00983],"force_p95":1.63098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70498,"mean_force":0.77782,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.48243,-0.01496,0.19251]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.50127,-0.01481,-0.00138],"force_p95":0.40828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45134,"mean_force":0.11519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48981,-0.0151,0.04349]},{"body_a":"world","body_b":"grasp_target","contact_count":3831.0,"contact_point_centroid":[0.51029,-0.00766,-0.00209],"force_p95":0.16554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36439,"mean_force":0.12704,"phase_index":6.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.5196,0.05997,0.34551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8221.0,"contact_point_centroid":[0.48822,0.00406,0.10903],"force_p95":0.08744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30942,"mean_force":0.05908,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48732,-0.01506,0.10657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8718.0,"contact_point_centroid":[0.48824,-0.03411,0.10742],"force_p95":0.0835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28591,"mean_force":0.05633,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48732,-0.01506,0.10544]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.4887,-0.03375,0.17373],"force_p95":0.10808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27573,"mean_force":0.06087,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.48595,-0.01502,0.17294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.48785,0.00404,0.17393],"force_p95":0.11356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23581,"mean_force":0.05908,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.48581,-0.01502,0.17282]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01555,-0.00205],"force_p95":0.13766,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17161,"mean_force":0.1267,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.01513,0.04353]},{"body_a":"world","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.50382,-0.01567,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49984,-0.00567,0.25727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.49138,0.00409,0.04508],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12871,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01512,0.04231]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49863,-0.01361,0.13097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.48954,0.00384,0.17614],"force_p95":0.10272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11152,"mean_force":0.06861,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48742,-0.01505,0.17488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.49019,-0.03378,0.17566],"force_p95":0.09918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10583,"mean_force":0.07078,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48742,-0.01505,0.17488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.49146,-0.0342,0.04416],"force_p95":0.06946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0876,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01512,0.04231]}],"total_contact_groups":14},"final_pose_error":0.14363,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51083,-0.00703,0.01602],"final_tcp_position":[0.55618,0.12739,0.48015],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5004,-0.01209,0.21106],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1851,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49912,-0.01521,0.05126],"tcp_start":[0.5004,-0.01209,0.21106],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.0151,0.02581],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31203,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49093,-0.01512,0.04228],"tcp_start":[0.49912,-0.01521,0.05126],"tcp_to_object_dist_end":0.02086,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.5001,-0.01493,0.15447],"object_pos_start":[0.50373,-0.0151,0.02581],"object_to_goal_dist_end":0.2393,"object_to_goal_dist_start":0.31203,"object_z_max":0.15421,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.48742,-0.01505,0.17488],"tcp_start":[0.49093,-0.01512,0.04228],"tcp_to_object_dist_end":0.02403,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50018,-0.01493,0.15463],"object_pos_start":[0.5001,-0.01493,0.15447],"object_to_goal_dist_end":0.2392,"object_to_goal_dist_start":0.2393,"object_z_max":0.15447,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.48749,-0.01505,0.17505],"tcp_start":[0.48742,-0.01505,0.17488],"tcp_to_object_dist_end":0.02404,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49594,-0.01606,0.01186],"object_pos_start":[0.50018,-0.01493,0.15463],"object_to_goal_dist_end":0.32482,"object_to_goal_dist_start":0.2392,"object_z_max":0.15472,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.48234,-0.01495,0.20055],"tcp_start":[0.48749,-0.01505,0.17505],"tcp_to_object_dist_end":0.18918,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51083,-0.00703,0.01602],"object_pos_start":[0.49594,-0.01606,0.01186],"object_to_goal_dist_end":0.31222,"object_to_goal_dist_start":0.32482,"object_z_max":0.02196,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55618,0.12739,0.48015],"tcp_start":[0.48234,-0.01495,0.20055],"tcp_to_object_dist_end":0.48532,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28102,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.10852,"approach_goal.approach_goal_z_adj":0.03694,"approach_object.approach_height":0.19256,"approach_object.approach_speed":0.06106,"descend_to_grasp.descend_speed":0.06468,"descend_to_grasp.grasp_offset_z":0.01002,"lift_1.lift_height":0.22693,"lift_1.lift_speed":0.03271,"retract_goal.retract_goal_height":0.30151,"retract_goal.retract_speed":0.0907},"optimized_scores":{"best_composite_score":-0.06074,"best_fitness_score":0.58926,"best_task_score":0.24101},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.48599,0.03676,-0.01005],"force_p95":1.62788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71244,"mean_force":0.60545,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.49244,0.03709,0.26585]},{"body_a":"world","body_b":"grasp_target","contact_count":2666.0,"contact_point_centroid":[0.51987,0.03709,-0.00238],"force_p95":0.24847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55524,"mean_force":0.14132,"phase_index":6.0,"phase_name":"retract_goal","phase_type":"retract","tcp_position_centroid":[0.56349,0.10931,0.35932]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.5086,0.03725,-0.0016],"force_p95":0.43158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44311,"mean_force":0.17559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49819,0.03758,0.04158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14822.0,"contact_point_centroid":[0.49577,0.0565,0.14148],"force_p95":0.07763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28019,"mean_force":0.05207,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49583,0.03739,0.1396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14053.0,"contact_point_centroid":[0.49599,0.01824,0.14317],"force_p95":0.07778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27076,"mean_force":0.05371,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49585,0.03739,0.14076]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03946,-0.00217],"force_p95":0.17154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2382,"mean_force":0.13537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5005,0.03777,0.04181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3794.0,"contact_point_centroid":[0.50045,0.01848,0.04354],"force_p95":0.0864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15795,"mean_force":0.05538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49934,0.03768,0.04055]},{"body_a":"world","body_b":"grasp_target","contact_count":580.0,"contact_point_centroid":[0.51251,0.03972,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50279,0.01337,0.27047]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50603,0.03347,0.14354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1250.0,"contact_point_centroid":[0.4953,0.05657,0.24723],"force_p95":0.06965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11925,"mean_force":0.04262,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.49541,0.03736,0.24598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.49544,0.01819,0.24756],"force_p95":0.06865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1113,"mean_force":0.04051,"phase_index":5.0,"phase_name":"release_goal","phase_type":"release","tcp_position_centroid":[0.49543,0.03736,0.246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17.0,"contact_point_centroid":[0.49695,0.05658,0.25054],"force_p95":0.08256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08806,"mean_force":0.06275,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49647,0.03744,0.24788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.50003,0.05682,0.0424],"force_p95":0.07665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08074,"mean_force":0.04499,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49935,0.03768,0.04056]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.49704,0.01832,0.2498],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07974,"mean_force":0.05776,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49647,0.03744,0.24788]}],"total_contact_groups":14},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52469,0.03714,0.01602],"final_tcp_position":[0.62042,0.16498,0.42956],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50674,0.02881,0.23813],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21247,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.5076,0.03832,0.0498],"tcp_start":[0.50674,0.02881,0.23813],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51247,0.03808,0.02542],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2136,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49931,0.03768,0.04052],"tcp_start":[0.5076,0.03832,0.0498],"tcp_to_object_dist_end":0.02003,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.5043,0.03749,0.22796],"object_pos_start":[0.51247,0.03808,0.02542],"object_to_goal_dist_end":0.20077,"object_to_goal_dist_start":0.2136,"object_z_max":0.22769,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","tcp_end":[0.49647,0.03744,0.24788],"tcp_start":[0.49931,0.03768,0.04052],"tcp_to_object_dist_end":0.02141,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50436,0.03749,0.22809],"object_pos_start":[0.5043,0.03749,0.22796],"object_to_goal_dist_end":0.20078,"object_to_goal_dist_start":0.20077,"object_z_max":0.22796,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.49653,0.03744,0.24804],"tcp_start":[0.49647,0.03744,0.24788],"tcp_to_object_dist_end":0.02142,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49596,0.03689,0.01604],"object_pos_start":[0.50436,0.03749,0.22809],"object_to_goal_dist_end":0.22881,"object_to_goal_dist_start":0.20078,"object_z_max":0.22815,"phase_name":"release_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"place_done","tcp_end":[0.49238,0.03709,0.27285],"tcp_start":[0.49653,0.03744,0.24804],"tcp_to_object_dist_end":0.25684,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.52469,0.03714,0.01602],"object_pos_start":[0.49596,0.03689,0.01604],"object_to_goal_dist_end":0.21343,"object_to_goal_dist_start":0.22881,"object_z_max":0.03058,"phase_name":"retract_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62042,0.16498,0.42956],"tcp_start":[0.49238,0.03709,0.27285],"tcp_to_object_dist_end":0.44331,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```