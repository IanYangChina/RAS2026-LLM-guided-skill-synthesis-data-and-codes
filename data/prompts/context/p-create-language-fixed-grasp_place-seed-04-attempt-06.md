## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 4 | 0.3107 | 0.31 | ❌ rejected |
| 5 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3394 | 0.34 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 3 | 0.3577 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2982 | 0.31 | ❌ rejected |
| 2 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3394 | 0.34 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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

## Current Skill (Q=0.311) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
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
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
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
    tolerance: 0.005
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: grasp_1
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
    tolerance: 0.02
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
    anchor: current_tcp
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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.311
- **task_score** (E): 0.312
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1561 |
| descend_1 | 1.00 | 1.00 | 0.1035 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.0987 |
| transport_arc | 1.00 | 1.00 | 0.1873 |
| release_1 | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.147) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.147)→(0.521, 0.005, 0.044) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.044)→(0.513, 0.005, 0.035) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.667 | 0.135 | 0.179 |
| lift_object | lift | 1.00 / step_budget | (0.513, 0.005, 0.035)→(0.521, 0.005, 0.133) | (0.526, 0.005, 0.026)→(0.536, 0.005, 0.116) | 0.249→0.204 | 1.00 / 23.000 | 524.439 | 0.515 |
| transport_arc | approach | 1.00 / step_budget | (0.521, 0.005, 0.133)→(0.601, 0.159, 0.181) | (0.536, 0.005, 0.116)→(0.575, 0.085, 0.014) | 0.204→0.198 | 1.00 / 6.667 | 3249.666 | 1.552 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.159, 0.181)→(0.595, 0.158, 0.201) | (0.575, 0.085, 0.014)→(0.575, 0.086, 0.016) | 0.198→0.196 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.540
- phase_score: 0.684
- phase_breakdown.descend_1_score: 0.838
- phase_breakdown.transport_arc_score: 0.675
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.115
- phase_breakdown.release_1_score: 0.491
- grasp_place_fitness: 0.745

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.280
- **K-run variance**: 0.0071
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.475


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83077,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05797,"lift_object.lift_height":0.11403,"release_1.release_duration":1.81479,"transport_arc.arc_height":0.29742},"optimized_scores":{"best_composite_score":0.28028,"best_fitness_score":0.60028,"best_task_score":0.24789},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1257.0,"contact_point_centroid":[0.59023,0.05889,-0.00274],"force_p95":0.38884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66357,"mean_force":0.1593,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.6041,0.09922,0.18779]},{"body_a":"world","body_b":"grasp_target","contact_count":336.0,"contact_point_centroid":[0.5412,0.00073,-0.00159],"force_p95":0.28859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54933,"mean_force":0.10621,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52834,0.00083,0.03253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10372.0,"contact_point_centroid":[0.53402,-0.01814,0.07165],"force_p95":0.10192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29982,"mean_force":0.06519,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53162,0.00076,0.06988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10715.0,"contact_point_centroid":[0.53369,0.01967,0.0703],"force_p95":0.10251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28863,"mean_force":0.06364,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53148,0.00076,0.06847]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2377.0,"contact_point_centroid":[0.55454,0.00059,0.14552],"force_p95":0.15783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25976,"mean_force":0.09135,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54873,0.01878,0.14615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1880.0,"contact_point_centroid":[0.55348,0.03575,0.14484],"force_p95":0.18971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25945,"mean_force":0.10789,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5477,0.01717,0.14457]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15456,"mean_force":0.12528,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53187,0.00091,0.03352]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5167,0.00046,0.20397]},{"body_a":"world","body_b":"grasp_target","contact_count":3472.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53602,0.00097,0.06588]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59021,0.05899,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6308,0.14294,0.18606]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53136,-0.01832,0.03478],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11656,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53062,0.00089,0.03206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53134,0.01996,0.0339],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09483,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53062,0.00089,0.03206]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1064.0,"contact_point_centroid":[0.61029,0.10755,0.19149],"force_p95":0.01269,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01081,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60994,0.10754,0.18929]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.6339,0.14384,0.18477],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01005,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63342,0.14383,0.18276]}],"total_contact_groups":14},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59021,0.05899,0.01602],"final_tcp_position":[0.63497,0.1435,0.18627],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.74915,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53572,0.00095,0.10599],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3472.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53894,0.00103,0.04181],"tcp_start":[0.53572,0.00095,0.10599],"tcp_to_object_dist_end":0.01668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00075,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12978,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10794.0,"raw_peak_contact_force":0.15456,"subtask_id":"grasp_1","tcp_end":[0.53059,0.00088,0.03202],"tcp_start":[0.53894,0.00103,0.04181],"tcp_to_object_dist_end":0.01492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.55479,0.00067,0.11295],"object_pos_start":[0.54418,0.00075,0.02588],"object_to_goal_dist_end":0.19876,"object_to_goal_dist_start":0.2505,"object_z_max":0.11284,"peak_contact_force":1573.09317,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21423.0,"raw_peak_contact_force":0.54933,"tcp_end":[0.53908,0.00069,0.12706],"tcp_start":[0.53059,0.00088,0.03202],"tcp_to_object_dist_end":0.02112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.59021,0.05899,0.01602],"object_pos_start":[0.55479,0.00067,0.11295],"object_to_goal_dist_end":0.20921,"object_to_goal_dist_start":0.19876,"object_z_max":0.14414,"peak_contact_force":9748.74915,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6578.0,"raw_peak_contact_force":1.66357,"subtask_id":"transport_arc","tcp_end":[0.63497,0.1435,0.18627],"tcp_start":[0.53908,0.00069,0.12706],"tcp_to_object_dist_end":0.19528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59021,0.05899,0.01602],"object_pos_start":[0.59021,0.05899,0.01602],"object_to_goal_dist_end":0.20921,"object_to_goal_dist_start":0.20921,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62928,0.14246,0.20535],"tcp_start":[0.63497,0.1435,0.18627],"tcp_to_object_dist_end":0.21057,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09008,"lift_object.lift_height":0.12374,"release_1.release_duration":0.89673,"transport_arc.arc_height":0.26788},"optimized_scores":{"best_composite_score":0.42536,"best_fitness_score":0.74536,"best_task_score":0.53959},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.59931,0.16866,-0.00686],"force_p95":0.99981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16408,"mean_force":0.41466,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58758,0.1576,0.11716]},{"body_a":"world","body_b":"grasp_target","contact_count":230.0,"contact_point_centroid":[0.52763,0.02918,-0.00128],"force_p95":0.28196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53597,"mean_force":0.07778,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51546,0.02964,0.03509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11020.0,"contact_point_centroid":[0.52067,0.04841,0.07727],"force_p95":0.10402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29788,"mean_force":0.06428,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51827,0.02951,0.07554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10559.0,"contact_point_centroid":[0.52116,0.01066,0.07926],"force_p95":0.10207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29566,"mean_force":0.06614,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51847,0.02951,0.07749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2734.0,"contact_point_centroid":[0.54999,0.05358,0.14007],"force_p95":0.18116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28754,"mean_force":0.1099,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54457,0.07199,0.1406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3187.0,"contact_point_centroid":[0.55238,0.09456,0.13952],"force_p95":0.14862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27454,"mean_force":0.09635,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54673,0.07647,0.14051]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03058,-0.00209],"force_p95":0.14917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21644,"mean_force":0.12978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51837,0.02987,0.03495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4085.0,"contact_point_centroid":[0.51778,0.01059,0.03635],"force_p95":0.07913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13974,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51715,0.02979,0.03357]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51064,0.01284,0.21997]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60003,0.16938,-0.00216],"force_p95":0.12488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12577,"mean_force":0.11591,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58502,0.16208,0.11338]},{"body_a":"world","body_b":"grasp_target","contact_count":3276.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52304,0.02873,0.07951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.51777,0.04891,0.03538],"force_p95":0.07168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0834,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51716,0.02979,0.03357]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8.0,"contact_point_centroid":[0.58726,0.16265,0.10923],"force_p95":0.01639,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.0082,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58696,0.16263,0.10715]}],"total_contact_groups":13},"final_pose_error":0.01967,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60003,0.16936,0.01602],"final_tcp_position":[0.59031,0.16309,0.11265],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.16408,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52323,0.02656,0.13774],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3276.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5253,0.03033,0.04287],"tcp_start":[0.52323,0.02656,0.13774],"tcp_to_object_dist_end":0.01765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02981,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18434,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14376,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10838.0,"raw_peak_contact_force":0.21644,"subtask_id":"grasp_1","tcp_end":[0.51712,0.02978,0.03353],"tcp_start":[0.5253,0.03033,0.04287],"tcp_to_object_dist_end":0.01543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.54031,0.02964,0.12045],"object_pos_start":[0.5304,0.02981,0.02568],"object_to_goal_dist_end":0.1615,"object_to_goal_dist_start":0.18434,"object_z_max":0.12034,"peak_contact_force":0.11239,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21809.0,"raw_peak_contact_force":0.53597,"tcp_end":[0.52553,0.02954,0.13693],"tcp_start":[0.51712,0.02978,0.03353],"tcp_to_object_dist_end":0.02214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.60031,0.16749,0.00864],"object_pos_start":[0.54031,0.02964,0.12045],"object_to_goal_dist_end":0.10007,"object_to_goal_dist_start":0.1615,"object_z_max":0.12442,"peak_contact_force":0.12662,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6057.0,"raw_peak_contact_force":1.16408,"subtask_id":"transport_arc","tcp_end":[0.59031,0.16309,0.11265],"tcp_start":[0.52553,0.02954,0.13693],"tcp_to_object_dist_end":0.10459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60003,0.16936,0.01602],"object_pos_start":[0.60031,0.16749,0.00864],"object_to_goal_dist_end":0.09254,"object_to_goal_dist_start":0.10007,"object_z_max":0.0165,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":808.0,"raw_peak_contact_force":0.12577,"subtask_id":"release_1","tcp_end":[0.58315,0.16146,0.13328],"tcp_start":[0.59031,0.16309,0.11265],"tcp_to_object_dist_end":0.11874,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14893,"lift_object.lift_height":0.12142,"release_1.release_duration":0.96609,"transport_arc.arc_height":0.28734},"optimized_scores":{"best_composite_score":0.2265,"best_fitness_score":0.5465,"best_task_score":0.14932},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1739.0,"contact_point_centroid":[0.53523,0.02987,-0.00257],"force_p95":0.25857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8286,"mean_force":0.14876,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54621,0.09954,0.24037]},{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.50141,-0.01531,-0.00152],"force_p95":0.24631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46072,"mean_force":0.09573,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.489,-0.01533,0.03929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10590.0,"contact_point_centroid":[0.4938,0.00376,0.07917],"force_p95":0.10202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30027,"mean_force":0.06367,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49198,-0.01526,0.07693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11520.0,"contact_point_centroid":[0.49372,-0.03416,0.07759],"force_p95":0.09874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27428,"mean_force":0.05939,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49185,-0.01526,0.07596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1979.0,"contact_point_centroid":[0.50781,0.01705,0.16356],"force_p95":0.17978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26675,"mean_force":0.10819,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50205,-0.0016,0.16247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2675.0,"contact_point_centroid":[0.50829,-0.01886,0.16399],"force_p95":0.13645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25071,"mean_force":0.08482,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5024,-0.00072,0.16392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01556,-0.00203],"force_p95":0.1338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16563,"mean_force":0.12557,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49222,-0.01539,0.0398]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.50382,-0.01567,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,-0.00587,0.25076]},{"body_a":"world","body_b":"grasp_target","contact_count":3164.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4982,-0.01398,0.11784]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53515,0.02991,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57402,0.16994,0.24585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4122.0,"contact_point_centroid":[0.49146,0.00391,0.04132],"force_p95":0.07671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09447,"mean_force":0.05207,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49106,-0.01537,0.03856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5372.0,"contact_point_centroid":[0.49081,-0.03443,0.04121],"force_p95":0.06393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08306,"mean_force":0.04079,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49106,-0.01537,0.03856]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1634.0,"contact_point_centroid":[0.55011,0.10723,0.24552],"force_p95":0.01168,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01591,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54962,0.10723,0.24327]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57631,0.17084,0.24391],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.00994,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57596,0.17083,0.24165]}],"total_contact_groups":14},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53515,0.02991,0.01602],"final_tcp_position":[0.5774,0.17051,0.24478],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.8286,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":776.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50039,-0.01241,0.19829],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3164.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49895,-0.01547,0.04705],"tcp_start":[0.50039,-0.01241,0.19829],"tcp_to_object_dist_end":0.02158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01524,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13248,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11294.0,"raw_peak_contact_force":0.16563,"subtask_id":"grasp_1","tcp_end":[0.49103,-0.01537,0.03852],"tcp_start":[0.49895,-0.01547,0.04705],"tcp_to_object_dist_end":0.01793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.51286,-0.01508,0.11598],"object_pos_start":[0.50372,-0.01524,0.02586],"object_to_goal_dist_end":0.25291,"object_to_goal_dist_start":0.31209,"object_z_max":0.11587,"peak_contact_force":0.11134,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22426.0,"raw_peak_contact_force":0.46072,"tcp_end":[0.49892,-0.01518,0.1352],"tcp_start":[0.49103,-0.01537,0.03852],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.53515,0.02991,0.01602],"object_pos_start":[0.51286,-0.01508,0.11598],"object_to_goal_dist_end":0.28525,"object_to_goal_dist_start":0.25291,"object_z_max":0.16876,"peak_contact_force":0.12262,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8027.0,"raw_peak_contact_force":1.8286,"subtask_id":"transport_arc","tcp_end":[0.5774,0.17051,0.24478],"tcp_start":[0.49892,-0.01518,0.1352],"tcp_to_object_dist_end":0.27182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53515,0.02991,0.01602],"object_pos_start":[0.53515,0.02991,0.01602],"object_to_goal_dist_end":0.28525,"object_to_goal_dist_start":0.28525,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57292,0.16947,0.26574],"tcp_start":[0.5774,0.17051,0.24478],"tcp_to_object_dist_end":0.28856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```