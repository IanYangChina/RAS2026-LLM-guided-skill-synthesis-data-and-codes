## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1316 | 0.37 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1884 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1989 | 0.30 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1922 | 0.29 | ✅ accepted |
| 7 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.530500292374538, 0.030794078973649372, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.530500292374538, 0.030794078973649372, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.132) — your mutation base

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
  - 0.1
  weight: 0.25
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.35
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
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
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: lift
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: transport_to_goal
  type: approach
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
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_distance:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
  type: descend
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
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_distance:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release
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
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.05
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.132
- **task_score** (E): 0.374
- **fitness_score**: 0.662  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_grasp | 1.00 | 1.00 | 0.1018 |
| grasp | 1.00 | 1.00 | 0.0119 |
| lift | 1.00 | 1.00 | 0.1009 |
| transport_to_goal | 1.00 | 1.00 | 0.2213 |
| descend_to_place | 1.00 | 1.00 | 0.1048 |
| release | 1.00 | 1.00 | 0.0223 |
| retract | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.510, 0.018, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, 0.018, 0.036)→(0.502, 0.017, 0.027) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.000 | 0.157 | 0.215 |
| lift | lift | 1.00 / step_budget | (0.502, 0.017, 0.027)→(0.498, 0.017, 0.128) | (0.515, 0.017, 0.025)→(0.515, 0.017, 0.116) | 0.237→0.202 | 1.00 / 23.333 | 78.575 | 0.708 |
| transport_to_goal | approach | 1.00 / step_budget | (0.498, 0.017, 0.128)→(0.597, 0.200, 0.167) | (0.515, 0.017, 0.116)→(0.573, 0.142, 0.016) | 0.202→0.163 | 1.00 / 6.667 | 0.120 | 1.311 |
| descend_to_place | descend | 1.00 / step_budget | (0.597, 0.200, 0.167)→(0.592, 0.198, 0.062) | (0.573, 0.142, 0.016)→(0.573, 0.142, 0.016) | 0.163→0.163 | 1.00 / 11.000 | 3253.862 | 0.446 |
| release | release | 1.00 / step_budget | (0.592, 0.198, 0.062)→(0.585, 0.195, 0.083) | (0.573, 0.142, 0.016)→(0.573, 0.142, 0.016) | 0.163→0.163 | 1.00 / 4.000 | 0.123 | 2.140 |
| retract | retract | 1.00 / step_budget | (0.585, 0.195, 0.083)→(0.582, 0.194, 0.042) | (0.573, 0.142, 0.016)→(0.573, 0.142, 0.016) | 0.163→0.164 | 1.00 / 17.667 | 1.648 | 1.727 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.533
- phase_score: 0.190
- phase_breakdown.reach_object_score: 0.179
- phase_breakdown.reach_goal_score: 0.035
- phase_breakdown.lift_object_score: 0.373
- grasp_place_fitness: 0.739

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.739
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.533
- **Median Q (composite search score)**: 0.156
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.245


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
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.625,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12873,"descend_to_grasp.descend_speed":0.05394,"descend_to_place.descend_distance":0.11417,"descend_to_place.place_speed":0.07256,"lift.lift_height":0.11161,"transport_to_goal.transport_distance":0.26555,"transport_to_goal.transport_speed":0.10628},"optimized_scores":{"best_composite_score":0.20934,"best_fitness_score":0.73934,"best_task_score":0.53275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":1223.0,"contact_point_centroid":[0.6133,0.25108,-0.00128],"force_p95":1.73122,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.1736,"mean_force":1.10299,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61338,0.24775,0.00396]},{"body_a":"world","body_b":"left_finger","contact_count":1203.0,"contact_point_centroid":[0.61338,0.24432,-0.00124],"force_p95":1.80519,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.65043,"mean_force":1.15362,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61339,0.24776,0.00393]},{"body_a":"world","body_b":"right_finger","contact_count":1402.0,"contact_point_centroid":[0.60562,0.28466,-0.0047],"force_p95":4.60952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.93509,"mean_force":2.99795,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60632,0.24486,-0.00476]},{"body_a":"world","body_b":"left_finger","contact_count":1254.0,"contact_point_centroid":[0.60662,0.20475,-0.00412],"force_p95":4.22633,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.54205,"mean_force":2.78465,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6064,0.24489,-0.0055]},{"body_a":"world","body_b":"right_finger","contact_count":2.0,"contact_point_centroid":[0.6232,0.25506,-2e-05],"force_p95":1.08186,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.08472,"mean_force":1.0561,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61578,0.24877,0.00767]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.58763,0.17226,-0.00254],"force_p95":0.33344,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08189,"mean_force":0.14784,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59703,0.20377,0.11663]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52749,0.02859,-0.00122],"force_p95":0.38879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55057,"mean_force":0.0814,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51444,0.02925,0.0368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8978.0,"contact_point_centroid":[0.51507,0.01026,0.08063],"force_p95":0.10848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32068,"mean_force":0.0712,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51186,0.02908,0.07867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9381.0,"contact_point_centroid":[0.51517,0.04787,0.0792],"force_p95":0.10465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.316,"mean_force":0.06919,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5119,0.02908,0.07743]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2628.0,"contact_point_centroid":[0.53795,0.05716,0.1259],"force_p95":0.17984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28282,"mean_force":0.11524,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53281,0.07554,0.12689]},{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.58779,0.17232,-0.00209],"force_p95":0.21357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26887,"mean_force":0.13469,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60675,0.24502,0.00633]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03055,-0.00213],"force_p95":0.15917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22715,"mean_force":0.13229,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51731,0.02944,0.03638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3266.0,"contact_point_centroid":[0.53992,0.09678,0.12524],"force_p95":0.14534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22054,"mean_force":0.09434,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53433,0.0788,0.12647]},{"body_a":"grasp_target","body_b":"hand","contact_count":49.0,"contact_point_centroid":[0.62102,0.18839,0.03277],"force_p95":0.19189,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20163,"mean_force":0.15622,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60671,0.24503,-0.00769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.5171,0.01016,0.03774],"force_p95":0.08058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15105,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51609,0.02936,0.035]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51089,0.01383,0.2182]}],"total_contact_groups":23},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58875,0.17291,0.01468],"final_tcp_position":[0.60793,0.24554,-0.01183],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":12.77341,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52419,0.02818,0.13726],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52421,0.0299,0.04428],"tcp_start":[0.52419,0.02818,0.13726],"tcp_to_object_dist_end":0.01933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02951,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18463,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15204,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10870.0,"raw_peak_contact_force":0.22715,"tcp_end":[0.51606,0.02936,0.03497],"tcp_start":[0.52421,0.0299,0.04428],"tcp_to_object_dist_end":0.01717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52599,0.02918,0.11618],"object_pos_start":[0.53043,0.02951,0.02557],"object_to_goal_dist_end":0.16761,"object_to_goal_dist_start":0.18463,"object_z_max":0.11607,"peak_contact_force":0.10832,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18505.0,"raw_peak_contact_force":0.55057,"subtask_id":"lift_object","tcp_end":[0.51197,0.0291,0.13435],"tcp_start":[0.51606,0.02936,0.03497],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.58781,0.17234,0.01602],"object_pos_start":[0.52599,0.02918,0.11618],"object_to_goal_dist_end":0.0933,"object_to_goal_dist_start":0.16761,"object_z_max":0.11621,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8185.0,"raw_peak_contact_force":1.08189,"subtask_id":"reach_goal","tcp_end":[0.62125,0.25104,0.11346],"tcp_start":[0.51197,0.0291,0.13435],"tcp_to_object_dist_end":0.12964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.58781,0.17234,0.01602],"object_pos_start":[0.58781,0.17234,0.01602],"object_to_goal_dist_end":0.0933,"object_to_goal_dist_start":0.0933,"object_z_max":0.01602,"peak_contact_force":12.77341,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2309.0,"raw_peak_contact_force":1.08472,"subtask_id":"reach_goal","tcp_end":[0.61576,0.24877,0.00731],"tcp_start":[0.62125,0.25104,0.11346],"tcp_to_object_dist_end":0.08184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58781,0.17234,0.01602],"object_pos_start":[0.58781,0.17234,0.01602],"object_to_goal_dist_end":0.0933,"object_to_goal_dist_start":0.0933,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3522.0,"raw_peak_contact_force":6.1736,"tcp_end":[0.60894,0.24589,0.02832],"tcp_start":[0.61576,0.24877,0.00731],"tcp_to_object_dist_end":0.0775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.58875,0.17291,0.01468],"object_pos_start":[0.58781,0.17234,0.01602],"object_to_goal_dist_end":0.09445,"object_to_goal_dist_start":0.0933,"object_z_max":0.01602,"peak_contact_force":4.69796,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3297.0,"raw_peak_contact_force":4.93509,"tcp_end":[0.60793,0.24554,-0.01183],"tcp_start":[0.60894,0.24589,0.02832],"tcp_to_object_dist_end":0.07966,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54008,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06806,"descend_to_grasp.descend_speed":0.07991,"descend_to_place.descend_distance":0.12805,"descend_to_place.place_speed":0.03373,"lift.lift_height":0.1109,"transport_to_goal.transport_distance":0.25186,"transport_to_goal.transport_speed":0.15381},"optimized_scores":{"best_composite_score":0.02957,"best_fitness_score":0.55957,"best_task_score":0.16976},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.51884,0.07718,-0.00259],"force_p95":0.31871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53693,"mean_force":0.1584,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53685,0.12302,0.20098]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.50049,-0.01525,-0.00133],"force_p95":0.77274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9853,"mean_force":0.12542,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48901,-0.01546,0.01686]},{"body_a":"grasp_target","body_b":"hand","contact_count":254.0,"contact_point_centroid":[0.50472,-0.01186,0.07157],"force_p95":0.10128,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45461,"mean_force":0.07577,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48681,-0.01542,0.03325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2545.0,"contact_point_centroid":[0.50008,0.03504,0.12991],"force_p95":0.20643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31028,"mean_force":0.10816,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49618,0.01693,0.13171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2143.0,"contact_point_centroid":[0.49869,-0.00559,0.12761],"force_p95":0.2103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29778,"mean_force":0.10825,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49477,0.01285,0.12924]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9834.0,"contact_point_centroid":[0.48875,0.00355,0.06222],"force_p95":0.10664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28875,"mean_force":0.06695,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48649,-0.01541,0.06031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10774.0,"contact_point_centroid":[0.48857,-0.03423,0.05941],"force_p95":0.1068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27,"mean_force":0.06196,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48654,-0.01542,0.05815]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50362,-0.01548,-0.00231],"force_p95":0.16427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17757,"mean_force":0.14377,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49193,-0.0155,0.01595]},{"body_a":"world","body_b":"grasp_target","contact_count":2068.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49879,-0.00699,0.21938]},{"body_a":"world","body_b":"grasp_target","contact_count":3180.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49768,-0.015,0.07106]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.5186,0.07688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55307,0.17091,0.17448]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5186,0.07688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.54703,0.16889,0.11599]},{"body_a":"world","body_b":"grasp_target","contact_count":520.0,"contact_point_centroid":[0.5186,0.07688,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54294,0.16764,0.11698]},{"body_a":"grasp_target","body_b":"hand","contact_count":381.0,"contact_point_centroid":[0.50854,-0.01744,0.05409],"force_p95":0.09377,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11292,"mean_force":0.08493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49111,-0.01549,0.01511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.49038,-0.03455,0.01699],"force_p95":0.06367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08305,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49073,-0.01548,0.01471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4131.0,"contact_point_centroid":[0.49101,0.0038,0.01706],"force_p95":0.07705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07738,"mean_force":0.05165,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49073,-0.01548,0.01471]}],"total_contact_groups":19},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5186,0.07688,0.01602],"final_tcp_position":[0.54124,0.16708,0.0952],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.68919,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2068.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4996,-0.01429,0.13881],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3180.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49876,-0.01558,0.02303],"tcp_start":[0.4996,-0.01429,0.13881],"tcp_to_object_dist_end":0.00587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50287,-0.01528,0.02507],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31291,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.16259,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11688.0,"raw_peak_contact_force":0.17757,"tcp_end":[0.49069,-0.01548,0.01468],"tcp_start":[0.49876,-0.01558,0.02303],"tcp_to_object_dist_end":0.01601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50878,-0.01561,0.11154],"object_pos_start":[0.50287,-0.01528,0.02507],"object_to_goal_dist_end":0.25689,"object_to_goal_dist_start":0.31291,"object_z_max":0.11145,"peak_contact_force":0.12391,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21022.0,"raw_peak_contact_force":0.9853,"subtask_id":"lift_object","tcp_end":[0.48655,-0.0154,0.11396],"tcp_start":[0.49069,-0.01548,0.01468],"tcp_to_object_dist_end":0.02236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.5186,0.07688,0.01602],"object_pos_start":[0.50878,-0.01561,0.11154],"object_to_goal_dist_end":0.26601,"object_to_goal_dist_start":0.25689,"object_z_max":0.12981,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7459.0,"raw_peak_contact_force":1.53693,"subtask_id":"reach_goal","tcp_end":[0.55617,0.17177,0.23341],"tcp_start":[0.48655,-0.0154,0.11396],"tcp_to_object_dist_end":0.24015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.5186,0.07688,0.01602],"object_pos_start":[0.5186,0.07688,0.01602],"object_to_goal_dist_end":0.26601,"object_to_goal_dist_start":0.26601,"object_z_max":0.01602,"peak_contact_force":9748.68919,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2980.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.55197,0.17046,0.11429],"tcp_start":[0.55617,0.17177,0.23341],"tcp_to_object_dist_end":0.13974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5186,0.07688,0.01602],"object_pos_start":[0.5186,0.07688,0.01602],"object_to_goal_dist_end":0.26601,"object_to_goal_dist_start":0.26601,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54523,0.16831,0.13633],"tcp_start":[0.55197,0.17046,0.11429],"tcp_to_object_dist_end":0.15344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.5186,0.07688,0.01602],"object_pos_start":[0.5186,0.07688,0.01602],"object_to_goal_dist_end":0.26601,"object_to_goal_dist_start":0.26601,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":520.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54124,0.16708,0.0952],"tcp_start":[0.54523,0.16831,0.13633],"tcp_to_object_dist_end":0.12214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28947,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.084,"descend_to_grasp.descend_speed":0.02601,"descend_to_place.descend_distance":0.09716,"descend_to_place.place_speed":0.06776,"lift.lift_height":0.11569,"transport_to_goal.transport_distance":0.20116,"transport_to_goal.transport_speed":0.11504},"optimized_scores":{"best_composite_score":0.15592,"best_fitness_score":0.68592,"best_task_score":0.42013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":263.0,"contact_point_centroid":[0.61122,0.1767,-0.00534],"force_p95":1.09982,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31388,"mean_force":0.28637,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.6065,0.16795,0.15299]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50961,0.03696,-0.00123],"force_p95":0.42811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58956,"mean_force":0.0835,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49731,0.03791,0.03437]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9788.0,"contact_point_centroid":[0.49762,0.01886,0.08059],"force_p95":0.10642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32347,"mean_force":0.0687,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49476,0.03771,0.0787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10209.0,"contact_point_centroid":[0.49771,0.05656,0.07872],"force_p95":0.10422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32075,"mean_force":0.06688,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4948,0.03771,0.07701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3473.0,"contact_point_centroid":[0.53912,0.06674,0.13868],"force_p95":0.17905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27207,"mean_force":0.11139,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53374,0.08503,0.13991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3835.0,"contact_point_centroid":[0.54101,0.10524,0.13858],"force_p95":0.16323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26559,"mean_force":0.10318,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53549,0.08713,0.14013]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03943,-0.00215],"force_p95":0.16592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24135,"mean_force":0.13401,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50011,0.03815,0.0338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4063.0,"contact_point_centroid":[0.49963,0.01884,0.03529],"force_p95":0.08166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15087,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49892,0.03805,0.03251]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5028,0.01775,0.21881]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.61164,0.17748,-0.00195],"force_p95":0.12721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12944,"mean_force":0.12196,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61008,0.17508,0.11032]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50591,0.03779,0.07287]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61164,0.17749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60276,0.1727,0.06555]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.61164,0.17749,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59799,0.17126,0.06587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.4996,0.05723,0.03431],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08208,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49893,0.03805,0.03252]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1029.0,"contact_point_centroid":[0.61046,0.17508,0.11174],"force_p95":0.01231,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01062,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61001,0.17506,0.10948]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.60684,0.17383,0.06383],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00985,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60631,0.1738,0.06168]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61164,0.17749,0.01602],"final_tcp_position":[0.59595,0.17063,0.04393],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":235.492,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50775,0.03631,0.13784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50683,0.0387,0.04117],"tcp_start":[0.50775,0.03631,0.13784],"tcp_to_object_dist_end":0.01621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03819,0.0255],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21351,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15711,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10888.0,"raw_peak_contact_force":0.24135,"tcp_end":[0.49889,0.03805,0.03248],"tcp_start":[0.50683,0.0387,0.04117],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.50961,0.03785,0.12002],"object_pos_start":[0.51243,0.03819,0.0255],"object_to_goal_dist_end":0.18076,"object_to_goal_dist_start":0.21351,"object_z_max":0.11991,"peak_contact_force":235.492,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20142.0,"raw_peak_contact_force":0.58956,"subtask_id":"lift_object","tcp_end":[0.49489,0.03773,0.13631],"tcp_start":[0.49889,0.03805,0.03248],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.61168,0.17707,0.01641],"object_pos_start":[0.50961,0.03785,0.12002],"object_to_goal_dist_end":0.12967,"object_to_goal_dist_start":0.18076,"object_z_max":0.12347,"peak_contact_force":0.11418,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7571.0,"raw_peak_contact_force":1.31388,"subtask_id":"reach_goal","tcp_end":[0.61351,0.17597,0.15423],"tcp_start":[0.49489,0.03773,0.13631],"tcp_to_object_dist_end":0.13784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.61164,0.17749,0.01602],"object_pos_start":[0.61168,0.17707,0.01641],"object_to_goal_dist_end":0.13008,"object_to_goal_dist_start":0.12967,"object_z_max":0.01662,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2005.0,"raw_peak_contact_force":0.12944,"subtask_id":"reach_goal","tcp_end":[0.60865,0.1745,0.06546],"tcp_start":[0.61351,0.17597,0.15423],"tcp_to_object_dist_end":0.04962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61164,0.17749,0.01602],"object_pos_start":[0.61164,0.17749,0.01602],"object_to_goal_dist_end":0.13008,"object_to_goal_dist_start":0.13008,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60058,0.17202,0.08521],"tcp_start":[0.60865,0.1745,0.06546],"tcp_to_object_dist_end":0.07028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.61164,0.17749,0.01602],"object_pos_start":[0.61164,0.17749,0.01602],"object_to_goal_dist_end":0.13008,"object_to_goal_dist_start":0.13008,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":492.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59595,0.17063,0.04393],"tcp_start":[0.60058,0.17202,0.08521],"tcp_to_object_dist_end":0.03275,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```