## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2182 | 0.35 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1316 | 0.37 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1884 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1989 | 0.30 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1922 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.218) — your mutation base

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

- **Composite score**: 0.218
- **task_score** (E): 0.347
- **fitness_score**: 0.648  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1660 |
| descend_to_grasp | 1.00 | 1.00 | 0.1072 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1057 |
| transport_to_goal | 0.67 | 1.00 | 0.2375 |
| descend_to_place | 1.00 | 1.00 | 0.1102 |
| release | 1.00 | 1.00 | 0.0211 |
| retract | 1.00 | 1.00 | 0.0411 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.510, 0.018, 0.031) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, 0.018, 0.031)→(0.502, 0.017, 0.022) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.025) | 0.236→0.237 | 1.00 / 42.333 | 0.151 | 0.222 |
| lift | lift | 1.00 / step_budget | (0.502, 0.017, 0.022)→(0.498, 0.017, 0.127) | (0.515, 0.018, 0.025)→(0.517, 0.017, 0.118) | 0.237→0.199 | 1.00 / 24.333 | 0.117 | 0.827 |
| transport_to_goal | approach | 0.67 / step_budget | (0.498, 0.017, 0.127)→(0.593, 0.161, 0.287) | (0.517, 0.017, 0.118)→(0.553, 0.124, 0.009) | 0.199→0.182 | 1.00 / 6.667 | 3249.843 | 1.818 |
| descend_to_place | descend | 1.00 / step_budget | (0.593, 0.161, 0.287)→(0.600, 0.176, 0.179) | (0.553, 0.124, 0.009)→(0.553, 0.124, 0.016) | 0.182→0.176 | 1.00 / 8.000 | 3249.663 | 0.255 |
| release | release | 1.00 / step_budget | (0.600, 0.176, 0.179)→(0.595, 0.174, 0.200) | (0.553, 0.124, 0.016)→(0.553, 0.124, 0.016) | 0.176→0.176 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.595, 0.174, 0.200)→(0.591, 0.173, 0.159) | (0.553, 0.124, 0.016)→(0.553, 0.124, 0.016) | 0.176→0.176 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.541
- phase_score: 0.393
- phase_breakdown.reach_object_score: 0.174
- phase_breakdown.reach_goal_score: 0.500
- phase_breakdown.lift_object_score: 0.428
- grasp_place_fitness: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.211
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.396


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19841,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09733,"descend_to_grasp.descend_speed":0.05586,"descend_to_place.place_speed":0.04819,"lift.lift_height":0.12051,"transport_to_goal.transport_speed":0.05001},"optimized_scores":{"best_composite_score":0.31478,"best_fitness_score":0.74478,"best_task_score":0.541},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.6047,0.17964,-0.00828],"force_p95":1.2305,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89575,"mean_force":0.87304,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59242,0.1671,0.2418]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52749,0.02833,-0.00121],"force_p95":0.39781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57365,"mean_force":0.08323,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51452,0.02928,0.0353]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.60506,0.18008,-0.0022],"force_p95":0.12359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5192,"mean_force":0.12288,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5944,0.17338,0.16111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9766.0,"contact_point_centroid":[0.51523,0.01031,0.08287],"force_p95":0.10886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32308,"mean_force":0.07144,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51195,0.02912,0.08099]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10155.0,"contact_point_centroid":[0.51532,0.04791,0.08133],"force_p95":0.10519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31856,"mean_force":0.06966,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51198,0.02912,0.07958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.54746,0.06542,0.17665],"force_p95":0.13505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24689,"mean_force":0.09968,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54199,0.08365,0.17872]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03054,-0.00212],"force_p95":0.1587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22776,"mean_force":0.13216,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51741,0.02948,0.03487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5282.0,"contact_point_centroid":[0.54935,0.10524,0.17887],"force_p95":0.13002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17344,"mean_force":0.0996,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.544,0.08705,0.18123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.51716,0.0102,0.03623],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14912,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51619,0.0294,0.03349]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51093,0.01384,0.21813]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52303,0.02925,0.07482]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60507,0.18007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59147,0.17459,0.12486]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.60507,0.18007,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5874,0.17331,0.12549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.51709,0.04855,0.03528],"force_p95":0.07317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08332,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5162,0.0294,0.0335]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4134.0,"contact_point_centroid":[0.59493,0.17355,0.16079],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01558,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59445,0.17352,0.15853]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.59505,0.17562,0.12329],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01024,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59456,0.17559,0.12096]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60507,0.18007,0.01602],"final_tcp_position":[0.58563,0.17274,0.10358],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.74254,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52429,0.02821,0.13709],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52433,0.02994,0.04277],"tcp_start":[0.52429,0.02821,0.13709],"tcp_to_object_dist_end":0.01787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.02951,0.02558],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18462,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1515,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.22776,"tcp_end":[0.51616,0.0294,0.03346],"tcp_start":[0.52433,0.02994,0.04277],"tcp_to_object_dist_end":0.01629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.52635,0.02931,0.12407],"object_pos_start":[0.53042,0.02951,0.02558],"object_to_goal_dist_end":0.16789,"object_to_goal_dist_start":0.18462,"object_z_max":0.12396,"peak_contact_force":0.10937,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20069.0,"raw_peak_contact_force":0.57365,"subtask_id":"lift_object","tcp_end":[0.51213,0.02914,0.14175],"tcp_start":[0.51616,0.0294,0.03346],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.60533,0.17938,-0.00397],"object_pos_start":[0.52635,0.02931,0.12407],"object_to_goal_dist_end":0.11213,"object_to_goal_dist_start":0.16789,"object_z_max":0.19964,"peak_contact_force":0.55946,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10653.0,"raw_peak_contact_force":1.89575,"tcp_end":[0.59336,0.16864,0.24297],"tcp_start":[0.51213,0.02914,0.14175],"tcp_to_object_dist_end":0.24747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60507,0.18007,0.01602],"object_pos_start":[0.60533,0.17938,-0.00397],"object_to_goal_dist_end":0.09215,"object_to_goal_dist_start":0.11213,"object_z_max":0.0167,"peak_contact_force":9748.74254,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8134.0,"raw_peak_contact_force":0.5192,"subtask_id":"reach_goal","tcp_end":[0.59617,0.17608,0.1239],"tcp_start":[0.59336,0.16864,0.24297],"tcp_to_object_dist_end":0.10832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60507,0.18007,0.01602],"object_pos_start":[0.60507,0.18007,0.01602],"object_to_goal_dist_end":0.09215,"object_to_goal_dist_start":0.09215,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58961,0.17397,0.14457],"tcp_start":[0.59617,0.17608,0.1239],"tcp_to_object_dist_end":0.12962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.60507,0.18007,0.01602],"object_pos_start":[0.60507,0.18007,0.01602],"object_to_goal_dist_end":0.09215,"object_to_goal_dist_start":0.09215,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":492.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58563,0.17274,0.10358],"tcp_start":[0.58961,0.17397,0.14457],"tcp_to_object_dist_end":0.08999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38767,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.14055,"descend_to_grasp.descend_speed":0.07582,"descend_to_place.place_speed":0.08187,"lift.lift_height":0.12027,"transport_to_goal.transport_speed":0.05009},"optimized_scores":{"best_composite_score":0.12843,"best_fitness_score":0.55843,"best_task_score":0.16511},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2392.0,"contact_point_centroid":[0.51529,0.06922,-0.00243],"force_p95":0.13397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97094,"mean_force":0.14201,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54207,0.10124,0.27649]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.50107,-0.01553,-0.00111],"force_p95":0.71028,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.909,"mean_force":0.10958,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48917,-0.01543,0.01944]},{"body_a":"grasp_target","body_b":"hand","contact_count":90.0,"contact_point_centroid":[0.50573,0.00467,0.06127],"force_p95":0.05495,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34464,"mean_force":0.03929,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48798,-0.01541,0.02341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10483.0,"contact_point_centroid":[0.48925,0.00351,0.06899],"force_p95":0.10696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31879,"mean_force":0.06916,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48653,-0.01538,0.06721]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3515.0,"contact_point_centroid":[0.50023,0.03072,0.15609],"force_p95":0.15595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30858,"mean_force":0.10247,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49754,0.01262,0.15931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11074.0,"contact_point_centroid":[0.48898,-0.03419,0.06621],"force_p95":0.1106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28536,"mean_force":0.06609,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48656,-0.01538,0.0651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3296.0,"contact_point_centroid":[0.49901,-0.00775,0.15345],"force_p95":0.16318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25019,"mean_force":0.10295,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49653,0.01051,0.15658]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50377,-0.01549,-0.00205],"force_p95":0.13382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1608,"mean_force":0.12668,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49194,-0.01546,0.01888]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49884,-0.00698,0.21953]},{"body_a":"world","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49762,-0.01497,0.07401]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51517,0.06923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57447,0.16757,0.29025]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51517,0.06923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57883,0.18098,0.26031]},{"body_a":"world","body_b":"grasp_target","contact_count":484.0,"contact_point_centroid":[0.51517,0.06923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57657,0.18014,0.26133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49121,0.00375,0.02041],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09564,"mean_force":0.0516,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01545,0.01764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49127,-0.03453,0.01949],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09198,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01545,0.01765]},{"body_a":"grasp_target","body_b":"hand","contact_count":307.0,"contact_point_centroid":[0.5083,-0.01968,0.05564],"force_p95":0.01943,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.05385,"mean_force":0.01218,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49081,-0.01545,0.01772]}],"total_contact_groups":19},"final_pose_error":0.0097,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51517,0.06923,0.01602],"final_tcp_position":[0.57546,0.17972,0.23944],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.84798,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49963,-0.0143,0.13874],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2992.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49882,-0.01554,0.02605],"tcp_start":[0.49963,-0.0143,0.13874],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50354,-0.01531,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13394,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11103.0,"raw_peak_contact_force":0.1608,"tcp_end":[0.49071,-0.01544,0.01761],"tcp_start":[0.49882,-0.01554,0.02605],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50831,-0.01545,0.11953],"object_pos_start":[0.50354,-0.01531,0.0258],"object_to_goal_dist_end":0.25274,"object_to_goal_dist_start":0.31223,"object_z_max":0.11944,"peak_contact_force":0.11769,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21787.0,"raw_peak_contact_force":0.909,"subtask_id":"lift_object","tcp_end":[0.48666,-0.01537,0.12624],"tcp_start":[0.49071,-0.01544,0.01761],"tcp_to_object_dist_end":0.02267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51517,0.06923,0.01602],"object_pos_start":[0.50831,-0.01545,0.11953],"object_to_goal_dist_end":0.27017,"object_to_goal_dist_start":0.25274,"object_z_max":0.16834,"peak_contact_force":9748.84798,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11529.0,"raw_peak_contact_force":1.97094,"tcp_end":[0.5662,0.14832,0.33899],"tcp_start":[0.48666,-0.01537,0.12624],"tcp_to_object_dist_end":0.33641,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51517,0.06923,0.01602],"object_pos_start":[0.51517,0.06923,0.01602],"object_to_goal_dist_end":0.27017,"object_to_goal_dist_start":0.27017,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8285.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58174,0.18204,0.25921],"tcp_start":[0.5662,0.14832,0.33899],"tcp_to_object_dist_end":0.27622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51517,0.06923,0.01602],"object_pos_start":[0.51517,0.06923,0.01602],"object_to_goal_dist_end":0.27017,"object_to_goal_dist_start":0.27017,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57781,0.18056,0.28007],"tcp_start":[0.58174,0.18204,0.25921],"tcp_to_object_dist_end":0.29333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":121.0,"n_steps_budget":600.0,"object_pos_end":[0.51517,0.06923,0.01602],"object_pos_start":[0.51517,0.06923,0.01602],"object_to_goal_dist_end":0.27017,"object_to_goal_dist_start":0.27017,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":484.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57546,0.17972,0.23944],"tcp_start":[0.57781,0.18056,0.28007],"tcp_to_object_dist_end":0.25644,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97546,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12724,"descend_to_grasp.descend_speed":0.09944,"descend_to_place.place_speed":0.08519,"lift.lift_height":0.11169,"transport_to_goal.transport_speed":0.15555},"optimized_scores":{"best_composite_score":0.21141,"best_fitness_score":0.64141,"best_task_score":0.33402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1796.0,"contact_point_centroid":[0.53902,0.12245,-0.00245],"force_p95":0.26402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58665,"mean_force":0.15131,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58321,0.12961,0.23094]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.50928,0.03847,-0.00136],"force_p95":0.77202,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99764,"mean_force":0.12927,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4975,0.03837,0.01679]},{"body_a":"grasp_target","body_b":"hand","contact_count":253.0,"contact_point_centroid":[0.51323,0.03714,0.07143],"force_p95":0.1027,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46025,"mean_force":0.0779,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4953,0.03819,0.03311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.5151,0.03848,0.13362],"force_p95":0.19179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2966,"mean_force":0.1103,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51106,0.05678,0.1357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2574.0,"contact_point_centroid":[0.51716,0.07759,0.13643],"force_p95":0.19796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28669,"mean_force":0.1111,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51355,0.05943,0.13899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10584.0,"contact_point_centroid":[0.49738,0.05702,0.0597],"force_p95":0.10491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28461,"mean_force":0.06334,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49502,0.03818,0.05819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9769.0,"contact_point_centroid":[0.49707,0.01924,0.06202],"force_p95":0.1104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28276,"mean_force":0.06711,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49498,0.03817,0.06021]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51236,0.0391,-0.00233],"force_p95":0.16922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27686,"mean_force":0.14757,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50046,0.03864,0.01593]},{"body_a":"grasp_target","body_b":"hand","contact_count":381.0,"contact_point_centroid":[0.51707,0.04971,0.054],"force_p95":0.11161,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22132,"mean_force":0.08976,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49963,0.03857,0.01506]},{"body_a":"world","body_b":"grasp_target","contact_count":2020.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50275,0.01777,0.21869]},{"body_a":"world","body_b":"grasp_target","contact_count":3208.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.0379,0.06941]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.53858,0.12259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62017,0.16791,0.21439]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53858,0.12259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61836,0.16939,0.15504]},{"body_a":"world","body_b":"grasp_target","contact_count":476.0,"contact_point_centroid":[0.53858,0.12259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61467,0.16826,0.15544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5486.0,"contact_point_centroid":[0.49891,0.05777,0.01699],"force_p95":0.06573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08835,"mean_force":0.04197,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03854,0.01465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4361.0,"contact_point_centroid":[0.49871,0.01931,0.01767],"force_p95":0.07724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07772,"mean_force":0.04739,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03854,0.01465]}],"total_contact_groups":19},"final_pose_error":0.00969,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53858,0.12259,0.01602],"final_tcp_position":[0.61297,0.16773,0.13331],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.58665,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2020.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50764,0.03629,0.13784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3208.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50738,0.03921,0.0233],"tcp_start":[0.50764,0.03629,0.13784],"tcp_to_object_dist_end":0.00582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51166,0.03844,0.025],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21405,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16632,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12028.0,"raw_peak_contact_force":0.27686,"tcp_end":[0.49922,0.03853,0.01462],"tcp_start":[0.50738,0.03921,0.0233],"tcp_to_object_dist_end":0.0162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.51731,0.03803,0.11172],"object_pos_start":[0.51166,0.03844,0.025],"object_to_goal_dist_end":0.17706,"object_to_goal_dist_start":0.21405,"object_z_max":0.11163,"peak_contact_force":0.12303,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20768.0,"raw_peak_contact_force":0.99764,"subtask_id":"lift_object","tcp_end":[0.49505,0.03819,0.11445],"tcp_start":[0.49922,0.03853,0.01462],"tcp_to_object_dist_end":0.02243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":763.0,"n_steps_budget":1000.0,"object_pos_end":[0.53858,0.12259,0.01602],"object_pos_start":[0.51731,0.03803,0.11172],"object_to_goal_dist_end":0.16448,"object_to_goal_dist_start":0.17706,"object_z_max":0.13909,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8331.0,"raw_peak_contact_force":1.58665,"tcp_end":[0.61938,0.16567,0.27837],"tcp_start":[0.49505,0.03819,0.11445],"tcp_to_object_dist_end":0.27787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.53858,0.12259,0.01602],"object_pos_start":[0.53858,0.12259,0.01602],"object_to_goal_dist_end":0.16448,"object_to_goal_dist_start":0.16448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4017.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62289,0.17078,0.15512],"tcp_start":[0.61938,0.16567,0.27837],"tcp_to_object_dist_end":0.16965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53858,0.12259,0.01602],"object_pos_start":[0.53858,0.12259,0.01602],"object_to_goal_dist_end":0.16448,"object_to_goal_dist_start":0.16448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61667,0.16884,0.17442],"tcp_start":[0.62289,0.17078,0.15512],"tcp_to_object_dist_end":0.18256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":119.0,"n_steps_budget":600.0,"object_pos_end":[0.53858,0.12259,0.01602],"object_pos_start":[0.53858,0.12259,0.01602],"object_to_goal_dist_end":0.16448,"object_to_goal_dist_start":0.16448,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":476.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61297,0.16773,0.13331],"tcp_start":[0.61667,0.16884,0.17442],"tcp_to_object_dist_end":0.14605,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```