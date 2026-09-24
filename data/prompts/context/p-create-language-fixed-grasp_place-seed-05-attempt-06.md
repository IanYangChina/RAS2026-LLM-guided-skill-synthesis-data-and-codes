## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0018 | 0.22 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0976 | 0.24 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0911 | 0.38 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1279 | 0.31 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.0792 | 0.39 | ✅ accepted |

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

## Current Skill (Q=0.002) — your mutation base

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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
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
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: scale
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - -0.15
      - 0.05
      default: -0.05
      binds_to:
      - path: target.offset.z
        mode: add
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
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.15
      - 0.05
      default: -0.03
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (scale)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (add)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.002
- **task_score** (E): 0.223
- **fitness_score**: 0.502  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0970 |
| descend_1 | 1.00 | 1.00 | 0.1722 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.1309 |
| transport_arc | 0.00 | 1.00 | 0.0954 |
| place_descend | 0.67 | 1.00 | 0.1417 |
| release_1 | 1.00 | 1.00 | 0.0221 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.015, 0.209) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 10.912 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.015, 0.209)→(0.511, 0.018, 0.037) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.037)→(0.502, 0.017, 0.028) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.025) | 0.236→0.237 | 1.00 / 42.000 | 0.155 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.502, 0.017, 0.028)→(0.495, 0.017, 0.159) | (0.515, 0.018, 0.025)→(0.501, 0.027, 0.091) | 0.237→0.205 | 1.00 / 13.667 | 0.135 | 0.895 |
| transport_arc | approach | 0.00 / step_budget | (0.495, 0.017, 0.159)→(0.519, 0.060, 0.234) | (0.501, 0.027, 0.091)→(0.507, 0.029, 0.016) | 0.205→0.237 | 1.00 / 8.667 | 0.123 | 1.077 |
| place_descend | descend | 0.67 / step_budget | (0.519, 0.060, 0.234)→(0.582, 0.153, 0.167) | (0.507, 0.029, 0.016)→(0.507, 0.029, 0.016) | 0.237→0.237 | 1.00 / 8.333 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.582, 0.153, 0.167)→(0.577, 0.152, 0.188) | (0.507, 0.029, 0.016)→(0.507, 0.029, 0.016) | 0.237→0.237 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.239
- phase_score: 0.324
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.428
- phase_breakdown.transport_arc_score: 0.042
- phase_breakdown.approach_1_score: 0.012
- phase_breakdown.descend_1_score: 0.864
- grasp_place_fitness: 0.594

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.594
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.314
- **Median Q (composite search score)**: 0.032
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90196,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15157,"descend_1.grasp_z_offset":-0.01179,"lift_1.lift_distance":0.1839,"place_descend.place_z_offset":-0.00401,"release_1.release_time":1.44359,"transport_arc.arc_height":0.24112,"transport_arc.transport_z_offset":0.1177},"optimized_scores":{"best_composite_score":-0.12061,"best_fitness_score":0.37939,"best_task_score":0.31364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.51718,0.05329,-0.00265],"force_p95":0.60418,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60388,"mean_force":0.16701,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50953,0.02914,0.15022]},{"body_a":"grasp_target","body_b":"hand","contact_count":535.0,"contact_point_centroid":[0.52475,0.03145,0.09354],"force_p95":0.14039,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48134,"mean_force":0.09509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51207,0.0293,0.0547]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53026,0.03014,-0.00249],"force_p95":0.18524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29065,"mean_force":0.15801,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5177,0.02969,0.01427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12867.0,"contact_point_centroid":[0.51515,0.01056,0.08548],"force_p95":0.14122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28875,"mean_force":0.08031,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51217,0.02931,0.08442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14308.0,"contact_point_centroid":[0.51521,0.04792,0.08349],"force_p95":0.14277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28458,"mean_force":0.07589,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51219,0.02931,0.08289]},{"body_a":"grasp_target","body_b":"hand","contact_count":396.0,"contact_point_centroid":[0.53446,0.037,0.05309],"force_p95":0.15212,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23145,"mean_force":0.13022,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.517,0.02964,0.01351]},{"body_a":"world","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51072,0.01331,0.24378]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52314,0.02868,0.10445]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.51578,0.0585,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53118,0.07151,0.20717]},{"body_a":"world","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.51578,0.0585,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57688,0.14964,0.13249]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51578,0.0585,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58395,0.16967,0.09552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3998.0,"contact_point_centroid":[0.51711,0.01037,0.0157],"force_p95":0.07877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08852,"mean_force":0.05166,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51645,0.02961,0.01291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.51625,0.04876,0.01555],"force_p95":0.06621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08764,"mean_force":0.04177,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51646,0.02961,0.01292]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1087.0,"contact_point_centroid":[0.5092,0.0291,0.17206],"force_p95":0.01255,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01088,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50874,0.02909,0.16988]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5998.0,"contact_point_centroid":[0.53177,0.07165,0.20954],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01041,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53127,0.07164,0.20724]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4382.0,"contact_point_centroid":[0.57747,0.1497,0.13476],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01043,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57691,0.14967,0.13246]}],"total_contact_groups":17},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.51578,0.0585,0.01602],"final_tcp_position":[0.59373,0.17266,0.10237],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.60388,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1540.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52384,0.02734,0.18815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52512,0.03018,0.02248],"tcp_start":[0.52384,0.02734,0.18815],"tcp_to_object_dist_end":0.00647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52934,0.02956,0.0246],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18544,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.18185,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11676.0,"raw_peak_contact_force":0.29065,"subtask_id":"grasp_1","tcp_end":[0.51643,0.02959,0.01288],"tcp_start":[0.52512,0.03018,0.02248],"tcp_to_object_dist_end":0.01744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51578,0.0585,0.01602],"object_pos_start":[0.52934,0.02956,0.0246],"object_to_goal_dist_end":0.17393,"object_to_goal_dist_start":0.18544,"object_z_max":0.15109,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30145.0,"raw_peak_contact_force":1.60388,"tcp_end":[0.5087,0.02909,0.16983],"tcp_start":[0.51643,0.02959,0.01288],"tcp_to_object_dist_end":0.15675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51578,0.0585,0.01602],"object_pos_start":[0.51578,0.0585,0.01602],"object_to_goal_dist_end":0.17393,"object_to_goal_dist_start":0.17393,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11598.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.5448,0.09689,0.219],"tcp_start":[0.5087,0.02909,0.16983],"tcp_to_object_dist_end":0.2086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.51578,0.0585,0.01602],"object_pos_start":[0.51578,0.0585,0.01602],"object_to_goal_dist_end":0.17393,"object_to_goal_dist_start":0.17393,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8482.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58897,0.17122,0.0943],"tcp_start":[0.5448,0.09689,0.219],"tcp_to_object_dist_end":0.15554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51578,0.0585,0.01602],"object_pos_start":[0.51578,0.0585,0.01602],"object_to_goal_dist_end":0.17393,"object_to_goal_dist_start":0.17393,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1033.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58193,0.16903,0.11531],"tcp_start":[0.58897,0.17122,0.0943],"tcp_to_object_dist_end":0.16264,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89362,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15085,"descend_1.grasp_z_offset":0.00999,"lift_1.lift_distance":0.13957,"place_descend.place_z_offset":0.0202,"release_1.release_time":0.7527,"transport_arc.arc_height":0.26677,"transport_arc.transport_z_offset":0.10232},"optimized_scores":{"best_composite_score":0.0323,"best_fitness_score":0.5323,"best_task_score":0.11584},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.49372,-0.01753,-0.0022],"force_p95":0.12393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58821,"mean_force":0.13255,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48477,-0.00443,0.23832]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.50063,-0.01502,-0.00112],"force_p95":0.37275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53008,"mean_force":0.07497,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48946,-0.01532,0.03753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14776.0,"contact_point_centroid":[0.4898,0.00346,0.10909],"force_p95":0.12445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32188,"mean_force":0.07766,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48615,-0.01526,0.10809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15591.0,"contact_point_centroid":[0.48986,-0.0339,0.10764],"force_p95":0.12264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29542,"mean_force":0.07415,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48617,-0.01526,0.10697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":741.0,"contact_point_centroid":[0.4861,0.00219,0.1584],"force_p95":0.19569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29512,"mean_force":0.1236,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48064,-0.01587,0.16315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.48579,-0.03373,0.15944],"force_p95":0.13025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29443,"mean_force":0.10247,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48041,-0.01597,0.16422]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01555,-0.00203],"force_p95":0.13314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16075,"mean_force":0.12559,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.01536,0.03709]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49914,-0.00661,0.24527]},{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49823,-0.01456,0.11623]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.49373,-0.01747,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53031,0.08905,0.25729]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49373,-0.01747,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54786,0.12957,0.25464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49137,0.00386,0.03862],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12217,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01534,0.03586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49144,-0.03442,0.03771],"force_p95":0.06858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09044,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01534,0.03586]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4849.0,"contact_point_centroid":[0.48545,-0.00379,0.24346],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48507,-0.00378,0.24113]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5967.0,"contact_point_centroid":[0.53083,0.0892,0.25948],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53038,0.08919,0.25728]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.55045,0.13014,0.25193],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54984,0.13013,0.24999]}],"total_contact_groups":16},"final_pose_error":0.06587,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49373,-0.01747,0.01602],"final_tcp_position":[0.55388,0.13114,0.25955],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":32.49014,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":32.49014,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50001,-0.01374,0.18961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.499,-0.01544,0.04454],"tcp_start":[0.50001,-0.01374,0.18961],"tcp_to_object_dist_end":0.01914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01523,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13097,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.16075,"subtask_id":"grasp_1","tcp_end":[0.49091,-0.01534,0.03582],"tcp_start":[0.499,-0.01544,0.04454],"tcp_to_object_dist_end":0.01622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":784.0,"n_steps_budget":870.0,"object_pos_end":[0.4886,-0.01524,0.13214],"object_pos_start":[0.50371,-0.01523,0.02587],"object_to_goal_dist_end":0.25337,"object_to_goal_dist_start":0.31208,"object_z_max":0.14316,"peak_contact_force":0.12467,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30497.0,"raw_peak_contact_force":0.53008,"tcp_end":[0.48323,-0.0152,0.15815],"tcp_start":[0.49091,-0.01534,0.03582],"tcp_to_object_dist_end":0.02655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49373,-0.01747,0.01602],"object_pos_start":[0.4886,-0.01524,0.13214],"object_to_goal_dist_end":0.32333,"object_to_goal_dist_start":0.25337,"object_z_max":0.1423,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11314.0,"raw_peak_contact_force":1.58821,"subtask_id":"transport_arc","tcp_end":[0.48788,0.00515,0.26282],"tcp_start":[0.48323,-0.0152,0.15815],"tcp_to_object_dist_end":0.24791,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49373,-0.01747,0.01602],"object_pos_start":[0.49373,-0.01747,0.01602],"object_to_goal_dist_end":0.32333,"object_to_goal_dist_start":0.32333,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11567.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5509,0.13039,0.25246],"tcp_start":[0.48788,0.00515,0.26282],"tcp_to_object_dist_end":0.28466,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49373,-0.01747,0.01602],"object_pos_start":[0.49373,-0.01747,0.01602],"object_to_goal_dist_end":0.32333,"object_to_goal_dist_start":0.32333,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54677,0.12925,0.27487],"tcp_start":[0.5509,0.13039,0.25246],"tcp_to_object_dist_end":0.30223,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88732,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2162,"descend_1.grasp_z_offset":0.01011,"lift_1.lift_distance":0.13004,"place_descend.place_z_offset":0.01942,"release_1.release_time":1.50752,"transport_arc.arc_height":0.26036,"transport_arc.transport_z_offset":0.1108},"optimized_scores":{"best_composite_score":0.09381,"best_fitness_score":0.59381,"best_task_score":0.23928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4438.0,"contact_point_centroid":[0.51043,0.04746,-0.00221],"force_p95":0.12403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52019,"mean_force":0.13356,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51699,0.06669,0.209]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50961,0.03735,-0.00121],"force_p95":0.39771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55031,"mean_force":0.07824,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4979,0.03807,0.03741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15312.0,"contact_point_centroid":[0.49815,0.01909,0.10522],"force_p95":0.11441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32384,"mean_force":0.07345,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49454,0.03782,0.10385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15819.0,"contact_point_centroid":[0.49794,0.05659,0.10328],"force_p95":0.11005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31713,"mean_force":0.07178,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49456,0.03782,0.10196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1501.0,"contact_point_centroid":[0.49684,0.02257,0.15321],"force_p95":0.18011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27454,"mean_force":0.11726,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4918,0.04049,0.1573]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1625.0,"contact_point_centroid":[0.49712,0.05851,0.15372],"force_p95":0.14303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2384,"mean_force":0.10926,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.492,0.04073,0.15807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03947,-0.00213],"force_p95":0.16039,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22774,"mean_force":0.13266,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50067,0.03831,0.03684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4072.0,"contact_point_centroid":[0.50001,0.01901,0.03837],"force_p95":0.08092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15261,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4995,0.03821,0.03556]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50278,0.01548,0.27495]},{"body_a":"world","body_b":"grasp_target","contact_count":2520.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50633,0.03553,0.14628]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.51045,0.04739,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5829,0.13387,0.17645]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51045,0.04739,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60281,0.15747,0.15479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.50001,0.05737,0.03738],"force_p95":0.07367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.081,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49951,0.03821,0.03557]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4502.0,"contact_point_centroid":[0.51853,0.06783,0.21304],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51808,0.06781,0.21078]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5950.0,"contact_point_centroid":[0.58337,0.13381,0.17871],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5828,0.13378,0.1765]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.60633,0.15838,0.15356],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60574,0.15834,0.15119]}],"total_contact_groups":16},"final_pose_error":0.02069,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51045,0.04739,0.01602],"final_tcp_position":[0.61127,0.15992,0.16253],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.52019,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50733,0.03235,0.25027],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50766,0.03887,0.04457],"tcp_start":[0.50733,0.03235,0.25027],"tcp_to_object_dist_end":0.0192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03837,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21336,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10877.0,"raw_peak_contact_force":0.22774,"subtask_id":"grasp_1","tcp_end":[0.49947,0.03821,0.03553],"tcp_start":[0.50766,0.03887,0.04457],"tcp_to_object_dist_end":0.01636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.49791,0.03761,0.12373],"object_pos_start":[0.51244,0.03837,0.02555],"object_to_goal_dist_end":0.18832,"object_to_goal_dist_start":0.21336,"object_z_max":0.13455,"peak_contact_force":0.15871,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31276.0,"raw_peak_contact_force":0.55031,"tcp_end":[0.49159,0.03759,0.14824],"tcp_start":[0.49947,0.03821,0.03553],"tcp_to_object_dist_end":0.02532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51045,0.04739,0.01602],"object_pos_start":[0.49791,0.03761,0.12373],"object_to_goal_dist_end":0.21452,"object_to_goal_dist_start":0.18832,"object_z_max":0.13968,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12066.0,"raw_peak_contact_force":1.52019,"subtask_id":"transport_arc","tcp_end":[0.52566,0.07706,0.21962],"tcp_start":[0.49159,0.03759,0.14824],"tcp_to_object_dist_end":0.20631,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51045,0.04739,0.01602],"object_pos_start":[0.51045,0.04739,0.01602],"object_to_goal_dist_end":0.21452,"object_to_goal_dist_start":0.21452,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11550.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60715,0.15874,0.15405],"tcp_start":[0.52566,0.07706,0.21962],"tcp_to_object_dist_end":0.202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51045,0.04739,0.01602],"object_pos_start":[0.51045,0.04739,0.01602],"object_to_goal_dist_end":0.21452,"object_to_goal_dist_start":0.21452,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60111,0.15694,0.17435],"tcp_start":[0.60715,0.15874,0.15405],"tcp_to_object_dist_end":0.21281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```