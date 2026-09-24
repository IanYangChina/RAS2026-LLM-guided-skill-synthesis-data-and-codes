## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2982 | 0.31 | ❌ rejected |
| 2 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3394 | 0.34 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 4 | 0.3252 | 0.34 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 1 | 0.3405 | 0.34 | ✅ accepted |

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

## Current Skill (Q=0.298) — your mutation base

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

- **Composite score**: 0.298
- **task_score** (E): 0.309
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0858 |
| descend_1 | 1.00 | 1.00 | 0.1654 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.0978 |
| transport_arc | 1.00 | 1.00 | 0.1848 |
| release_1 | 1.00 | 1.00 | 0.0211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.004, 0.220) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, 0.004, 0.220)→(0.521, 0.005, 0.054) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.054)→(0.513, 0.005, 0.045) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.667 | 0.140 | 0.179 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.045)→(0.521, 0.005, 0.142) | (0.526, 0.005, 0.026)→(0.534, 0.005, 0.117) | 0.249→0.205 | 1.00 / 27.000 | 0.094 | 0.408 |
| transport_arc | approach | 1.00 / step_budget | (0.521, 0.005, 0.142)→(0.601, 0.159, 0.182) | (0.534, 0.005, 0.117)→(0.573, 0.082, 0.015) | 0.205→0.200 | 1.00 / 7.000 | 91004.871 | 1.569 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.159, 0.182)→(0.595, 0.158, 0.202) | (0.573, 0.082, 0.015)→(0.573, 0.083, 0.016) | 0.200→0.198 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.540
- phase_score: 0.682
- phase_breakdown.descend_1_score: 0.873
- phase_breakdown.transport_arc_score: 0.673
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.022
- phase_breakdown.release_1_score: 0.489
- grasp_place_fitness: 0.734

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.734
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.264
- **K-run variance**: 0.0071
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.904,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19251,"grasp_1.grasp_duration":0.31059,"lift_1.lift_height":0.12737,"transport_arc.arc_height":0.27006},"optimized_scores":{"best_composite_score":0.26391,"best_fitness_score":0.58391,"best_task_score":0.23871},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1257.0,"contact_point_centroid":[0.58483,0.04849,-0.00281],"force_p95":0.42749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70226,"mean_force":0.16821,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60274,0.09703,0.19363]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.54283,0.0008,-0.00113],"force_p95":0.26683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4083,"mean_force":0.05394,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52897,0.00084,0.04568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9583.0,"contact_point_centroid":[0.53565,-0.0181,0.08923],"force_p95":0.09923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29151,"mean_force":0.06707,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53219,0.00076,0.08722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9937.0,"contact_point_centroid":[0.5356,0.01962,0.08961],"force_p95":0.10107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26977,"mean_force":0.0649,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53226,0.00076,0.08747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1894.0,"contact_point_centroid":[0.55246,-0.00398,0.15436],"force_p95":0.14068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25787,"mean_force":0.08096,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54614,0.01434,0.15433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1495.0,"contact_point_centroid":[0.5515,0.03172,0.15352],"force_p95":0.17562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25588,"mean_force":0.09823,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54534,0.01301,0.15302]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14914,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53144,0.0009,0.0455]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.54431,0.00113,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12346,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51442,0.00039,0.26931]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4117.0,"contact_point_centroid":[0.53111,-0.01833,0.04677],"force_p95":0.07624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12323,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53023,0.00088,0.04407]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53347,0.0009,0.14398]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58488,0.05048,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63059,0.14256,0.18795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53107,0.01995,0.04589],"force_p95":0.06828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09366,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53023,0.00088,0.04407]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1215.0,"contact_point_centroid":[0.60621,0.10127,0.19678],"force_p95":0.01217,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01658,"mean_force":0.01067,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.60571,0.10127,0.19448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.63355,0.14347,0.18696],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01019,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63317,0.14346,0.18462]}],"total_contact_groups":14},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58488,0.05048,0.01602],"final_tcp_position":[0.63477,0.14311,0.18826],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273014.40366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":584.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53078,0.00081,0.23665],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53866,0.00103,0.05419],"tcp_start":[0.53078,0.00081,0.23665],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13023,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10792.0,"raw_peak_contact_force":0.14914,"subtask_id":"grasp_1","tcp_end":[0.5302,0.00087,0.04403],"tcp_start":[0.53866,0.00103,0.05419],"tcp_to_object_dist_end":0.02294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.55228,0.00075,0.11585],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.19877,"object_to_goal_dist_start":0.25048,"object_z_max":0.11574,"peak_contact_force":0.08563,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19672.0,"raw_peak_contact_force":0.4083,"tcp_end":[0.53923,0.00071,0.14056],"tcp_start":[0.5302,0.00087,0.04403],"tcp_to_object_dist_end":0.02794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.58488,0.05048,0.01602],"object_pos_start":[0.55228,0.00075,0.11585],"object_to_goal_dist_end":0.21487,"object_to_goal_dist_start":0.19877,"object_z_max":0.14096,"peak_contact_force":273014.40366,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5861.0,"raw_peak_contact_force":1.70226,"subtask_id":"transport_arc","tcp_end":[0.63477,0.14311,0.18826],"tcp_start":[0.53923,0.00071,0.14056],"tcp_to_object_dist_end":0.20183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58488,0.05048,0.01602],"object_pos_start":[0.58488,0.05048,0.01602],"object_to_goal_dist_end":0.21487,"object_to_goal_dist_start":0.21487,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62908,0.14208,0.20725],"tcp_start":[0.63477,0.14311,0.18826],"tcp_to_object_dist_end":0.2166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17409,"grasp_1.grasp_duration":0.97519,"lift_1.lift_height":0.12942,"transport_arc.arc_height":0.28694},"optimized_scores":{"best_composite_score":0.41411,"best_fitness_score":0.73411,"best_task_score":0.5401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.60142,0.1703,-0.00614],"force_p95":1.10563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24094,"mean_force":0.34614,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.58679,0.15603,0.11851]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.52907,0.02917,-0.00122],"force_p95":0.26713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41655,"mean_force":0.05333,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5157,0.02929,0.04638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10848.0,"contact_point_centroid":[0.52169,0.0482,0.08988],"force_p95":0.09299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28153,"mean_force":0.06061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51871,0.0293,0.08766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3783.0,"contact_point_centroid":[0.55319,0.09476,0.14415],"force_p95":0.12874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28001,"mean_force":0.08111,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54686,0.07652,0.14353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9743.0,"contact_point_centroid":[0.52127,0.01032,0.08773],"force_p95":0.10795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25815,"mean_force":0.06586,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51851,0.0293,0.08603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3070.0,"contact_point_centroid":[0.55089,0.05418,0.14452],"force_p95":0.15123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25184,"mean_force":0.09322,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54502,0.07286,0.14404]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03067,-0.00212],"force_p95":0.15475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21533,"mean_force":0.13148,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51813,0.02947,0.0459]},{"body_a":"world","body_b":"grasp_target","contact_count":692.0,"contact_point_centroid":[0.5305,0.03079,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50973,0.01123,0.26112]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60348,0.17102,-0.00203],"force_p95":0.12453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12567,"mean_force":0.11778,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58499,0.16199,0.11361]},{"body_a":"world","body_b":"grasp_target","contact_count":2012.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52192,0.02677,0.1357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.51792,0.01018,0.04715],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10977,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51694,0.02939,0.04453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5234.0,"contact_point_centroid":[0.51727,0.04865,0.04679],"force_p95":0.07004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07472,"mean_force":0.04264,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51695,0.02939,0.04453]},{"body_a":"left_finger","body_b":"right_finger","contact_count":89.0,"contact_point_centroid":[0.58803,0.16274,0.11034],"force_p95":0.01515,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.01144,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58719,0.16271,0.10786]}],"total_contact_groups":13},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60349,0.17102,0.01602],"final_tcp_position":[0.59027,0.16298,0.11286],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.24094,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5212,0.02375,0.21985],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52519,0.02992,0.05417],"tcp_start":[0.5212,0.02375,0.21985],"tcp_to_object_dist_end":0.02866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.02982,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18437,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15165,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11850.0,"raw_peak_contact_force":0.21533,"subtask_id":"grasp_1","tcp_end":[0.51691,0.02939,0.0445],"tcp_start":[0.52519,0.02992,0.05417],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53813,0.03012,0.11699],"object_pos_start":[0.53045,0.02982,0.02557],"object_to_goal_dist_end":0.16168,"object_to_goal_dist_start":0.18437,"object_z_max":0.11688,"peak_contact_force":0.10193,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20746.0,"raw_peak_contact_force":0.41655,"tcp_end":[0.52559,0.02953,0.14252],"tcp_start":[0.51691,0.02939,0.0445],"tcp_to_object_dist_end":0.02844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.60419,0.17001,0.01243],"object_pos_start":[0.53813,0.03012,0.11699],"object_to_goal_dist_end":0.09607,"object_to_goal_dist_start":0.16168,"object_z_max":0.11885,"peak_contact_force":0.08675,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7026.0,"raw_peak_contact_force":1.24094,"subtask_id":"transport_arc","tcp_end":[0.59027,0.16298,0.11286],"tcp_start":[0.52559,0.02953,0.14252],"tcp_to_object_dist_end":0.10163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60349,0.17102,0.01602],"object_pos_start":[0.60419,0.17001,0.01243],"object_to_goal_dist_end":0.0924,"object_to_goal_dist_start":0.09607,"object_z_max":0.01647,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":889.0,"raw_peak_contact_force":0.12567,"subtask_id":"release_1","tcp_end":[0.58312,0.16136,0.13351],"tcp_start":[0.59027,0.16298,0.11286],"tcp_to_object_dist_end":0.11963,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15369,"grasp_1.grasp_duration":0.73553,"lift_1.lift_height":0.12986,"transport_arc.arc_height":0.29866},"optimized_scores":{"best_composite_score":0.21664,"best_fitness_score":0.53664,"best_task_score":0.14682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1808.0,"contact_point_centroid":[0.53121,0.02669,-0.00254],"force_p95":0.23857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76448,"mean_force":0.14852,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54513,0.097,0.23939]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.50246,-0.01482,-0.00112],"force_p95":0.24454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39912,"mean_force":0.04627,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48997,-0.01519,0.04791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9840.0,"contact_point_centroid":[0.49498,0.00379,0.08991],"force_p95":0.10384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27136,"mean_force":0.06543,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49255,-0.01516,0.08876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10657.0,"contact_point_centroid":[0.49503,-0.03406,0.08916],"force_p95":0.09819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25847,"mean_force":0.06112,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49247,-0.01516,0.08776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1870.0,"contact_point_centroid":[0.50787,0.01538,0.16498],"force_p95":0.16156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24561,"mean_force":0.09485,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50163,-0.00328,0.16459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.50825,-0.02013,0.16677],"force_p95":0.13536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23793,"mean_force":0.08219,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50218,-0.00177,0.16699]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01562,-0.00205],"force_p95":0.13736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17206,"mean_force":0.12642,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49228,-0.01523,0.04733]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.50382,-0.01567,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49981,-0.00583,0.25292]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49848,-0.0138,0.12767]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53117,0.02669,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57395,0.16977,0.24582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4358.0,"contact_point_centroid":[0.49162,0.00405,0.04797],"force_p95":0.07415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11506,"mean_force":0.04969,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49114,-0.01521,0.04609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5379.0,"contact_point_centroid":[0.49221,-0.03433,0.04848],"force_p95":0.06517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08296,"mean_force":0.04077,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49114,-0.01521,0.0461]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1721.0,"contact_point_centroid":[0.54864,0.10416,0.24462],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5483,0.10415,0.24229]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.5762,0.17067,0.24371],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01013,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57591,0.17066,0.24163]}],"total_contact_groups":14},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53117,0.02669,0.01602],"final_tcp_position":[0.57733,0.17033,0.24474],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.76448,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50041,-0.01234,0.20262],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49913,-0.01531,0.05483],"tcp_start":[0.50041,-0.01234,0.20262],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01524,0.02581],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31212,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13694,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11537.0,"raw_peak_contact_force":0.17206,"subtask_id":"grasp_1","tcp_end":[0.49111,-0.01521,0.04606],"tcp_start":[0.49913,-0.01531,0.05483],"tcp_to_object_dist_end":0.02386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.5107,-0.01543,0.1172],"object_pos_start":[0.50373,-0.01524,0.02581],"object_to_goal_dist_end":0.2532,"object_to_goal_dist_start":0.31212,"object_z_max":0.11708,"peak_contact_force":0.09378,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20642.0,"raw_peak_contact_force":0.39912,"tcp_end":[0.49903,-0.01517,0.1438],"tcp_start":[0.49111,-0.01521,0.04606],"tcp_to_object_dist_end":0.02905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.53117,0.02669,0.01602],"object_pos_start":[0.5107,-0.01543,0.1172],"object_to_goal_dist_end":0.28778,"object_to_goal_dist_start":0.2532,"object_z_max":0.16076,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7655.0,"raw_peak_contact_force":1.76448,"subtask_id":"transport_arc","tcp_end":[0.57733,0.17033,0.24474],"tcp_start":[0.49903,-0.01517,0.1438],"tcp_to_object_dist_end":0.274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53117,0.02669,0.01602],"object_pos_start":[0.53117,0.02669,0.01602],"object_to_goal_dist_end":0.28778,"object_to_goal_dist_start":0.28778,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57285,0.1693,0.26571],"tcp_start":[0.57733,0.17033,0.24474],"tcp_to_object_dist_end":0.29055,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```