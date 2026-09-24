## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2878 | 0.13 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1875 | 0.14 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0937 | 0.16 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3395 | 0.29 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.4989 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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

## Current Skill (Q=0.288) — your mutation base

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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
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
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: transport_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: transport_arc

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.288
- **task_score** (E): 0.125
- **fitness_score**: 0.528  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1293 |
| descend_1 | 1.00 | 1.00 | 0.1251 |
| grasp_1 | 1.00 | 1.00 | 0.0107 |
| lift_1 | 0.33 | 1.00 | 0.1380 |
| transport_1 | 0.00 | 1.00 | 0.1566 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.179) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 10.837 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.179)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 44.667 | 0.141 | 0.192 |
| lift_1 | lift | 0.33 / step_budget | (0.511, -0.001, 0.045)→(0.507, -0.001, 0.183) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.156) | 0.289→0.233 | 1.00 / 26.000 | 0.097 | 0.446 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.183)→(0.526, 0.039, 0.146) | (0.518, -0.001, 0.156)→(0.531, 0.001, -6.407) | 0.233→6.668 | 1.00 / 8.000 | 91150.246 | 1126.111 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.240
- phase_score: 0.259
- phase_breakdown.transport_arc_score: 0.026
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.172
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.descend_1_score: 0.867
- grasp_place_fitness: 0.586

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.586
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.240
- **Median Q (composite search score)**: 0.294
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.311


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28358,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15778,"lift_1.lift_height":0.23922,"transport_1.transport_arc_height":0.22553},"optimized_scores":{"best_composite_score":0.22392,"best_fitness_score":0.46392,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":23.0,"contact_point_centroid":[0.47428,0.15196,-0.00338],"force_p95":771.90239,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":917.37443,"mean_force":96.36151,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.42427,0.0658,-2e-05]},{"body_a":"world","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.54656,0.06541,-0.00162],"force_p95":753.21335,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":827.0444,"mean_force":270.48657,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.415,0.06793,0.02232]},{"body_a":"world","body_b":"link6","contact_count":850.0,"contact_point_centroid":[0.64426,0.0683,-0.00031],"force_p95":264.08988,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.39984,"mean_force":238.67474,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.40348,0.09469,0.07439]},{"body_a":"world","body_b":"right_finger","contact_count":353.0,"contact_point_centroid":[0.42931,0.08301,-0.00365],"force_p95":27.97478,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.63892,"mean_force":3.25936,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.42563,0.06589,-0.00083]},{"body_a":"world","body_b":"left_finger","contact_count":315.0,"contact_point_centroid":[0.42698,0.04802,-0.00342],"force_p95":25.62874,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.60279,"mean_force":2.63946,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.42542,0.06588,-0.00133]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.46842,0.06592,-0.02283],"force_p95":3.64537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.8247,"mean_force":1.36846,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.44657,0.06672,0.01513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":957.0,"contact_point_centroid":[0.5026,0.07691,0.15566],"force_p95":0.69693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.01705,"mean_force":0.24601,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.496,0.05917,0.15833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.50448,0.03836,0.17699],"force_p95":0.34035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54784,"mean_force":0.17162,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50009,0.05752,0.18034]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.48006,0.04626,-0.00118],"force_p95":0.27995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41811,"mean_force":0.05738,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47131,0.04716,0.0487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16312.0,"contact_point_centroid":[0.47134,0.06585,0.11942],"force_p95":0.09844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30052,"mean_force":0.06279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46896,0.04694,0.11873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15624.0,"contact_point_centroid":[0.47088,0.02802,0.11987],"force_p95":0.10174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29959,"mean_force":0.06445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46894,0.04694,0.11955]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.48273,0.04859,-0.00213],"force_p95":0.15569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21247,"mean_force":0.13197,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47347,0.04738,0.04756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47207,0.0281,0.04827],"force_p95":0.08033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14737,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47277,0.04731,0.04678]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49018,0.02061,0.24802]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47868,0.04517,0.12457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.47291,0.06643,0.04823],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07452,"mean_force":0.04419,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47278,0.04731,0.04678]}],"total_contact_groups":17},"final_pose_error":0.23467,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.46134,-0.03607,-19.25694],"final_tcp_position":[0.41161,0.13188,0.10133],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":917.37443,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48147,0.04281,0.19557],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47833,0.04777,0.0547],"tcp_start":[0.48147,0.04281,0.19557],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04765,0.02558],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29098,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15201,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10755.0,"raw_peak_contact_force":0.21247,"subtask_id":"grasp_1","tcp_end":[0.47275,0.04731,0.04675],"tcp_start":[0.47833,0.04777,0.0547],"tcp_to_object_dist_end":0.02338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47874,0.04738,0.18049],"object_pos_start":[0.48265,0.04765,0.02558],"object_to_goal_dist_end":0.21464,"object_to_goal_dist_start":0.29098,"object_z_max":0.18029,"peak_contact_force":0.09745,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32071.0,"raw_peak_contact_force":0.41811,"tcp_end":[0.46931,0.04698,0.21062],"tcp_start":[0.47275,0.04731,0.04675],"tcp_to_object_dist_end":0.03158,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46134,-0.03607,-19.25694],"object_pos_start":[0.47874,0.04738,0.18049],"object_to_goal_dist_end":19.4896,"object_to_goal_dist_start":0.21464,"object_z_max":0.18119,"peak_contact_force":250.23447,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6584.0,"raw_peak_contact_force":917.37443,"subtask_id":"transport_arc","tcp_end":[0.41161,0.13188,0.10133],"tcp_start":[0.46931,0.04698,0.21062],"tcp_to_object_dist_end":19.35907,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33835,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18964,"lift_1.lift_height":0.28108,"transport_1.transport_arc_height":0.19211},"optimized_scores":{"best_composite_score":0.29386,"best_fitness_score":0.53386,"best_task_score":0.1362},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":98.0,"contact_point_centroid":[0.55064,-0.0783,-0.00202],"force_p95":637.28556,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1016.56293,"mean_force":156.78777,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50109,-0.02402,-0.00092]},{"body_a":"world","body_b":"link7","contact_count":239.0,"contact_point_centroid":[0.60563,-0.01175,-0.00018],"force_p95":296.07725,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.6587,"mean_force":198.78225,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48272,-0.02406,0.01488]},{"body_a":"world","body_b":"link6","contact_count":613.0,"contact_point_centroid":[0.67542,0.03149,-0.00015],"force_p95":224.43357,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.88089,"mean_force":203.94331,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.44301,-0.0242,0.07305]},{"body_a":"world","body_b":"left_finger","contact_count":1382.0,"contact_point_centroid":[0.50644,-0.03956,-0.00526],"force_p95":8.54686,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.11004,"mean_force":3.3214,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50295,-0.0238,-0.00298]},{"body_a":"world","body_b":"right_finger","contact_count":1191.0,"contact_point_centroid":[0.50464,-0.0072,-0.00586],"force_p95":8.81355,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.86252,"mean_force":3.47958,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50434,-0.02362,-0.0047]},{"body_a":"world","body_b":"grasp_target","contact_count":2424.0,"contact_point_centroid":[0.53749,-0.01026,-0.0082],"force_p95":1.05256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.75561,"mean_force":0.53081,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.45756,-0.02406,0.05397]},{"body_a":"grasp_target","body_b":"hand","contact_count":917.0,"contact_point_centroid":[0.54728,-0.01543,0.03148],"force_p95":1.42152,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.57299,"mean_force":0.83852,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.45652,-0.02414,0.05438]},{"body_a":"grasp_target","body_b":"link7","contact_count":761.0,"contact_point_centroid":[0.55193,-0.00032,0.02691],"force_p95":0.54686,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.31144,"mean_force":0.37604,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.44794,-0.0241,0.06493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":714.0,"contact_point_centroid":[0.56812,-0.04235,0.17897],"force_p95":0.43695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64621,"mean_force":0.20324,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5617,-0.0245,0.18085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.56514,-0.00498,0.18148],"force_p95":0.44779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62355,"mean_force":0.21734,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56062,-0.02452,0.18399]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.53462,-0.02041,-0.00114],"force_p95":0.3443,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45856,"mean_force":0.07,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52419,-0.02088,0.04661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15601.0,"contact_point_centroid":[0.52421,-0.00183,0.11584],"force_p95":0.10206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27815,"mean_force":0.06449,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52168,-0.02082,0.11411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17197.0,"contact_point_centroid":[0.52398,-0.03973,0.11447],"force_p95":0.09618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27744,"mean_force":0.05936,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52168,-0.02082,0.11287]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17472,"mean_force":0.12666,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52656,-0.02093,0.04587]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51327,-0.00893,0.26184]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52908,-0.01964,0.13854]}],"total_contact_groups":19},"final_pose_error":0.3107,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52042,0.01286,0.01989],"final_tcp_position":[0.44562,-0.02301,0.12663],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1016.56293,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":32.26436,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52887,-0.01836,0.22453],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53177,-0.02099,0.05426],"tcp_start":[0.52887,-0.01836,0.22453],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.53694,-0.02095,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31657,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13463,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12633.0,"raw_peak_contact_force":0.17472,"subtask_id":"grasp_1","tcp_end":[0.52578,-0.02091,0.04488],"tcp_start":[0.53177,-0.02099,0.05426],"tcp_to_object_dist_end":0.0221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53306,-0.0208,0.17846],"object_pos_start":[0.53694,-0.02095,0.02581],"object_to_goal_dist_end":0.26189,"object_to_goal_dist_start":0.31657,"object_z_max":0.17828,"peak_contact_force":0.10533,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32941.0,"raw_peak_contact_force":0.45856,"tcp_end":[0.52215,-0.02082,0.20599],"tcp_start":[0.52578,-0.02091,0.04488],"tcp_to_object_dist_end":0.0296,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52042,0.01286,0.01989],"object_pos_start":[0.53306,-0.0208,0.17846],"object_to_goal_dist_end":0.29904,"object_to_goal_dist_start":0.26189,"object_z_max":0.17905,"peak_contact_force":191.38136,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11739.0,"raw_peak_contact_force":1016.56293,"subtask_id":"transport_arc","tcp_end":[0.44562,-0.02301,0.12663],"tcp_start":[0.52215,-0.02082,0.20599],"tcp_to_object_dist_end":0.13519,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.0625,"average_mean_iterations":16.35938,"average_solve_count":128.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08114,"lift_1.lift_height":0.10156,"transport_1.transport_arc_height":0.14639},"optimized_scores":{"best_composite_score":0.34574,"best_fitness_score":0.58574,"best_task_score":0.23952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":85.0,"contact_point_centroid":[0.70392,0.04194,-0.00155],"force_p95":922.00607,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1444.39664,"mean_force":300.9506,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.65091,-0.00814,0.00359]},{"body_a":"world","body_b":"link6","contact_count":782.0,"contact_point_centroid":[0.57182,0.13029,-0.00029],"force_p95":411.04895,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":493.59185,"mean_force":294.49239,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.71668,-0.0228,0.17645]},{"body_a":"world","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.7189,0.08512,-0.00061],"force_p95":341.76371,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.0617,"mean_force":221.45403,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.69396,-0.04436,0.07949]},{"body_a":"world","body_b":"right_finger","contact_count":674.0,"contact_point_centroid":[0.63291,0.0266,-0.01659],"force_p95":27.15623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.61283,"mean_force":12.97026,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.64363,0.01563,-0.01716]},{"body_a":"world","body_b":"left_finger","contact_count":726.0,"contact_point_centroid":[0.65524,0.00528,-0.01582],"force_p95":21.72127,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.81798,"mean_force":12.05972,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.64388,0.01405,-0.01555]},{"body_a":"grasp_target","body_b":"hand","contact_count":148.0,"contact_point_centroid":[0.67389,0.05489,0.0373],"force_p95":4.74632,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.86794,"mean_force":1.25688,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.66247,-0.01056,0.02334]},{"body_a":"grasp_target","body_b":"link7","contact_count":337.0,"contact_point_centroid":[0.63601,0.03719,0.04388],"force_p95":1.9171,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.73739,"mean_force":0.7503,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.70796,-0.04032,0.12985]},{"body_a":"world","body_b":"grasp_target","contact_count":3006.0,"contact_point_centroid":[0.62046,0.02791,-0.00428],"force_p95":0.94681,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70834,"mean_force":0.29276,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.70695,-0.0166,0.15475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":678.0,"contact_point_centroid":[0.57661,-0.01597,0.1234],"force_p95":0.4311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.44249,"mean_force":0.21265,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56911,0.00198,0.12281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":673.0,"contact_point_centroid":[0.57967,0.02776,0.11743],"force_p95":0.34768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68453,"mean_force":0.17114,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57895,0.00829,0.11783]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.54307,-0.02834,-0.00116],"force_p95":0.2954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46146,"mean_force":0.07084,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53193,-0.0285,0.04593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11161.0,"contact_point_centroid":[0.53064,-0.00937,0.08847],"force_p95":0.08463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30242,"mean_force":0.05419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52932,-0.02841,0.08593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10937.0,"contact_point_centroid":[0.53082,-0.0475,0.08725],"force_p95":0.08557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29288,"mean_force":0.05544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52936,-0.02841,0.08513]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.54561,-0.02909,-0.00207],"force_p95":0.13964,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18799,"mean_force":0.12805,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53439,-0.02858,0.04519]},{"body_a":"world","body_b":"grasp_target","contact_count":2452.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51798,-0.01342,0.20796]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53779,-0.02786,0.08551]}],"total_contact_groups":19},"final_pose_error":0.18308,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61075,0.02502,0.01602],"final_tcp_position":[0.72108,0.00794,0.20987],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273009.12077,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2452.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53842,-0.02713,0.11775],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53954,-0.02868,0.05372],"tcp_start":[0.53842,-0.02713,0.11775],"tcp_to_object_dist_end":0.02836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02862,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26064,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13629,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11431.0,"raw_peak_contact_force":0.18799,"subtask_id":"grasp_1","tcp_end":[0.53359,-0.02855,0.04417],"tcp_start":[0.53954,-0.02868,0.05372],"tcp_to_object_dist_end":0.02194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.54253,-0.02841,0.1101],"object_pos_start":[0.54552,-0.02862,0.02576],"object_to_goal_dist_end":0.22361,"object_to_goal_dist_start":0.26064,"object_z_max":0.10998,"peak_contact_force":0.08695,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22249.0,"raw_peak_contact_force":0.46146,"tcp_end":[0.5294,-0.0284,0.13316],"tcp_start":[0.53359,-0.02855,0.04417],"tcp_to_object_dist_end":0.02654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61075,0.02502,0.01602],"object_pos_start":[0.54253,-0.02841,0.1101],"object_to_goal_dist_end":0.21437,"object_to_goal_dist_start":0.22361,"object_z_max":0.11014,"peak_contact_force":273009.12077,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10592.0,"raw_peak_contact_force":1444.39664,"subtask_id":"transport_arc","tcp_end":[0.72108,0.00794,0.20987],"tcp_start":[0.5294,-0.0284,0.13316],"tcp_to_object_dist_end":0.2237,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```