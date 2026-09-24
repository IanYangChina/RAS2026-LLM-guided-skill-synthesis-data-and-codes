## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0229 | 0.32 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 0 | 0.2685 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.023) — your mutation base

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
- id: transport_arc
  type: approach
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
  subtask_id: transport_arc
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.023
- **task_score** (E): 0.317
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1427 |
| descend_1 | 1.00 | 1.00 | 0.1379 |
| grasp_1 | 1.00 | 1.00 | 0.0091 |
| lift_1 | 1.00 | 1.00 | 0.1239 |
| transport_arc | 1.00 | 1.00 | 0.1776 |
| place_descend | 1.00 | 1.00 | 0.0494 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.162) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.162)→(0.511, 0.018, 0.024) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.024) | 0.236→0.237 | 1.00 / 17.667 | 1.308 | 1.739 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.024)→(0.506, 0.018, 0.019) | (0.516, 0.018, 0.024)→(0.516, 0.018, 0.024) | 0.237→0.237 | 1.00 / 42.333 | 1.033 | 1.224 |
| lift_1 | lift | 1.00 / step_budget | (0.506, 0.018, 0.019)→(0.502, 0.018, 0.142) | (0.516, 0.018, 0.024)→(0.517, 0.018, 0.133) | 0.237→0.194 | 1.00 / 27.667 | 0.105 | 1.376 |
| transport_arc | approach | 1.00 / step_budget | (0.502, 0.018, 0.142)→(0.590, 0.160, 0.197) | (0.517, 0.018, 0.133)→(0.555, 0.092, 0.059) | 0.194→0.151 | 1.00 / 15.333 | 3249.670 | 1.017 |
| place_descend | descend | 1.00 / step_budget | (0.590, 0.160, 0.197)→(0.601, 0.176, 0.226) | (0.555, 0.092, 0.059)→(0.557, 0.096, 0.016) | 0.151→0.189 | 1.00 / 8.333 | 3249.737 | 0.669 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.176, 0.226)→(0.596, 0.175, 0.246) | (0.557, 0.096, 0.016)→(0.557, 0.096, 0.016) | 0.189→0.189 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.390
- phase_score: 0.393
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.260
- phase_breakdown.transport_arc_score: 0.242
- phase_breakdown.approach_1_score: 0.019
- phase_breakdown.descend_1_score: 0.697
- grasp_place_fitness: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.673
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.019
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86822,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19411,"descend_1.grasp_z_offset":-0.00156,"grasp_1.grasp_z_offset":0.02222,"lift_1.lift_distance":0.13052,"place_descend.place_z_offset":0.04277,"release_1.release_time":1.49542,"release_1.release_z_offset":0.04002,"transport_arc.arc_height":0.18535,"transport_arc.transport_speed":0.4813,"transport_arc.transport_z_offset":0.06558},"optimized_scores":{"best_composite_score":0.0227,"best_fitness_score":0.6727,"best_task_score":0.38963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2714.0,"contact_point_centroid":[0.52865,0.09817,-0.0024],"force_p95":0.19297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61284,"mean_force":0.14693,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56008,0.11408,0.18818]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.5273,0.02862,-0.00119],"force_p95":0.55492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76633,"mean_force":0.10359,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51505,0.02947,0.02495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11255.0,"contact_point_centroid":[0.51524,0.0105,0.07848],"force_p95":0.11003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33172,"mean_force":0.06885,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51241,0.0293,0.07718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11343.0,"contact_point_centroid":[0.51558,0.04813,0.07597],"force_p95":0.10745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32912,"mean_force":0.06893,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51244,0.02931,0.07457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1783.0,"contact_point_centroid":[0.51894,0.02052,0.14883],"force_p95":0.17801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28114,"mean_force":0.10797,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51561,0.03868,0.15262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2077.0,"contact_point_centroid":[0.51945,0.05783,0.15005],"force_p95":0.17027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26601,"mean_force":0.1065,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51623,0.03989,0.15403]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03046,-0.00211],"force_p95":0.15563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24198,"mean_force":0.13161,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51795,0.02967,0.02452]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.13649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51048,0.01274,0.26406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4059.0,"contact_point_centroid":[0.51752,0.0104,0.02593],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13826,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51672,0.02959,0.02316]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52295,0.02814,0.12977]},{"body_a":"world","body_b":"grasp_target","contact_count":376.0,"contact_point_centroid":[0.52933,0.09921,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59144,0.16793,0.16475]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52933,0.09921,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58952,0.17117,0.1537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4980.0,"contact_point_centroid":[0.51747,0.04874,0.02497],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09163,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51673,0.02959,0.02317]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2821.0,"contact_point_centroid":[0.56104,0.11502,0.19084],"force_p95":0.01112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01581,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56063,0.115,0.1885]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.5929,0.17216,0.15188],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01033,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59232,0.17214,0.14969]},{"body_a":"left_finger","body_b":"right_finger","contact_count":406.0,"contact_point_centroid":[0.59185,0.16797,0.16692],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01034,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59145,0.16795,0.16469]}],"total_contact_groups":16},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.52933,0.09921,0.01602],"final_tcp_position":[0.59406,0.17245,0.15304],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.96635,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52313,0.02627,0.22889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52527,0.03016,0.03276],"tcp_start":[0.52313,0.02627,0.22889],"tcp_to_object_dist_end":0.00856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53036,0.02951,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18462,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14792,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.24198,"subtask_id":"grasp_1","tcp_end":[0.5167,0.02959,0.02313],"tcp_start":[0.52527,0.03016,0.03276],"tcp_to_object_dist_end":0.01389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.53099,0.02943,0.12958],"object_pos_start":[0.53036,0.02951,0.02563],"object_to_goal_dist_end":0.16638,"object_to_goal_dist_start":0.18462,"object_z_max":0.12949,"peak_contact_force":0.1231,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22745.0,"raw_peak_contact_force":0.76633,"tcp_end":[0.51265,0.02933,0.14141],"tcp_start":[0.5167,0.02959,0.02313],"tcp_to_object_dist_end":0.02182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52933,0.09921,0.01602],"object_pos_start":[0.53099,0.02943,0.12958],"object_to_goal_dist_end":0.14138,"object_to_goal_dist_start":0.16638,"object_z_max":0.1419,"peak_contact_force":9748.78483,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9395.0,"raw_peak_contact_force":1.61284,"tcp_end":[0.58993,0.16412,0.17656],"tcp_start":[0.51265,0.02933,0.14141],"tcp_to_object_dist_end":0.18346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.52933,0.09921,0.01602],"object_pos_start":[0.52933,0.09921,0.01602],"object_to_goal_dist_end":0.14138,"object_to_goal_dist_start":0.14138,"object_z_max":0.01602,"peak_contact_force":9748.96635,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":782.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59406,0.17245,0.15304],"tcp_start":[0.58993,0.16412,0.17656],"tcp_to_object_dist_end":0.16831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52933,0.09921,0.01602],"object_pos_start":[0.52933,0.09921,0.01602],"object_to_goal_dist_end":0.14138,"object_to_goal_dist_start":0.14138,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58786,0.1706,0.17346],"tcp_start":[0.59406,0.17245,0.15304],"tcp_to_object_dist_end":0.18251,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00794,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11102,"descend_1.grasp_z_offset":0.01383,"grasp_1.grasp_z_offset":0.00715,"lift_1.lift_distance":0.14485,"place_descend.place_z_offset":0.06815,"release_1.release_time":1.55518,"release_1.release_z_offset":0.01676,"transport_arc.arc_height":0.26072,"transport_arc.transport_speed":0.6222,"transport_arc.transport_z_offset":0.00015},"optimized_scores":{"best_composite_score":-0.11013,"best_fitness_score":0.53987,"best_task_score":0.13877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2937.0,"contact_point_centroid":[0.51418,0.01832,-0.00238],"force_p95":0.12471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29012,"mean_force":0.13752,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53323,0.08358,0.25124]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.5007,-0.01504,-0.00112],"force_p95":0.34428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48175,"mean_force":0.06969,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4894,-0.01531,0.04133]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11525.0,"contact_point_centroid":[0.49,0.00358,0.09932],"force_p95":0.10848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31651,"mean_force":0.07076,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48686,-0.01526,0.09737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12072.0,"contact_point_centroid":[0.49008,-0.03405,0.09802],"force_p95":0.1045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28953,"mean_force":0.06822,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48688,-0.01526,0.09641]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1551.0,"contact_point_centroid":[0.4944,0.0107,0.18223],"force_p95":0.16506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25598,"mean_force":0.10524,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48856,-0.00764,0.18478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1605.0,"contact_point_centroid":[0.49425,-0.02606,0.18183],"force_p95":0.16318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25162,"mean_force":0.10275,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48848,-0.00781,0.18448]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01556,-0.00203],"force_p95":0.13352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16191,"mean_force":0.12568,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01534,0.04089]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49893,-0.00692,0.22506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49132,0.00388,0.04242],"force_p95":0.07642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12426,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01533,0.03965]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49809,-0.01478,0.09878]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51421,0.01833,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57638,0.17262,0.27991]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51421,0.01833,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58203,0.18483,0.30744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.49139,-0.0344,0.0415],"force_p95":0.0687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08935,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49087,-0.01533,0.03966]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2908.0,"contact_point_centroid":[0.53613,0.08874,0.25579],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01578,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5358,0.08874,0.25358]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4264.0,"contact_point_centroid":[0.57685,0.17262,0.2821],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57637,0.17261,0.27987]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.58391,0.1855,0.30615],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58344,0.18548,0.30363]}],"total_contact_groups":16},"final_pose_error":0.0104,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51421,0.01833,0.01602],"final_tcp_position":[0.58421,0.18573,0.30637],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.29012,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49979,-0.0142,0.14993],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49889,-0.01543,0.04834],"tcp_start":[0.49979,-0.0142,0.14993],"tcp_to_object_dist_end":0.02286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01524,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13141,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.16191,"subtask_id":"grasp_1","tcp_end":[0.49084,-0.01533,0.03962],"tcp_start":[0.49889,-0.01543,0.04834],"tcp_to_object_dist_end":0.01885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":814.0,"n_steps_budget":900.0,"object_pos_end":[0.49955,-0.0153,0.14901],"object_pos_start":[0.50372,-0.01524,0.02586],"object_to_goal_dist_end":0.24199,"object_to_goal_dist_start":0.31209,"object_z_max":0.1489,"peak_contact_force":0.11414,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23727.0,"raw_peak_contact_force":0.48175,"tcp_end":[0.48715,-0.01526,0.17246],"tcp_start":[0.49084,-0.01533,0.03962],"tcp_to_object_dist_end":0.02652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51421,0.01833,0.01602],"object_pos_start":[0.49955,-0.0153,0.14901],"object_to_goal_dist_end":0.29624,"object_to_goal_dist_start":0.24199,"object_z_max":0.17441,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9001.0,"raw_peak_contact_force":1.29012,"tcp_end":[0.56974,0.15764,0.25475],"tcp_start":[0.48715,-0.01526,0.17246],"tcp_to_object_dist_end":0.28193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51421,0.01833,0.01602],"object_pos_start":[0.51421,0.01833,0.01602],"object_to_goal_dist_end":0.29624,"object_to_goal_dist_start":0.29624,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58421,0.18573,0.30637],"tcp_start":[0.56974,0.15764,0.25475],"tcp_to_object_dist_end":0.34238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51421,0.01833,0.01602],"object_pos_start":[0.51421,0.01833,0.01602],"object_to_goal_dist_end":0.29624,"object_to_goal_dist_start":0.29624,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58132,0.18447,0.32712],"tcp_start":[0.58421,0.18573,0.30637],"tcp_to_object_dist_end":0.35901,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0146,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07,"descend_1.grasp_z_offset":-0.04283,"grasp_1.grasp_z_offset":0.009,"lift_1.lift_distance":0.1325,"place_descend.place_z_offset":0.08602,"release_1.release_time":0.82424,"release_1.release_z_offset":0.00082,"transport_arc.arc_height":0.28056,"transport_arc.transport_speed":0.59606,"transport_arc.transport_z_offset":0.01675},"optimized_scores":{"best_composite_score":0.01872,"best_fitness_score":0.66872,"best_task_score":0.42308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":810.0,"contact_point_centroid":[0.5076,0.08105,-0.00327],"force_p95":3.86496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.97225,"mean_force":2.46079,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50764,0.03881,-0.00184]},{"body_a":"world","body_b":"left_finger","contact_count":799.0,"contact_point_centroid":[0.50759,-0.00348,-0.00325],"force_p95":3.85364,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.88715,"mean_force":2.44533,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50765,0.03881,-0.00191]},{"body_a":"world","body_b":"left_finger","contact_count":9000.0,"contact_point_centroid":[0.51031,-0.00281,-0.00468],"force_p95":2.87753,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.2668,"mean_force":1.90854,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51048,0.03899,-0.00703]},{"body_a":"world","body_b":"right_finger","contact_count":9000.0,"contact_point_centroid":[0.5103,0.08078,-0.00474],"force_p95":2.90249,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.22623,"mean_force":1.93147,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51048,0.03899,-0.00703]},{"body_a":"world","body_b":"right_finger","contact_count":1116.0,"contact_point_centroid":[0.51037,0.07975,-0.00286],"force_p95":2.1459,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.87957,"mean_force":0.8316,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51027,0.03891,-0.00055]},{"body_a":"world","body_b":"left_finger","contact_count":1094.0,"contact_point_centroid":[0.51039,-0.00194,-0.00286],"force_p95":2.18995,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.86125,"mean_force":0.82056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51029,0.03891,-0.00062]},{"body_a":"world","body_b":"grasp_target","contact_count":2218.0,"contact_point_centroid":[0.62649,0.17024,-0.00243],"force_p95":0.15805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76292,"mean_force":0.14194,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6193,0.16716,0.20155]},{"body_a":"world","body_b":"grasp_target","contact_count":651.0,"contact_point_centroid":[0.51155,0.03955,-0.00289],"force_p95":0.26403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73722,"mean_force":0.16665,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50872,0.0388,0.00632]},{"body_a":"grasp_target","body_b":"hand","contact_count":93.0,"contact_point_centroid":[0.52303,0.03919,0.04787],"force_p95":0.68432,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72586,"mean_force":0.47657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50706,0.03867,0.00431]},{"body_a":"grasp_target","body_b":"hand","contact_count":450.0,"contact_point_centroid":[0.51676,0.03986,0.04142],"force_p95":0.61315,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61832,"mean_force":0.59872,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51048,0.03899,-0.00703]},{"body_a":"grasp_target","body_b":"hand","contact_count":747.0,"contact_point_centroid":[0.51463,0.05566,0.09324],"force_p95":0.35586,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59982,"mean_force":0.09982,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50693,0.03867,0.05305]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.51245,0.03973,-0.0023],"force_p95":0.28111,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3727,"mean_force":0.15099,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50599,0.03775,0.04825]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51163,0.0398,-0.00434],"force_p95":0.32647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33426,"mean_force":0.27227,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51048,0.03899,-0.00703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3711.0,"contact_point_centroid":[0.61302,0.14101,0.16393],"force_p95":0.15977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30624,"mean_force":0.09502,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61125,0.15987,0.16673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12577.0,"contact_point_centroid":[0.50654,0.05777,0.06534],"force_p95":0.07216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22316,"mean_force":0.05013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50646,0.03863,0.06349]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5232.0,"contact_point_centroid":[0.61224,0.17827,0.16503],"force_p95":0.10518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21665,"mean_force":0.06809,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61142,0.16005,0.1676]}],"total_contact_groups":24},"final_pose_error":0.01274,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62647,0.17023,0.01602],"final_tcp_position":[0.62355,0.17084,0.21907],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":4.97225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50762,0.03672,0.10807],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.51385,0.03986,0.02109],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21422,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":3.67966,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3214.0,"raw_peak_contact_force":4.97225,"subtask_id":"descend_1","tcp_end":[0.50885,0.03896,-0.00773],"tcp_start":[0.50762,0.03672,0.10807],"tcp_to_object_dist_end":0.02927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51296,0.03984,0.02135],"object_pos_start":[0.51385,0.03986,0.02109],"object_to_goal_dist_end":0.21456,"object_to_goal_dist_start":0.21422,"object_z_max":0.02135,"peak_contact_force":2.81995,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20250.0,"raw_peak_contact_force":3.2668,"subtask_id":"grasp_1","tcp_end":[0.51103,0.03901,-0.00675],"tcp_start":[0.50885,0.03896,-0.00773],"tcp_to_object_dist_end":0.02818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":747.0,"n_steps_budget":840.0,"object_pos_end":[0.52091,0.03858,0.12091],"object_pos_start":[0.51296,0.03984,0.02135],"object_to_goal_dist_end":0.17291,"object_to_goal_dist_start":0.21456,"object_z_max":0.1208,"peak_contact_force":0.0792,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28128.0,"raw_peak_contact_force":2.87957,"tcp_end":[0.50682,0.03867,0.11363],"tcp_start":[0.51103,0.03901,-0.00675],"tcp_to_object_dist_end":0.01585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62266,0.15782,0.14468],"object_pos_start":[0.52091,0.03858,0.12091],"object_to_goal_dist_end":0.0155,"object_to_goal_dist_start":0.17291,"object_z_max":0.15698,"peak_contact_force":0.10352,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32670.0,"raw_peak_contact_force":0.14873,"tcp_end":[0.61131,0.15775,0.15925],"tcp_start":[0.50682,0.03867,0.11363],"tcp_to_object_dist_end":0.01847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62647,0.17023,0.01602],"object_pos_start":[0.62266,0.15782,0.14468],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.0155,"object_z_max":0.15716,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13232.0,"raw_peak_contact_force":1.76292,"tcp_end":[0.62355,0.17084,0.21907],"tcp_start":[0.61131,0.15775,0.15925],"tcp_to_object_dist_end":0.20307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62647,0.17023,0.01602],"object_pos_start":[0.62647,0.17023,0.01602],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61884,0.16928,0.23871],"tcp_start":[0.62355,0.17084,0.21907],"tcp_to_object_dist_end":0.22282,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```