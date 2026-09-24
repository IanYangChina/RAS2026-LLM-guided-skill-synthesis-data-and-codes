## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1121 | 0.38 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.1672 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0796 | 0.39 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1519 | 0.35 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0222 | 0.51 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.112) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: approach_1
- id: descend_1
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
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.04
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_1
- id: lift_1
  type: lift
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
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: scale
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
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.001
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: transport_arc
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.001
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    release_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (scale)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.001
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.001
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.112
- **task_score** (E): 0.381
- **fitness_score**: 0.418  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0742 |
| descend_1 | 1.00 | 1.00 | 0.1961 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.0219 |
| retract_1 | 1.00 | 1.00 | 0.0426 |
| transport_approach | 0.67 | 1.00 | 0.2115 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.015, 0.234) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.015, 0.234)→(0.511, 0.018, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.038)→(0.502, 0.017, 0.029) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.143 | 0.209 |
| lift_1 | lift | 1.00 / step_budget | (0.509, 0.017, 0.043)→(0.515, 0.017, 0.064) | (0.515, 0.018, 0.026)→(0.521, 0.017, 0.037) | 0.237→0.228 | 1.00 / 43.000 | 0.070 | 0.439 |
| retract_1 | retract | 1.00 / step_budget | (0.515, 0.017, 0.064)→(0.511, 0.017, 0.106) | (0.526, 0.017, 0.055)→(0.519, 0.017, 0.093) | 0.218→0.205 | 1.00 / 42.667 | 0.069 | 0.094 |
| transport_approach | approach | 0.67 / step_budget | (0.511, 0.017, 0.106)→(0.590, 0.157, 0.238) | (0.519, 0.017, 0.093)→(0.586, 0.142, 0.016) | 0.205→0.158 | 1.00 / 6.667 | 3249.080 | 1.816 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.532
- phase_score: 0.335
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.transport_arc_score: 0.191
- phase_breakdown.approach_1_score: 0.009
- phase_breakdown.descend_1_score: 0.793
- grasp_place_fitness: 0.493

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.493
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.532
- **Median Q (composite search score)**: -0.093
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44218,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23406,"descend_1.grasp_z_offset":0.00523,"lift_1.lift_distance":0.18258,"place_descend.place_z_offset":-0.00968,"release_1.release_time":1.53321,"retract_1.retract_height":0.05371,"transport_approach.transport_speed":0.20185},"optimized_scores":{"best_composite_score":-0.03674,"best_fitness_score":0.49326,"best_task_score":0.53176},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":239.0,"contact_point_centroid":[0.59897,0.15734,-0.00601],"force_p95":1.21269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63758,"mean_force":0.3076,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.58556,0.15306,0.18423]},{"body_a":"world","body_b":"grasp_target","contact_count":549.0,"contact_point_centroid":[0.53402,0.02853,-0.00111],"force_p95":0.23323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42599,"mean_force":0.06853,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51726,0.02937,0.03255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10171.0,"contact_point_centroid":[0.5497,0.05796,0.13572],"force_p95":0.14216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27652,"mean_force":0.07876,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54671,0.07677,0.1355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15084.0,"contact_point_centroid":[0.52369,0.04824,0.04871],"force_p95":0.07786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22825,"mean_force":0.05294,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52313,0.02918,0.04676]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03052,-0.00211],"force_p95":0.15431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22643,"mean_force":0.13112,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51809,0.02966,0.03138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11987.0,"contact_point_centroid":[0.55118,0.09748,0.13656],"force_p95":0.12313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22366,"mean_force":0.06772,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54771,0.07888,0.13676]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14471.0,"contact_point_centroid":[0.52408,0.01007,0.04991],"force_p95":0.08051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21287,"mean_force":0.05399,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52346,0.02916,0.04763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.51761,0.01039,0.03279],"force_p95":0.07987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14123,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51688,0.02959,0.03001]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51031,0.01247,0.28126]},{"body_a":"world","body_b":"grasp_target","contact_count":2712.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5227,0.02764,0.15079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10059.0,"contact_point_centroid":[0.52636,0.048,0.08823],"force_p95":0.06855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09189,"mean_force":0.04777,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5262,0.02879,0.0872]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10461.0,"contact_point_centroid":[0.52631,0.00962,0.08839],"force_p95":0.0677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08746,"mean_force":0.04579,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5262,0.02879,0.08707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.51757,0.04873,0.03182],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08662,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51688,0.02959,0.03002]}],"total_contact_groups":13},"final_pose_error":0.03321,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59928,0.15778,0.0157],"final_tcp_position":[0.58765,0.15716,0.18684],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.63758,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52232,0.02527,0.26441],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2712.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52533,0.03014,0.03964],"tcp_start":[0.52232,0.02527,0.26441],"tcp_to_object_dist_end":0.01458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.0296,0.02564],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18454,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14752,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10847.0,"raw_peak_contact_force":0.22643,"subtask_id":"grasp_1","tcp_end":[0.51685,0.02958,0.02998],"tcp_start":[0.52533,0.03014,0.03964],"tcp_to_object_dist_end":0.01423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":784.0,"n_steps_budget":600.0,"object_pos_end":[0.53615,0.02939,0.03727],"object_pos_start":[0.5304,0.0296,0.02564],"object_to_goal_dist_end":0.17761,"object_to_goal_dist_start":0.18454,"object_z_max":0.05471,"peak_contact_force":0.06948,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30104.0,"raw_peak_contact_force":0.42599,"tcp_end":[0.53036,0.02907,0.06623],"tcp_start":[0.52421,0.02927,0.04507],"tcp_to_object_dist_end":0.02954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":479.0,"n_steps_budget":600.0,"object_pos_end":[0.5334,0.02872,0.09506],"object_pos_start":[0.53994,0.02911,0.05474],"object_to_goal_dist_end":0.16513,"object_to_goal_dist_start":0.17024,"object_z_max":0.095,"peak_contact_force":0.06872,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":20520.0,"raw_peak_contact_force":0.09189,"tcp_end":[0.52594,0.02878,0.1096],"tcp_start":[0.53036,0.02907,0.06623],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59928,0.15778,0.0157],"object_pos_start":[0.5334,0.02872,0.09506],"object_to_goal_dist_end":0.09473,"object_to_goal_dist_start":0.16513,"object_z_max":0.14855,"peak_contact_force":0.09576,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22397.0,"raw_peak_contact_force":1.63758,"subtask_id":"transport_arc","tcp_end":[0.58765,0.15716,0.18684],"tcp_start":[0.52594,0.02878,0.1096],"tcp_to_object_dist_end":0.17154,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6259,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18284,"descend_1.grasp_z_offset":-0.00356,"lift_1.lift_distance":0.12111,"place_descend.place_z_offset":-0.00867,"release_1.release_time":0.88446,"retract_1.retract_height":0.0521,"transport_approach.transport_speed":0.38314},"optimized_scores":{"best_composite_score":-0.20654,"best_fitness_score":0.32346,"best_task_score":0.18958},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1566.0,"contact_point_centroid":[0.53945,0.10946,-0.00265],"force_p95":0.31382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04796,"mean_force":0.15568,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.55717,0.1236,0.2634]},{"body_a":"world","body_b":"grasp_target","contact_count":431.0,"contact_point_centroid":[0.50685,-0.01517,-0.00106],"force_p95":0.32163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49735,"mean_force":0.08284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49104,-0.01527,0.02471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8073.0,"contact_point_centroid":[0.51475,0.04042,0.13982],"force_p95":0.1318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31382,"mean_force":0.06717,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51241,0.02181,0.13997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6392.0,"contact_point_centroid":[0.51324,-0.00064,0.13586],"force_p95":0.14919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26318,"mean_force":0.07745,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51099,0.01833,0.13587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12435.0,"contact_point_centroid":[0.49729,0.00399,0.04153],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21913,"mean_force":0.05311,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49713,-0.01515,0.03937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13109.0,"contact_point_centroid":[0.49712,-0.03424,0.04097],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.216,"mean_force":0.05096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49702,-0.01515,0.03909]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.0155,-0.00203],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1653,"mean_force":0.12551,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49196,-0.01535,0.02365]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49933,-0.00618,0.26155]},{"body_a":"world","body_b":"grasp_target","contact_count":2360.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49832,-0.01421,0.12519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.49127,0.00386,0.02519],"force_p95":0.07596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10946,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01534,0.02243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9494.0,"contact_point_centroid":[0.50029,0.00418,0.07992],"force_p95":0.07156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0925,"mean_force":0.05,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50011,-0.01503,0.07818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10340.0,"contact_point_centroid":[0.50008,-0.03417,0.07968],"force_p95":0.06905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0904,"mean_force":0.04643,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50011,-0.01503,0.07817]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.49133,-0.03442,0.02427],"force_p95":0.06821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08972,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01534,0.02243]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1491.0,"contact_point_centroid":[0.55937,0.12754,0.27044],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01057,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.55893,0.12754,0.26819]}],"total_contact_groups":14},"final_pose_error":0.05282,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53914,0.10955,0.01602],"final_tcp_position":[0.57288,0.15874,0.30606],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.04796,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":972.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50015,-0.01305,0.22168],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.499,-0.01543,0.03108],"tcp_start":[0.50015,-0.01305,0.22168],"tcp_to_object_dist_end":0.00699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.0152,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12981,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10799.0,"raw_peak_contact_force":0.1653,"subtask_id":"grasp_1","tcp_end":[0.49075,-0.01534,0.0224],"tcp_start":[0.499,-0.01543,0.03108],"tcp_to_object_dist_end":0.01338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":648.0,"n_steps_budget":600.0,"object_pos_end":[0.51009,-0.01514,0.03704],"object_pos_start":[0.50367,-0.0152,0.02588],"object_to_goal_dist_end":0.30248,"object_to_goal_dist_start":0.31206,"object_z_max":0.05408,"peak_contact_force":0.07149,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25975.0,"raw_peak_contact_force":0.49735,"tcp_end":[0.5042,-0.01508,0.05715],"tcp_start":[0.49735,-0.01515,0.03631],"tcp_to_object_dist_end":0.02096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.51072,-0.01494,0.09228],"object_pos_start":[0.51633,-0.015,0.05411],"object_to_goal_dist_end":0.26655,"object_to_goal_dist_start":0.28915,"object_z_max":0.09222,"peak_contact_force":0.0702,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":19834.0,"raw_peak_contact_force":0.0925,"tcp_end":[0.49983,-0.01502,0.09961],"tcp_start":[0.5042,-0.01508,0.05715],"tcp_to_object_dist_end":0.01313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53914,0.10955,0.01602],"object_pos_start":[0.51072,-0.01494,0.09228],"object_to_goal_dist_end":0.24944,"object_to_goal_dist_start":0.26655,"object_z_max":0.17834,"peak_contact_force":0.12263,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17522.0,"raw_peak_contact_force":2.04796,"subtask_id":"transport_arc","tcp_end":[0.57288,0.15874,0.30606],"tcp_start":[0.49983,-0.01502,0.09961],"tcp_to_object_dist_end":0.29611,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51079,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17857,"descend_1.grasp_z_offset":0.00767,"lift_1.lift_distance":0.19688,"place_descend.place_z_offset":0.01025,"release_1.release_time":1.58795,"retract_1.retract_height":0.05093,"transport_approach.transport_speed":0.30593},"optimized_scores":{"best_composite_score":-0.09304,"best_fitness_score":0.43696,"best_task_score":0.42199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":301.0,"contact_point_centroid":[0.61892,0.15919,-0.00563],"force_p95":0.93593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76374,"mean_force":0.27163,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.60652,0.15147,0.21655]},{"body_a":"world","body_b":"grasp_target","contact_count":472.0,"contact_point_centroid":[0.51517,0.03706,-0.00113],"force_p95":0.25388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39463,"mean_force":0.07093,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49986,0.03804,0.03579]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11955.0,"contact_point_centroid":[0.54691,0.09974,0.1482],"force_p95":0.10807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31572,"mean_force":0.06655,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54339,0.08109,0.14787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10355.0,"contact_point_centroid":[0.54447,0.05997,0.14674],"force_p95":0.13139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27493,"mean_force":0.07559,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.54142,0.07882,0.14573]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03946,-0.00213],"force_p95":0.16078,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2347,"mean_force":0.13271,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50061,0.03835,0.03462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13320.0,"contact_point_centroid":[0.50555,0.05688,0.05148],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2273,"mean_force":0.05219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5053,0.03779,0.04952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12831.0,"contact_point_centroid":[0.50586,0.01866,0.05258],"force_p95":0.08053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20831,"mean_force":0.05289,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50553,0.03777,0.05024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4070.0,"contact_point_centroid":[0.49997,0.01905,0.03614],"force_p95":0.08091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15284,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49943,0.03825,0.03334]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50289,0.01648,0.25753]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50639,0.03646,0.1279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9849.0,"contact_point_centroid":[0.50779,0.05644,0.0896],"force_p95":0.06856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09623,"mean_force":0.04775,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50781,0.03723,0.08848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10318.0,"contact_point_centroid":[0.50773,0.01806,0.08993],"force_p95":0.06732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09135,"mean_force":0.04537,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50781,0.03723,0.08848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4998.0,"contact_point_centroid":[0.49996,0.05741,0.03516],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08462,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49944,0.03825,0.03335]},{"body_a":"left_finger","body_b":"right_finger","contact_count":94.0,"contact_point_centroid":[0.60958,0.15444,0.22202],"force_p95":0.01487,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01572,"mean_force":0.01247,"phase_index":5.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.60915,0.15441,0.21942]}],"total_contact_groups":14},"final_pose_error":0.03367,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.619,0.15906,0.0166],"final_tcp_position":[0.61073,0.15598,0.22101],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9747.02099,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50768,0.03419,0.2151],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50762,0.03892,0.04236],"tcp_start":[0.50768,0.03419,0.2151],"tcp_to_object_dist_end":0.01707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03837,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21337,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15304,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10868.0,"raw_peak_contact_force":0.2347,"subtask_id":"grasp_1","tcp_end":[0.4994,0.03825,0.03331],"tcp_start":[0.50762,0.03892,0.04236],"tcp_to_object_dist_end":0.01516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":678.0,"n_steps_budget":600.0,"object_pos_end":[0.51753,0.03792,0.03683],"object_pos_start":[0.51243,0.03837,0.02555],"object_to_goal_dist_end":0.20477,"object_to_goal_dist_start":0.21337,"object_z_max":0.05464,"peak_contact_force":0.06974,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26623.0,"raw_peak_contact_force":0.39463,"tcp_end":[0.51186,0.03755,0.06818],"tcp_start":[0.50622,0.03797,0.04726],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":469.0,"n_steps_budget":600.0,"object_pos_end":[0.5143,0.03717,0.09308],"object_pos_start":[0.5208,0.03761,0.05468],"object_to_goal_dist_end":0.18397,"object_to_goal_dist_start":0.19433,"object_z_max":0.09302,"peak_contact_force":0.06748,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":20167.0,"raw_peak_contact_force":0.09623,"tcp_end":[0.50753,0.03721,0.10938],"tcp_start":[0.51186,0.03755,0.06818],"tcp_to_object_dist_end":0.01765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.619,0.15906,0.0166],"object_pos_start":[0.5143,0.03717,0.09308],"object_to_goal_dist_end":0.12942,"object_to_goal_dist_start":0.18397,"object_z_max":0.17323,"peak_contact_force":9747.02099,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22705.0,"raw_peak_contact_force":1.76374,"subtask_id":"transport_arc","tcp_end":[0.61073,0.15598,0.22101],"tcp_start":[0.50753,0.03721,0.10938],"tcp_to_object_dist_end":0.2046,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```