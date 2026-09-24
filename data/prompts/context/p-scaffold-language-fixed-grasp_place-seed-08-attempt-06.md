## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3395 | 0.29 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.4989 | 0.45 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0985 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2124 | 0.23 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2828 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.340) — your mutation base

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

- **Composite score**: 0.340
- **task_score** (E): 0.289
- **fitness_score**: 0.610  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.270

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0572 |
| descend_1 | 1.00 | 1.00 | 0.2206 |
| grasp_1 | 1.00 | 1.00 | 0.0108 |
| lift_1 | 0.67 | 1.00 | 0.1423 |
| transport_1 | 1.00 | 1.00 | 0.2074 |
| release_1 | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.002, 0.275) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 4.010 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.002, 0.275)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.046) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 44.333 | 0.140 | 0.187 |
| lift_1 | lift | 0.67 / step_budget | (0.511, -0.001, 0.046)→(0.507, -0.001, 0.188) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.160) | 0.289→0.232 | 1.00 / 25.333 | 0.103 | 0.450 |
| transport_1 | approach | 1.00 / step_budget | (0.507, -0.001, 0.188)→(0.595, 0.184, 0.213) | (0.518, -0.001, 0.160)→(0.599, 0.189, 0.115) | 0.232→0.096 | 1.00 / 12.333 | 3251.187 | 0.940 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.184, 0.213)→(0.590, 0.183, 0.234) | (0.599, 0.189, 0.115)→(0.598, 0.191, 0.018) | 0.096→0.188 | 1.00 / 3.333 | 0.161 | 1.174 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.352
- phase_score: 0.630
- phase_breakdown.transport_arc_score: 0.592
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.015
- phase_breakdown.release_1_score: 0.447
- phase_breakdown.descend_1_score: 0.872
- grasp_place_fitness: 0.642

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.642
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.352
- **Median Q (composite search score)**: 0.333
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67606,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23501,"lift_1.lift_height":0.18749,"transport_1.transport_speed":0.24537},"optimized_scores":{"best_composite_score":0.31309,"best_fitness_score":0.58309,"best_task_score":0.23849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.57347,0.20645,-0.0107],"force_p95":1.73184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98066,"mean_force":0.67327,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56432,0.20412,0.23785]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.48008,0.04626,-0.00121],"force_p95":0.27857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41687,"mean_force":0.05792,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47145,0.04711,0.04878]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8284.0,"contact_point_centroid":[0.51488,0.09533,0.21586],"force_p95":0.12088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37354,"mean_force":0.0955,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50774,0.113,0.21873]},{"body_a":"world","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.56733,0.22661,-0.00205],"force_p95":0.20358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34866,"mean_force":0.12681,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56471,0.20892,0.24109]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16439.0,"contact_point_centroid":[0.47134,0.06581,0.11894],"force_p95":0.09845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30004,"mean_force":0.06231,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46908,0.0469,0.1182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15726.0,"contact_point_centroid":[0.47081,0.02796,0.11908],"force_p95":0.10159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29914,"mean_force":0.06404,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46906,0.04689,0.11876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8549.0,"contact_point_centroid":[0.51114,0.13137,0.2168],"force_p95":0.12339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28449,"mean_force":0.09105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50747,0.11259,0.21864]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.48273,0.04858,-0.00213],"force_p95":0.15651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21342,"mean_force":0.13221,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4736,0.04733,0.04767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.4722,0.02806,0.04833],"force_p95":0.08036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14744,"mean_force":0.052,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47291,0.04727,0.04688]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49126,0.01867,0.28282]},{"body_a":"world","body_b":"grasp_target","contact_count":2636.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47984,0.0433,0.15958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.47304,0.06639,0.0483],"force_p95":0.07331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07461,"mean_force":0.04418,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47291,0.04727,0.04689]},{"body_a":"left_finger","body_b":"right_finger","contact_count":23.0,"contact_point_centroid":[0.5662,0.20889,0.24203],"force_p95":0.01614,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01614,"mean_force":0.01401,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56773,0.20947,0.23905]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.56646,0.20958,0.23882],"force_p95":0.01359,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01407,"mean_force":0.01068,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56685,0.20984,0.23654]}],"total_contact_groups":14},"final_pose_error":0.02604,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56659,0.22737,0.01602],"final_tcp_position":[0.568,0.20996,0.23914],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9753.19171,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":11.78441,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48335,0.03908,0.26657],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2636.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47849,0.04771,0.05484],"tcp_start":[0.48335,0.03908,0.26657],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04762,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.291,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15277,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10759.0,"raw_peak_contact_force":0.21342,"subtask_id":"grasp_1","tcp_end":[0.47288,0.04726,0.04686],"tcp_start":[0.47849,0.04771,0.05484],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4788,0.04737,0.17903],"object_pos_start":[0.48265,0.04762,0.02556],"object_to_goal_dist_end":0.21496,"object_to_goal_dist_start":0.291,"object_z_max":0.17884,"peak_contact_force":0.09796,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32300.0,"raw_peak_contact_force":0.41687,"tcp_end":[0.46943,0.04693,0.20905],"tcp_start":[0.47288,0.04726,0.04686],"tcp_to_object_dist_end":0.03145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5711,0.22024,0.01782],"object_pos_start":[0.4788,0.04737,0.17903],"object_to_goal_dist_end":0.21311,"object_to_goal_dist_start":0.21496,"object_z_max":0.19576,"peak_contact_force":9753.19171,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16986.0,"raw_peak_contact_force":1.98066,"subtask_id":"transport_arc","tcp_end":[0.568,0.20996,0.23914],"tcp_start":[0.46943,0.04693,0.20905],"tcp_to_object_dist_end":0.22159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56659,0.22737,0.01602],"object_pos_start":[0.5711,0.22024,0.01782],"object_to_goal_dist_end":0.21501,"object_to_goal_dist_start":0.21311,"object_z_max":0.0189,"peak_contact_force":0.12269,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":986.0,"raw_peak_contact_force":0.34866,"subtask_id":"release_1","tcp_end":[0.5637,0.20848,0.26101],"tcp_start":[0.568,0.20996,0.23914],"tcp_to_object_dist_end":0.24574,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63816,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29697,"lift_1.lift_height":0.29873,"transport_1.transport_speed":0.34056},"optimized_scores":{"best_composite_score":0.33346,"best_fitness_score":0.60346,"best_task_score":0.27553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":430.0,"contact_point_centroid":[0.61418,0.19927,-0.00454],"force_p95":0.94184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61267,"mean_force":0.23146,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59268,0.19737,0.22294]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.53438,-0.02089,-0.00115],"force_p95":0.34088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46043,"mean_force":0.06664,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5245,-0.021,0.04684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9617.0,"contact_point_centroid":[0.55844,0.10093,0.20899],"force_p95":0.13284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45313,"mean_force":0.09534,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55583,0.0819,0.20936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18.0,"contact_point_centroid":[0.59322,0.21642,0.21241],"force_p95":0.37646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41954,"mean_force":0.26333,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59727,0.19893,0.21694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10450.0,"contact_point_centroid":[0.56378,0.06352,0.20739],"force_p95":0.12403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4164,"mean_force":0.09002,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55539,0.08061,0.2093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.60553,0.1854,0.21064],"force_p95":0.2108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36974,"mean_force":0.07815,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5969,0.19914,0.21628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15454.0,"contact_point_centroid":[0.52451,-0.00197,0.11696],"force_p95":0.1018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29816,"mean_force":0.06514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.522,-0.02094,0.11536]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17061.0,"contact_point_centroid":[0.52434,-0.03984,0.1155],"force_p95":0.09632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28746,"mean_force":0.05981,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52199,-0.02094,0.11408]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.53702,-0.02122,-0.00204],"force_p95":0.13316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16452,"mean_force":0.12608,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52688,-0.02105,0.04613]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51663,-0.01087,0.30874]},{"body_a":"world","body_b":"grasp_target","contact_count":3100.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53111,-0.02038,0.18519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4363.0,"contact_point_centroid":[0.5269,-0.00177,0.04824],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10897,"mean_force":0.04926,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52612,-0.02103,0.04517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5122.0,"contact_point_centroid":[0.52626,-0.04012,0.0474],"force_p95":0.06521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08126,"mean_force":0.04281,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52612,-0.02103,0.04517]}],"total_contact_groups":13},"final_pose_error":0.03351,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61426,0.1994,0.01618],"final_tcp_position":[0.59739,0.1986,0.21712],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.61267,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53185,-0.01968,0.31861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3100.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53215,-0.02114,0.05459],"tcp_start":[0.53185,-0.01968,0.31861],"tcp_to_object_dist_end":0.02899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.53694,-0.02096,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31656,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1312,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11165.0,"raw_peak_contact_force":0.16452,"subtask_id":"grasp_1","tcp_end":[0.52609,-0.02103,0.04514],"tcp_start":[0.53215,-0.02114,0.05459],"tcp_to_object_dist_end":0.02214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53316,-0.02091,0.17979],"object_pos_start":[0.53694,-0.02096,0.02584],"object_to_goal_dist_end":0.26182,"object_to_goal_dist_start":0.31656,"object_z_max":0.1796,"peak_contact_force":0.10672,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32658.0,"raw_peak_contact_force":0.46043,"tcp_end":[0.52249,-0.02095,0.20766],"tcp_start":[0.52609,-0.02103,0.04514],"tcp_to_object_dist_end":0.02985,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60185,0.20071,0.17875],"object_pos_start":[0.53316,-0.02091,0.17979],"object_to_goal_dist_end":0.04031,"object_to_goal_dist_start":0.26182,"object_z_max":0.18,"peak_contact_force":0.2345,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20067.0,"raw_peak_contact_force":0.45313,"subtask_id":"transport_arc","tcp_end":[0.59739,0.1986,0.21712],"tcp_start":[0.52249,-0.02095,0.20766],"tcp_to_object_dist_end":0.03869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61426,0.1994,0.01618],"object_pos_start":[0.60185,0.20071,0.17875],"object_to_goal_dist_end":0.19336,"object_to_goal_dist_start":0.04031,"object_z_max":0.17875,"peak_contact_force":0.12739,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":552.0,"raw_peak_contact_force":1.61267,"subtask_id":"release_1","tcp_end":[0.59253,0.19732,0.23797],"tcp_start":[0.59739,0.1986,0.21712],"tcp_to_object_dist_end":0.22286,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70732,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20835,"lift_1.lift_height":0.11474,"transport_1.transport_speed":0.31418},"optimized_scores":{"best_composite_score":0.37204,"best_fitness_score":0.64204,"best_task_score":0.3522},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.60331,0.1452,-0.00703],"force_p95":1.2019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55968,"mean_force":0.3978,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61304,0.14287,0.19606]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54301,-0.02825,-0.00117],"force_p95":0.31674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47157,"mean_force":0.0717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53256,-0.0286,0.0463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":682.0,"contact_point_centroid":[0.61495,0.16256,0.17641],"force_p95":0.28076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42229,"mean_force":0.10198,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61653,0.14387,0.17953]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.62417,0.12727,0.17449],"force_p95":0.20751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41415,"mean_force":0.09651,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61655,0.14388,0.17957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12796.0,"contact_point_centroid":[0.57561,0.0355,0.15964],"force_p95":0.12449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38752,"mean_force":0.08146,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57006,0.05327,0.16126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11592.0,"contact_point_centroid":[0.57186,0.07337,0.16036],"force_p95":0.12724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34024,"mean_force":0.08676,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57078,0.05462,0.16157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12903.0,"contact_point_centroid":[0.53107,-0.04751,0.09238],"force_p95":0.08505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28451,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52998,-0.02851,0.09031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11169.0,"contact_point_centroid":[0.53145,-0.00936,0.09143],"force_p95":0.09974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27146,"mean_force":0.05883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52997,-0.0285,0.08935]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.54561,-0.02914,-0.00206],"force_p95":0.13876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18189,"mean_force":0.1276,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.535,-0.02868,0.04562]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51736,-0.01256,0.26889]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53723,-0.02703,0.14629]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5080.0,"contact_point_centroid":[0.53352,-0.00933,0.04725],"force_p95":0.06706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0986,"mean_force":0.04306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53423,-0.02865,0.04463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5878.0,"contact_point_centroid":[0.53319,-0.04788,0.04692],"force_p95":0.06116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07773,"mean_force":0.03795,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53423,-0.02865,0.04464]}],"total_contact_groups":13},"final_pose_error":0.02876,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61212,0.14501,0.02305],"final_tcp_position":[0.61854,0.14392,0.18345],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.55968,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53658,-0.02537,0.24008],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54027,-0.02879,0.05426],"tcp_start":[0.53658,-0.02537,0.24008],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.54552,-0.02874,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26072,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13701,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12638.0,"raw_peak_contact_force":0.18189,"subtask_id":"grasp_1","tcp_end":[0.5342,-0.02865,0.0446],"tcp_start":[0.54027,-0.02879,0.05426],"tcp_to_object_dist_end":0.02197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":635.0,"n_steps_budget":720.0,"object_pos_end":[0.54267,-0.02872,0.12233],"object_pos_start":[0.54552,-0.02874,0.02577],"object_to_goal_dist_end":0.22048,"object_to_goal_dist_start":0.26072,"object_z_max":0.12222,"peak_contact_force":0.10557,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24221.0,"raw_peak_contact_force":0.47157,"tcp_end":[0.53014,-0.02851,0.14652],"tcp_start":[0.5342,-0.02865,0.0446],"tcp_to_object_dist_end":0.02724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62523,0.14685,0.14989],"object_pos_start":[0.54267,-0.02872,0.12233],"object_to_goal_dist_end":0.03339,"object_to_goal_dist_start":0.22048,"object_z_max":0.14986,"peak_contact_force":0.13447,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24388.0,"raw_peak_contact_force":0.38752,"subtask_id":"transport_arc","tcp_end":[0.61854,0.14392,0.18345],"tcp_start":[0.53014,-0.02851,0.14652],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61212,0.14501,0.02305],"object_pos_start":[0.62523,0.14685,0.14989],"object_to_goal_dist_end":0.15653,"object_to_goal_dist_start":0.03339,"object_z_max":0.14989,"peak_contact_force":0.2321,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1560.0,"raw_peak_contact_force":1.55968,"subtask_id":"release_1","tcp_end":[0.61299,0.14286,0.20418],"tcp_start":[0.61854,0.14392,0.18345],"tcp_to_object_dist_end":0.18115,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```