## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1994 | 0.17 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2883 | 0.25 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2878 | 0.13 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1875 | 0.14 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0937 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.199) — your mutation base

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

- **Composite score**: 0.199
- **task_score** (E): 0.168
- **fitness_score**: 0.549  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0952 |
| descend_1 | 1.00 | 1.00 | 0.1653 |
| grasp_1 | 1.00 | 1.00 | 0.0108 |
| lift_1 | 0.67 | 1.00 | 0.1164 |
| transport_1 | 0.00 | 1.00 | 0.1052 |
| release_1 | 1.00 | 1.00 | 0.0237 |
| retract_1 | 0.67 | 1.00 | 0.1227 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.220) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 11.155 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.220)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 46.333 | 0.141 | 0.189 |
| lift_1 | lift | 0.67 / step_budget | (0.511, -0.001, 0.045)→(0.507, -0.001, 0.162) | (0.522, -0.001, 0.026)→(0.519, -0.001, 0.136) | 0.289→0.241 | 1.00 / 25.667 | 0.104 | 0.444 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.162)→(0.540, 0.073, 0.227) | (0.519, -0.001, 0.136)→(0.540, 0.029, 0.016) | 0.241→0.271 | 1.00 / 8.333 | 3249.786 | 1.739 |
| release_1 | release | 1.00 / step_budget | (0.540, 0.073, 0.227)→(0.535, 0.073, 0.250) | (0.540, 0.029, 0.016)→(0.540, 0.029, 0.016) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 0.67 / step_budget | (0.535, 0.073, 0.250)→(0.533, 0.072, 0.372) | (0.540, 0.029, 0.016)→(0.540, 0.029, 0.016) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.210
- phase_score: 0.268
- phase_breakdown.transport_arc_score: 0.045
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.007
- phase_breakdown.release_1_score: 0.038
- phase_breakdown.descend_1_score: 0.873
- grasp_place_fitness: 0.571

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.571
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.210
- **Median Q (composite search score)**: 0.198
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60417,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17053,"lift_1.lift_height":0.10697,"retract_1.retract_height":0.08827,"transport_1.transport_arc_height":0.29922},"optimized_scores":{"best_composite_score":0.19843,"best_fitness_score":0.54843,"best_task_score":0.16912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1159.0,"contact_point_centroid":[0.51116,0.08718,-0.00289],"force_p95":0.4357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71668,"mean_force":0.16442,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5001,0.10202,0.20924]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48014,0.04632,-0.00119],"force_p95":0.26293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41648,"mean_force":0.05722,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47132,0.04716,0.04876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7391.0,"contact_point_centroid":[0.48196,0.08271,0.16837],"force_p95":0.11957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3103,"mean_force":0.07909,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47648,0.06411,0.16891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11504.0,"contact_point_centroid":[0.46983,0.06599,0.09304],"force_p95":0.08889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29986,"mean_force":0.05542,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46891,0.04693,0.09188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11025.0,"contact_point_centroid":[0.46922,0.02786,0.09346],"force_p95":0.08836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29854,"mean_force":0.05671,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46888,0.04693,0.09273]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.48273,0.04859,-0.00213],"force_p95":0.15564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21239,"mean_force":0.13195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4735,0.04738,0.04762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7381.0,"contact_point_centroid":[0.48227,0.04636,0.16923],"force_p95":0.11543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19742,"mean_force":0.07847,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47697,0.06493,0.17001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.4721,0.02811,0.04831],"force_p95":0.08031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14734,"mean_force":0.05202,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47281,0.04731,0.04684]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49038,0.02031,0.25415]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47885,0.04493,0.13062]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51124,0.08717,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50383,0.11266,0.22019]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.51124,0.08717,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50013,0.11181,0.27775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4983.0,"contact_point_centroid":[0.47295,0.06643,0.04827],"force_p95":0.07322,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07449,"mean_force":0.0442,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47281,0.04731,0.04684]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1000.0,"contact_point_centroid":[0.50182,0.10422,0.21317],"force_p95":0.01256,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.0107,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50148,0.10421,0.21086]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.50652,0.11324,0.21696],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00988,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50608,0.11322,0.21475]}],"total_contact_groups":15},"final_pose_error":0.01245,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51124,0.08717,0.01602],"final_tcp_position":[0.50027,0.11182,0.31702],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.71668,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48174,0.04234,0.20782],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47837,0.04777,0.05478],"tcp_start":[0.48174,0.04234,0.20782],"tcp_to_object_dist_end":0.0291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04765,0.02558],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29097,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15198,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10754.0,"raw_peak_contact_force":0.21239,"subtask_id":"grasp_1","tcp_end":[0.47278,0.04731,0.04681],"tcp_start":[0.47837,0.04777,0.05478],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.47985,0.04739,0.11591],"object_pos_start":[0.48265,0.04765,0.02558],"object_to_goal_dist_end":0.23762,"object_to_goal_dist_start":0.29097,"object_z_max":0.1158,"peak_contact_force":0.10352,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22668.0,"raw_peak_contact_force":0.41648,"tcp_end":[0.46895,0.04694,0.14235],"tcp_start":[0.47278,0.04731,0.04681],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51124,0.08717,0.01602],"object_pos_start":[0.47985,0.04739,0.11591],"object_to_goal_dist_end":0.26657,"object_to_goal_dist_start":0.23762,"object_z_max":0.16195,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16931.0,"raw_peak_contact_force":1.71668,"subtask_id":"transport_arc","tcp_end":[0.50724,0.11337,0.21677],"tcp_start":[0.46895,0.04694,0.14235],"tcp_to_object_dist_end":0.20249,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51124,0.08717,0.01602],"object_pos_start":[0.51124,0.08717,0.01602],"object_to_goal_dist_end":0.26657,"object_to_goal_dist_start":0.26657,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.50255,0.11235,0.24098],"tcp_start":[0.50724,0.11337,0.21677],"tcp_to_object_dist_end":0.22653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51124,0.08717,0.01602],"object_pos_start":[0.51124,0.08717,0.01602],"object_to_goal_dist_end":0.26657,"object_to_goal_dist_start":0.26657,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50027,0.11182,0.31702],"tcp_start":[0.50255,0.11235,0.24098],"tcp_to_object_dist_end":0.3022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65868,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13954,"lift_1.lift_height":0.29079,"retract_1.retract_height":0.14304,"transport_1.transport_arc_height":0.29257},"optimized_scores":{"best_composite_score":0.17865,"best_fitness_score":0.52865,"best_task_score":0.12572},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3072.0,"contact_point_centroid":[0.54214,-0.00777,-0.00235],"force_p95":0.12522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86317,"mean_force":0.1378,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53877,0.035,0.24158]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53449,-0.02054,-0.00113],"force_p95":0.33703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45432,"mean_force":0.06958,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52408,-0.02088,0.04655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15591.0,"contact_point_centroid":[0.52414,-0.00182,0.11544],"force_p95":0.10285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28084,"mean_force":0.06456,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52158,-0.02082,0.11363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17375.0,"contact_point_centroid":[0.52385,-0.03973,0.11458],"force_p95":0.09527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27923,"mean_force":0.05894,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52158,-0.02082,0.11285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1149.0,"contact_point_centroid":[0.52875,0.00427,0.20876],"force_p95":0.18865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27201,"mean_force":0.10923,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52231,-0.01434,0.20946]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.52857,-0.03167,0.20881],"force_p95":0.13479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21133,"mean_force":0.08045,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52241,-0.01368,0.20991]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17462,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52646,-0.02093,0.04579]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.53702,-0.02132,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51368,-0.00938,0.23771]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52946,-0.02005,0.11461]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54213,-0.00777,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54983,0.07375,0.25867]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.54213,-0.00777,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54691,0.07324,0.3421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5090.0,"contact_point_centroid":[0.52502,-0.0016,0.04715],"force_p95":0.06651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08846,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52571,-0.02091,0.04483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5863.0,"contact_point_centroid":[0.5248,-0.04014,0.04706],"force_p95":0.06057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07742,"mean_force":0.03792,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52571,-0.02091,0.04483]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3068.0,"contact_point_centroid":[0.53999,0.03727,0.24523],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01523,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5396,0.03727,0.2429]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55205,0.07414,0.25648],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01009,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55186,0.07414,0.25392]}],"total_contact_groups":15},"final_pose_error":0.01347,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54213,-0.00777,0.01602],"final_tcp_position":[0.54761,0.0733,0.40861],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9749.11143,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":33.21877,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52987,-0.01918,0.17616],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53165,-0.02099,0.05416],"tcp_start":[0.52987,-0.01918,0.17616],"tcp_to_object_dist_end":0.02865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.53694,-0.02095,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31657,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13437,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12633.0,"raw_peak_contact_force":0.17462,"subtask_id":"grasp_1","tcp_end":[0.52568,-0.02091,0.0448],"tcp_start":[0.53165,-0.02099,0.05416],"tcp_to_object_dist_end":0.02207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53301,-0.02088,0.17834],"object_pos_start":[0.53694,-0.02095,0.02581],"object_to_goal_dist_end":0.262,"object_to_goal_dist_start":0.31657,"object_z_max":0.17815,"peak_contact_force":0.10463,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33110.0,"raw_peak_contact_force":0.45432,"tcp_end":[0.52205,-0.02083,0.20582],"tcp_start":[0.52568,-0.02091,0.0448],"tcp_to_object_dist_end":0.02958,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54213,-0.00777,0.01602],"object_pos_start":[0.53301,-0.02088,0.17834],"object_to_goal_dist_end":0.31105,"object_to_goal_dist_start":0.262,"object_z_max":0.18421,"peak_contact_force":9749.11143,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8913.0,"raw_peak_contact_force":1.86317,"subtask_id":"transport_arc","tcp_end":[0.55292,0.07409,0.25626],"tcp_start":[0.52205,-0.02083,0.20582],"tcp_to_object_dist_end":0.25404,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54213,-0.00777,0.01602],"object_pos_start":[0.54213,-0.00777,0.01602],"object_to_goal_dist_end":0.31105,"object_to_goal_dist_start":0.31105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54872,0.07355,0.27899],"tcp_start":[0.55292,0.07409,0.25626],"tcp_to_object_dist_end":0.27533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.54213,-0.00777,0.01602],"object_pos_start":[0.54213,-0.00777,0.01602],"object_to_goal_dist_end":0.31105,"object_to_goal_dist_start":0.31105,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54761,0.0733,0.40861],"tcp_start":[0.54872,0.07355,0.27899],"tcp_to_object_dist_end":0.40091,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58084,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24871,"lift_1.lift_height":0.105,"retract_1.retract_height":0.23444,"transport_1.transport_arc_height":0.18675},"optimized_scores":{"best_composite_score":0.22114,"best_fitness_score":0.57114,"best_task_score":0.21029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1009.0,"contact_point_centroid":[0.56693,0.00846,-0.00295],"force_p95":0.50382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63613,"mean_force":0.16874,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55384,0.02281,0.20102]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.54318,-0.02867,-0.00116],"force_p95":0.30105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45978,"mean_force":0.07181,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53265,-0.02864,0.04636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12699.0,"contact_point_centroid":[0.53088,-0.04758,0.08916],"force_p95":0.08086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28136,"mean_force":0.0502,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53005,-0.02855,0.08692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11017.0,"contact_point_centroid":[0.53124,-0.00938,0.08865],"force_p95":0.09661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27881,"mean_force":0.0568,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53005,-0.02855,0.08647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7238.0,"contact_point_centroid":[0.54048,0.00554,0.16367],"force_p95":0.13286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26736,"mean_force":0.08497,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53462,-0.01314,0.16302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8283.0,"contact_point_centroid":[0.54049,-0.03093,0.16429],"force_p95":0.10311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2296,"mean_force":0.07556,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53503,-0.01248,0.16382]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.54561,-0.02914,-0.00206],"force_p95":0.13754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18005,"mean_force":0.12723,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53511,-0.02872,0.04567]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5184,-0.01321,0.28578]},{"body_a":"world","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5377,-0.02715,0.16369]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56705,0.00845,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5554,0.03238,0.20915]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56705,0.00845,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55176,0.03206,0.30887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5081.0,"contact_point_centroid":[0.53361,-0.00938,0.04719],"force_p95":0.06687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09831,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53434,-0.02869,0.04468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5874.0,"contact_point_centroid":[0.53331,-0.04793,0.04687],"force_p95":0.06092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07746,"mean_force":0.03796,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53434,-0.02869,0.04468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":837.0,"contact_point_centroid":[0.55527,0.025,0.20484],"force_p95":0.01294,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01077,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55503,0.02501,0.20246]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.5582,0.03265,0.20668],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01088,"mean_force":0.00995,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55788,0.03265,0.20437]}],"total_contact_groups":15},"final_pose_error":0.07217,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56705,0.00845,0.01602],"final_tcp_position":[0.55258,0.03209,0.39178],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.63613,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53713,-0.02554,0.27507],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2604.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5404,-0.02885,0.05432],"tcp_start":[0.53713,-0.02554,0.27507],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02876,0.02579],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26073,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13595,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12635.0,"raw_peak_contact_force":0.18005,"subtask_id":"grasp_1","tcp_end":[0.53431,-0.02869,0.04465],"tcp_start":[0.5404,-0.02885,0.05432],"tcp_to_object_dist_end":0.02194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54276,-0.0287,0.11354],"object_pos_start":[0.54552,-0.02876,0.02579],"object_to_goal_dist_end":0.22276,"object_to_goal_dist_start":0.26073,"object_z_max":0.11343,"peak_contact_force":0.10511,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23868.0,"raw_peak_contact_force":0.45978,"tcp_end":[0.53015,-0.02855,0.13713],"tcp_start":[0.53431,-0.02869,0.04465],"tcp_to_object_dist_end":0.02675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56705,0.00845,0.01602],"object_pos_start":[0.54276,-0.0287,0.11354],"object_to_goal_dist_end":0.23389,"object_to_goal_dist_start":0.22276,"object_z_max":0.15832,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17367.0,"raw_peak_contact_force":1.63613,"subtask_id":"transport_arc","tcp_end":[0.55905,0.03247,0.20664],"tcp_start":[0.53015,-0.02855,0.13713],"tcp_to_object_dist_end":0.1923,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56705,0.00845,0.01602],"object_pos_start":[0.56705,0.00845,0.01602],"object_to_goal_dist_end":0.23389,"object_to_goal_dist_start":0.23389,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55398,0.03225,0.22949],"tcp_start":[0.55905,0.03247,0.20664],"tcp_to_object_dist_end":0.21519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56705,0.00845,0.01602],"object_pos_start":[0.56705,0.00845,0.01602],"object_to_goal_dist_end":0.23389,"object_to_goal_dist_start":0.23389,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55258,0.03209,0.39178],"tcp_start":[0.55398,0.03225,0.22949],"tcp_to_object_dist_end":0.37678,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```