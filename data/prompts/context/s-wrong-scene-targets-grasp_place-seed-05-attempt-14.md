## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1209 | 0.25 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2137 | 0.33 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2182 | 0.35 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1316 | 0.37 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1884 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.121) — your mutation base

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

- **Composite score**: 0.121
- **task_score** (E): 0.248
- **fitness_score**: 0.601  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_grasp | 1.00 | 1.00 | 0.1066 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1133 |
| transport_to_goal | 0.00 | 1.00 | 0.0177 |
| descend_to_place | 0.33 | 1.00 | 0.1252 |
| release | 1.00 | 1.00 | 0.0232 |
| retract | 1.00 | 1.00 | 0.0411 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.017, 0.138)→(0.510, 0.018, 0.031) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, 0.018, 0.031)→(0.502, 0.017, 0.023) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.000 | 0.155 | 0.221 |
| lift | lift | 1.00 / step_budget | (0.502, 0.017, 0.023)→(0.498, 0.017, 0.136) | (0.515, 0.017, 0.025)→(0.516, 0.017, 0.125) | 0.237→0.201 | 1.00 / 22.333 | 0.143 | 0.795 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.501, 0.022, 0.155)→(0.501, 0.025, 0.172) | (0.516, 0.017, 0.125)→(0.518, 0.022, 0.141) | 0.201→0.197 | 1.00 / 12.333 | 0.013 | 0.285 |
| descend_to_place | descend | 0.33 / step_budget | (0.501, 0.025, 0.172)→(0.563, 0.116, 0.142) | (0.518, 0.027, 0.151)→(0.515, 0.058, 0.016) | 0.196→0.217 | 1.00 / 8.333 | 94251.831 | 1.635 |
| release | release | 1.00 / step_budget | (0.563, 0.116, 0.142)→(0.557, 0.114, 0.164) | (0.515, 0.058, 0.016)→(0.515, 0.058, 0.016) | 0.217→0.217 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.557, 0.114, 0.164)→(0.553, 0.114, 0.123) | (0.515, 0.058, 0.016)→(0.515, 0.058, 0.016) | 0.217→0.217 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.331
- phase_score: 0.348
- phase_breakdown.reach_object_score: 0.146
- phase_breakdown.reach_goal_score: 0.346
- phase_breakdown.lift_object_score: 0.496
- grasp_place_fitness: 0.644

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.644
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.331
- **Median Q (composite search score)**: 0.130
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56818,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.11765,"descend_to_grasp.descend_speed":0.06809,"descend_to_place.place_speed":0.06281,"lift.lift_height":0.13766,"transport_to_goal.arc_height":0.1859,"transport_to_goal.transport_speed":0.11934},"optimized_scores":{"best_composite_score":0.16353,"best_fitness_score":0.64353,"best_task_score":0.33145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3680.0,"contact_point_centroid":[0.51977,0.06784,-0.00229],"force_p95":0.12428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.645,"mean_force":0.13514,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55213,0.10478,0.14799]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.52716,0.02876,-0.00118],"force_p95":0.53715,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73497,"mean_force":0.10018,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51483,0.02946,0.02652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1354.0,"contact_point_centroid":[0.5147,0.05007,0.16711],"force_p95":0.19831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38697,"mean_force":0.11158,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51142,0.0321,0.17138]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11337.0,"contact_point_centroid":[0.51527,0.01053,0.0826],"force_p95":0.11239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33248,"mean_force":0.07047,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51221,0.02929,0.08148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11353.0,"contact_point_centroid":[0.51557,0.04811,0.08019],"force_p95":0.11115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33012,"mean_force":0.07111,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51224,0.0293,0.07894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1185.0,"contact_point_centroid":[0.5143,0.01357,0.16509],"force_p95":0.19433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29483,"mean_force":0.10863,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51121,0.03164,0.16923]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03048,-0.00211],"force_p95":0.15599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24027,"mean_force":0.13163,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51772,0.02966,0.0261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.51737,0.01039,0.02747],"force_p95":0.08003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14048,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51649,0.02958,0.02472]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51091,0.01385,0.21811]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52316,0.02932,0.07125]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5197,0.06784,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57682,0.15136,0.11776]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.5197,0.06784,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57263,0.15021,0.11845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":48.0,"contact_point_centroid":[0.521,0.05278,0.1912],"force_p95":0.10216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1053,"mean_force":0.04027,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51464,0.03858,0.19795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4980.0,"contact_point_centroid":[0.5173,0.04873,0.02653],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09073,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51649,0.02958,0.02473]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3691.0,"contact_point_centroid":[0.55442,0.10783,0.14822],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01666,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55399,0.10782,0.14593]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.58075,0.15233,0.11576],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57997,0.15231,0.11349]}],"total_contact_groups":16},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5197,0.06784,0.01602],"final_tcp_position":[0.57086,0.1497,0.09661],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.645,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52422,0.0282,0.13715],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52476,0.03014,0.03402],"tcp_start":[0.52422,0.0282,0.13715],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02953,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18461,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1484,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10842.0,"raw_peak_contact_force":0.24027,"tcp_end":[0.51646,0.02958,0.02469],"tcp_start":[0.52476,0.03014,0.03402],"tcp_to_object_dist_end":0.01395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.52936,0.02943,0.13519],"object_pos_start":[0.53037,0.02953,0.02563],"object_to_goal_dist_end":0.1679,"object_to_goal_dist_start":0.18461,"object_z_max":0.13512,"peak_contact_force":0.19141,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22834.0,"raw_peak_contact_force":0.73497,"subtask_id":"lift_object","tcp_end":[0.51249,0.02932,0.14998],"tcp_start":[0.51646,0.02958,0.02469],"tcp_to_object_dist_end":0.02243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.52804,0.02951,0.13649],"object_pos_start":[0.52936,0.02943,0.13519],"object_to_goal_dist_end":0.16861,"object_to_goal_dist_start":0.1679,"object_z_max":0.17018,"peak_contact_force":0.03368,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2539.0,"raw_peak_contact_force":0.38697,"subtask_id":"reach_goal","tcp_end":[0.51423,0.03809,0.19782],"tcp_start":[0.51155,0.02944,0.15194],"tcp_to_object_dist_end":0.06345,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5197,0.06784,0.01602],"object_pos_start":[0.52751,0.04091,0.16868],"object_to_goal_dist_end":0.16564,"object_to_goal_dist_start":0.16764,"object_z_max":0.16868,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7419.0,"raw_peak_contact_force":1.645,"subtask_id":"reach_goal","tcp_end":[0.58162,0.15256,0.11627],"tcp_start":[0.51423,0.03809,0.19782],"tcp_to_object_dist_end":0.14513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5197,0.06784,0.01602],"object_pos_start":[0.5197,0.06784,0.01602],"object_to_goal_dist_end":0.16564,"object_to_goal_dist_start":0.16564,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57493,0.15081,0.13773],"tcp_start":[0.58162,0.15256,0.11627],"tcp_to_object_dist_end":0.15732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.5197,0.06784,0.01602],"object_pos_start":[0.5197,0.06784,0.01602],"object_to_goal_dist_end":0.16564,"object_to_goal_dist_start":0.16564,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":504.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57086,0.1497,0.09661],"tcp_start":[0.57493,0.15081,0.13773],"tcp_to_object_dist_end":0.12575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33758,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.19348,"descend_to_grasp.descend_speed":0.05313,"descend_to_place.place_speed":0.04345,"lift.lift_height":0.11039,"transport_to_goal.arc_height":0.06959,"transport_to_goal.transport_speed":0.17642},"optimized_scores":{"best_composite_score":0.06889,"best_fitness_score":0.54889,"best_task_score":0.14842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2101.0,"contact_point_centroid":[0.50695,0.04041,-0.00234],"force_p95":0.17882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33916,"mean_force":0.14139,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50864,0.03932,0.14627]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.50049,-0.01525,-0.00134],"force_p95":0.77641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98469,"mean_force":0.1263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48901,-0.01546,0.01682]},{"body_a":"grasp_target","body_b":"hand","contact_count":256.0,"contact_point_centroid":[0.50473,-0.01174,0.0716],"force_p95":0.10164,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45393,"mean_force":0.07606,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48681,-0.01542,0.03328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9838.0,"contact_point_centroid":[0.48875,0.00355,0.06197],"force_p95":0.10654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28834,"mean_force":0.0669,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4865,-0.01541,0.06006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10788.0,"contact_point_centroid":[0.48857,-0.03423,0.0592],"force_p95":0.10676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2695,"mean_force":0.06189,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48654,-0.01542,0.05794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4575.0,"contact_point_centroid":[0.49304,-0.01677,0.12083],"force_p95":0.16973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24795,"mean_force":0.09654,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49009,0.00159,0.12293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4682.0,"contact_point_centroid":[0.49394,0.02138,0.1218],"force_p95":0.15095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23855,"mean_force":0.09826,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.49078,0.00316,0.12379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.48942,-0.03415,0.11454],"force_p95":0.1703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19432,"mean_force":0.1024,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48602,-0.01542,0.11425]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50362,-0.01548,-0.00231],"force_p95":0.16444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17775,"mean_force":0.14394,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49193,-0.0155,0.01593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.49078,0.00316,0.11541],"force_p95":0.15328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1742,"mean_force":0.09869,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48599,-0.01542,0.11429]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49889,-0.007,0.21932]},{"body_a":"world","body_b":"grasp_target","contact_count":3416.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49767,-0.015,0.07178]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50683,0.04046,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51303,0.05555,0.16048]},{"body_a":"world","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.50683,0.04046,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50941,0.05515,0.16203]},{"body_a":"grasp_target","body_b":"hand","contact_count":381.0,"contact_point_centroid":[0.50856,-0.01744,0.05407],"force_p95":0.09455,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11365,"mean_force":0.08566,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49111,-0.01549,0.01508]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5376.0,"contact_point_centroid":[0.49038,-0.03455,0.01696],"force_p95":0.06367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08304,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49073,-0.01548,0.01469]}],"total_contact_groups":19},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.50683,0.04046,0.01602],"final_tcp_position":[0.50792,0.05497,0.14043],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.59984,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49961,-0.01429,0.13877],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3416.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49876,-0.01558,0.023],"tcp_start":[0.49961,-0.01429,0.13877],"tcp_to_object_dist_end":0.00589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50287,-0.01528,0.02506],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31291,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.16275,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11688.0,"raw_peak_contact_force":0.17775,"tcp_end":[0.4907,-0.01548,0.01466],"tcp_start":[0.49876,-0.01558,0.023],"tcp_to_object_dist_end":0.01602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50877,-0.0156,0.11109],"object_pos_start":[0.50287,-0.01528,0.02506],"object_to_goal_dist_end":0.25712,"object_to_goal_dist_start":0.31291,"object_z_max":0.111,"peak_contact_force":0.12358,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21042.0,"raw_peak_contact_force":0.98469,"subtask_id":"lift_object","tcp_end":[0.48655,-0.01541,0.11346],"tcp_start":[0.4907,-0.01548,0.01466],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50886,-0.0156,0.11111],"object_pos_start":[0.50877,-0.0156,0.11109],"object_to_goal_dist_end":0.25708,"object_to_goal_dist_start":0.25712,"object_z_max":0.11257,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":342.0,"raw_peak_contact_force":0.19432,"subtask_id":"reach_goal","tcp_end":[0.48501,-0.01543,0.11616],"tcp_start":[0.48661,-0.01541,0.11353],"tcp_to_object_dist_end":0.02438,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,0.04046,0.01602],"object_pos_start":[0.50716,-0.01568,0.11291],"object_to_goal_dist_end":0.28616,"object_to_goal_dist_start":0.25671,"object_z_max":0.11349,"peak_contact_force":273006.59984,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13270.0,"raw_peak_contact_force":1.33916,"subtask_id":"reach_goal","tcp_end":[0.51711,0.05593,0.15692],"tcp_start":[0.48501,-0.01543,0.11616],"tcp_to_object_dist_end":0.14212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50683,0.04046,0.01602],"object_pos_start":[0.50683,0.04046,0.01602],"object_to_goal_dist_end":0.28616,"object_to_goal_dist_start":0.28616,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51143,0.05536,0.18133],"tcp_start":[0.51711,0.05593,0.15692],"tcp_to_object_dist_end":0.16605,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":137.0,"n_steps_budget":600.0,"object_pos_end":[0.50683,0.04046,0.01602],"object_pos_start":[0.50683,0.04046,0.01602],"object_to_goal_dist_end":0.28616,"object_to_goal_dist_start":0.28616,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":548.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50792,0.05497,0.14043],"tcp_start":[0.51143,0.05536,0.18133],"tcp_to_object_dist_end":0.12526,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63793,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.14896,"descend_to_grasp.descend_speed":0.04381,"descend_to_place.place_speed":0.07005,"lift.lift_height":0.12766,"transport_to_goal.arc_height":0.05145,"transport_to_goal.transport_speed":0.13647},"optimized_scores":{"best_composite_score":0.13023,"best_fitness_score":0.61023,"best_task_score":0.26411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3686.0,"contact_point_centroid":[0.51853,0.06602,-0.00228],"force_p95":0.12435,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92149,"mean_force":0.13502,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5545,0.10344,0.17112]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.50929,0.03701,-0.00121],"force_p95":0.49212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66463,"mean_force":0.09056,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4974,0.03802,0.03012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10368.0,"contact_point_centroid":[0.49796,0.01901,0.08122],"force_p95":0.1088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32895,"mean_force":0.07055,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49484,0.03782,0.07941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10806.0,"contact_point_centroid":[0.49801,0.05666,0.07964],"force_p95":0.10591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32697,"mean_force":0.06875,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49487,0.03783,0.07802]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1621.0,"contact_point_centroid":[0.50335,0.06146,0.16857],"force_p95":0.16899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27324,"mean_force":0.11462,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49815,0.04328,0.17153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1554.0,"contact_point_centroid":[0.50288,0.02422,0.16572],"force_p95":0.1811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25145,"mean_force":0.11513,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49741,0.04243,0.16827]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03939,-0.00214],"force_p95":0.16407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24456,"mean_force":0.13364,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50019,0.03826,0.02954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51082,0.06496,0.196],"force_p95":0.15629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16065,"mean_force":0.10766,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50513,0.05173,0.20322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4055.0,"contact_point_centroid":[0.4997,0.01896,0.03104],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14859,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.499,0.03817,0.02825]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50276,0.01778,0.21866]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50592,0.03784,0.07106]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5185,0.06601,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58583,0.13768,0.15429]},{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.5185,0.06601,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58206,0.13672,0.15517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5014.0,"contact_point_centroid":[0.49966,0.05734,0.03006],"force_p95":0.07399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08696,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.499,0.03817,0.02826]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3664.0,"contact_point_centroid":[0.55745,0.10591,0.17206],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01063,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55696,0.1059,0.16983]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58909,0.13849,0.15234],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58871,0.13847,0.15015]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5185,0.06601,0.01602],"final_tcp_position":[0.5804,0.13628,0.13333],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.7705,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50763,0.0363,0.13779],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50699,0.03882,0.03693],"tcp_start":[0.50763,0.0363,0.13779],"tcp_to_object_dist_end":0.01226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.0382,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15516,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10869.0,"raw_peak_contact_force":0.24456,"tcp_end":[0.49897,0.03816,0.02822],"tcp_start":[0.50699,0.03882,0.03693],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.51102,0.03805,0.12944],"object_pos_start":[0.51241,0.0382,0.02553],"object_to_goal_dist_end":0.17863,"object_to_goal_dist_start":0.2135,"object_z_max":0.12933,"peak_contact_force":0.11433,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21316.0,"raw_peak_contact_force":0.66463,"subtask_id":"lift_object","tcp_end":[0.49503,0.03785,0.14389],"tcp_start":[0.49897,0.03816,0.02822],"tcp_to_object_dist_end":0.02155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.51813,0.05196,0.17527],"object_pos_start":[0.51102,0.03805,0.12944],"object_to_goal_dist_end":0.1656,"object_to_goal_dist_start":0.17863,"object_z_max":0.17538,"peak_contact_force":0.00587,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3175.0,"raw_peak_contact_force":0.27324,"subtask_id":"reach_goal","tcp_end":[0.50512,0.05172,0.20317],"tcp_start":[0.50533,0.05108,0.20011],"tcp_to_object_dist_end":0.03079,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5185,0.06601,0.01602],"object_pos_start":[0.51843,0.05466,0.17232],"object_to_goal_dist_end":0.19971,"object_to_goal_dist_start":0.16294,"object_z_max":0.17232,"peak_contact_force":9748.7705,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7354.0,"raw_peak_contact_force":1.92149,"subtask_id":"reach_goal","tcp_end":[0.5902,0.13873,0.15296],"tcp_start":[0.50512,0.05172,0.20317],"tcp_to_object_dist_end":0.17083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5185,0.06601,0.01602],"object_pos_start":[0.5185,0.06601,0.01602],"object_to_goal_dist_end":0.19971,"object_to_goal_dist_start":0.19971,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58413,0.13721,0.17416],"tcp_start":[0.5902,0.13873,0.15296],"tcp_to_object_dist_end":0.18543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.5185,0.06601,0.01602],"object_pos_start":[0.5185,0.06601,0.01602],"object_to_goal_dist_end":0.19971,"object_to_goal_dist_start":0.19971,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":496.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5804,0.13628,0.13333],"tcp_start":[0.58413,0.13721,0.17416],"tcp_to_object_dist_end":0.1501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```