## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2957 | 0.18 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.296) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: -0.296
- **task_score** (E): 0.184
- **fitness_score**: 0.174  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1692 |
| descend_1 | 0.00 | 1.00 | 0.0661 |
| grasp_1 | 1.00 | 1.00 | 0.0014 |
| lift_1 | 1.00 | 1.00 | 0.0284 |
| transport | 0.00 | 1.00 | 0.1060 |
| release_1 | 1.00 | 1.00 | 0.0226 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.407, 0.002, 0.159) | (0.526, 0.005, 0.030)→(0.489, 0.012, 0.016) | 0.246→0.266 | 1.00 / 5.000 | 190.924 | 1468.991 |
| descend_1 | descend | 0.00 / step_budget | (0.407, 0.002, 0.159)→(0.464, 0.010, 0.181) | (0.489, 0.012, 0.016)→(0.488, 0.012, 0.016) | 0.266→0.266 | 1.00 / 5.000 | 399.100 | 916.969 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, 0.010, 0.181)→(0.463, 0.010, 0.180) | (0.488, 0.012, 0.016)→(0.488, 0.012, 0.016) | 0.266→0.266 | 1.00 / 9.333 | 68.548 | 260.014 |
| lift_1 | lift | 1.00 / step_budget | (0.463, 0.010, 0.180)→(0.483, 0.014, 0.195) | (0.488, 0.012, 0.016)→(0.488, 0.012, 0.016) | 0.266→0.266 | 1.00 / 9.000 | 133.179 | 460.134 |
| transport | approach | 0.00 / step_budget | (0.483, 0.014, 0.195)→(0.513, 0.046, 0.259) | (0.488, 0.012, 0.016)→(0.488, 0.012, 0.016) | 0.266→0.266 | 1.00 / 9.000 | 49.365 | 262.380 |
| release_1 | release | 1.00 / step_budget | (0.513, 0.046, 0.259)→(0.513, 0.042, 0.278) | (0.488, 0.012, 0.016)→(0.488, 0.012, 0.016) | 0.266→0.266 | 1.00 / 4.667 | 85.119 | 86.329 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.281
- phase_score: 0.184
- phase_breakdown.release_1_score: 0.029
- phase_breakdown.descend_1_score: 0.048
- phase_breakdown.transport_arc_score: 0.042
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.027
- grasp_place_fitness: 0.220

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.220
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.281
- **Median Q (composite search score)**: -0.303
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":31.0,"average_failure_rate":0.2844,"average_mean_iterations":62.56881,"average_solve_count":109.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05092,"descend_1.depth":0.03603,"grasp_1.grasp_duration":1.87247,"lift_1.speed":0.05854,"release_1.release_duration":1.7923,"transport.arc_height":0.06772,"transport.speed":0.09366},"optimized_scores":{"best_composite_score":-0.3028,"best_fitness_score":0.1672,"best_task_score":0.16467},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63761,0.00021,-0.00046],"force_p95":197.97607,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1415.18332,"mean_force":198.64333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40296,9e-05,0.1339]},{"body_a":"world","body_b":"link6","contact_count":978.0,"contact_point_centroid":[0.62661,0.00602,-0.00023],"force_p95":510.57384,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":914.75985,"mean_force":289.0961,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42967,0.0022,0.19181]},{"body_a":"link5","body_b":"hand","contact_count":612.0,"contact_point_centroid":[0.51736,-0.06452,0.15463],"force_p95":334.6989,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.79839,"mean_force":225.16019,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49381,0.01009,0.19588]},{"body_a":"world","body_b":"link6","contact_count":447.0,"contact_point_centroid":[0.67583,0.00724,-0.00013],"force_p95":75.5042,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.15714,"mean_force":70.15862,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4647,0.00647,0.17299]},{"body_a":"world","body_b":"link6","contact_count":101.0,"contact_point_centroid":[0.68775,-0.00105,-6e-05],"force_p95":278.19772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.67145,"mean_force":171.30931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46852,0.00547,0.17202]},{"body_a":"link5","body_b":"hand","contact_count":295.0,"contact_point_centroid":[0.52687,-0.04305,0.17889],"force_p95":260.76526,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":287.80401,"mean_force":205.8374,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51729,0.03225,0.24259]},{"body_a":"grasp_target","body_b":"link6","contact_count":430.0,"contact_point_centroid":[0.53962,0.01744,0.03123],"force_p95":0.59993,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.73285,"mean_force":0.23289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3949,2e-05,0.11226]},{"body_a":"grasp_target","body_b":"link7","contact_count":476.0,"contact_point_centroid":[0.52915,0.00464,0.03254],"force_p95":0.98876,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.29923,"mean_force":0.36907,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39594,3e-05,0.11252]},{"body_a":"grasp_target","body_b":"hand","contact_count":96.0,"contact_point_centroid":[0.49784,0.01403,0.04539],"force_p95":2.42702,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.0016,"mean_force":1.02013,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38726,-8e-05,0.07624]},{"body_a":"world","body_b":"grasp_target","contact_count":3754.0,"contact_point_centroid":[0.51198,0.00743,-0.00229],"force_p95":0.29125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.54566,"mean_force":0.15686,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41523,0.00012,0.1447]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50547,0.00861,-0.00199],"force_p95":0.12279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13692,"mean_force":0.12268,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43034,0.00227,0.19189]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50546,0.00861,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4647,0.00647,0.173]},{"body_a":"world","body_b":"grasp_target","contact_count":3228.0,"contact_point_centroid":[0.50546,0.00861,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48836,0.00923,0.19055]},{"body_a":"world","body_b":"grasp_target","contact_count":4344.0,"contact_point_centroid":[0.50546,0.00861,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51909,0.03921,0.29793]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50546,0.00861,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53146,0.05839,0.40207]},{"body_a":"grasp_target","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.53439,0.00142,0.03589],"force_p95":0.04063,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.04286,"mean_force":0.02226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.39517,0.00043,0.15317]}],"total_contact_groups":21},"final_pose_error":0.23151,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50546,0.00861,0.01602],"final_tcp_position":[0.53081,0.05829,0.39429],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1415.18332,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50554,0.0086,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27053,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":189.38925,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5663.0,"raw_peak_contact_force":1415.18332,"subtask_id":"approach_1","tcp_end":[0.41926,0.00025,0.17254],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17892,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50546,0.00861,0.01602],"object_pos_start":[0.50554,0.0086,0.01602],"object_to_goal_dist_end":0.27057,"object_to_goal_dist_start":0.27053,"object_z_max":0.01602,"peak_contact_force":444.63435,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5032.0,"raw_peak_contact_force":914.75985,"subtask_id":"descend_1","tcp_end":[0.46489,0.00658,0.17452],"tcp_start":[0.41926,0.00025,0.17254],"tcp_to_object_dist_end":0.16363,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50546,0.00861,0.01602],"object_pos_start":[0.50546,0.00861,0.01602],"object_to_goal_dist_end":0.27057,"object_to_goal_dist_start":0.27057,"object_z_max":0.01602,"peak_contact_force":67.65191,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2594.0,"raw_peak_contact_force":336.15714,"subtask_id":"grasp_1","tcp_end":[0.46469,0.00645,0.17286],"tcp_start":[0.46489,0.00658,0.17452],"tcp_to_object_dist_end":0.16207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50546,0.00861,0.01602],"object_pos_start":[0.50546,0.00861,0.01602],"object_to_goal_dist_end":0.27057,"object_to_goal_dist_start":0.27057,"object_z_max":0.01602,"peak_contact_force":177.34507,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7480.0,"raw_peak_contact_force":394.79839,"tcp_end":[0.4973,0.01061,0.20036],"tcp_start":[0.46469,0.00645,0.17286],"tcp_to_object_dist_end":0.18454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.50546,0.00861,0.01602],"object_pos_start":[0.50546,0.00861,0.01602],"object_to_goal_dist_end":0.27057,"object_to_goal_dist_start":0.27057,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9405.0,"raw_peak_contact_force":287.80401,"subtask_id":"transport_arc","tcp_end":[0.53068,0.0584,0.39569],"tcp_start":[0.4973,0.01061,0.20036],"tcp_to_object_dist_end":0.38375,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50546,0.00861,0.01602],"object_pos_start":[0.50546,0.00861,0.01602],"object_to_goal_dist_end":0.27057,"object_to_goal_dist_start":0.27057,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53234,0.05829,0.42258],"tcp_start":[0.53068,0.0584,0.39569],"tcp_to_object_dist_end":0.41046,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":29.0,"average_failure_rate":0.26126,"average_mean_iterations":57.10811,"average_solve_count":111.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04629,"descend_1.depth":0.04747,"grasp_1.grasp_duration":0.84887,"lift_1.speed":0.0354,"release_1.release_duration":2.37035,"transport.arc_height":0.08238,"transport.speed":0.08289},"optimized_scores":{"best_composite_score":-0.24989,"best_fitness_score":0.22011,"best_task_score":0.28121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63546,0.00498,-0.00046],"force_p95":198.85689,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.44361,"mean_force":200.13306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39779,0.00469,0.12917]},{"body_a":"world","body_b":"link6","contact_count":980.0,"contact_point_centroid":[0.62534,0.01901,-0.00022],"force_p95":469.59301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.94932,"mean_force":294.93268,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42739,0.02055,0.19149]},{"body_a":"world","body_b":"link6","contact_count":624.0,"contact_point_centroid":[0.69676,0.04267,-7e-05],"force_p95":185.63446,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":849.15617,"mean_force":62.07568,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48494,0.05125,0.18774]},{"body_a":"link5","body_b":"hand","contact_count":525.0,"contact_point_centroid":[0.52919,-0.02329,0.17643],"force_p95":306.91394,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.83574,"mean_force":242.83473,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49258,0.05151,0.19431]},{"body_a":"link5","body_b":"hand","contact_count":1136.0,"contact_point_centroid":[0.52942,0.00621,0.17486],"force_p95":277.42824,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.36002,"mean_force":220.70802,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51718,0.08395,0.2235]},{"body_a":"world","body_b":"link6","contact_count":448.0,"contact_point_centroid":[0.66338,0.0472,-0.00013],"force_p95":73.99314,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.04482,"mean_force":71.21084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.462,0.04399,0.18421]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.7027,0.04636,-6e-05],"force_p95":190.26155,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.22946,"mean_force":151.27633,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49313,0.05163,0.19415]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52553,0.03257,0.16377],"force_p95":183.84918,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.12597,"mean_force":127.80773,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53094,0.10434,0.23381]},{"body_a":"world","body_b":"link6","contact_count":69.0,"contact_point_centroid":[0.6636,0.03794,-0.00019],"force_p95":101.10833,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.92435,"mean_force":60.79597,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53066,0.10374,0.22712]},{"body_a":"grasp_target","body_b":"link7","contact_count":251.0,"contact_point_centroid":[0.50634,0.01867,0.03507],"force_p95":2.88373,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.75362,"mean_force":0.46314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38943,0.00283,0.09811]},{"body_a":"grasp_target","body_b":"hand","contact_count":131.0,"contact_point_centroid":[0.49641,0.0399,0.05395],"force_p95":2.11225,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.62285,"mean_force":0.81887,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38594,0.00253,0.08397]},{"body_a":"world","body_b":"grasp_target","contact_count":3611.0,"contact_point_centroid":[0.50293,0.0453,-0.00228],"force_p95":0.39402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22588,"mean_force":0.15971,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41125,0.00457,0.14163]},{"body_a":"grasp_target","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.53806,0.03475,0.02877],"force_p95":0.86967,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95322,"mean_force":0.44242,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38379,0.00253,0.08671]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49752,0.04852,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42789,0.02078,0.19174]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.49752,0.04852,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.462,0.04399,0.18421]},{"body_a":"world","body_b":"grasp_target","contact_count":3884.0,"contact_point_centroid":[0.49752,0.04852,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48495,0.05147,0.18824]}],"total_contact_groups":23},"final_pose_error":0.14204,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49752,0.04852,0.01602],"final_tcp_position":[0.53134,0.10264,0.23546],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1349.44361,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49752,0.04852,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":192.03225,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5013.0,"raw_peak_contact_force":1349.44361,"subtask_id":"approach_1","tcp_end":[0.41036,0.00797,0.16296],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17559,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49752,0.04852,0.01602],"object_pos_start":[0.49752,0.04852,0.01602],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.1903,"object_z_max":0.01602,"peak_contact_force":376.95661,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4980.0,"raw_peak_contact_force":922.94932,"subtask_id":"descend_1","tcp_end":[0.46214,0.04356,0.18517],"tcp_start":[0.41036,0.00797,0.16296],"tcp_to_object_dist_end":0.17289,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49752,0.04852,0.01602],"object_pos_start":[0.49752,0.04852,0.01602],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.1903,"object_z_max":0.01602,"peak_contact_force":69.18008,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2596.0,"raw_peak_contact_force":232.04482,"subtask_id":"grasp_1","tcp_end":[0.462,0.04399,0.18409],"tcp_start":[0.46214,0.04356,0.18517],"tcp_to_object_dist_end":0.17185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":571.0,"n_steps_budget":750.0,"object_pos_end":[0.49752,0.04852,0.01602],"object_pos_start":[0.49752,0.04852,0.01602],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.1903,"object_z_max":0.01602,"peak_contact_force":222.06897,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9238.0,"raw_peak_contact_force":849.15617,"tcp_end":[0.49312,0.05163,0.19413],"tcp_start":[0.462,0.04399,0.18409],"tcp_to_object_dist_end":0.1782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":736.0,"n_steps_budget":1000.0,"object_pos_end":[0.49752,0.04852,0.01602],"object_pos_start":[0.49752,0.04852,0.01602],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.1903,"object_z_max":0.01602,"peak_contact_force":145.85238,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10654.0,"raw_peak_contact_force":305.36002,"subtask_id":"transport_arc","tcp_end":[0.53075,0.10348,0.22833],"tcp_start":[0.49312,0.05163,0.19413],"tcp_to_object_dist_end":0.22182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49752,0.04852,0.01602],"object_pos_start":[0.49752,0.04852,0.01602],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.1903,"object_z_max":0.01602,"peak_contact_force":189.12597,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1303.0,"raw_peak_contact_force":189.12597,"subtask_id":"release_1","tcp_end":[0.53201,0.10582,0.25452],"tcp_start":[0.53075,0.10348,0.22833],"tcp_to_object_dist_end":0.24771,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.77528,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01227,"descend_1.depth":0.03949,"grasp_1.grasp_duration":1.37048,"lift_1.speed":0.0765,"release_1.release_duration":2.30686,"transport.arc_height":0.02281,"transport.speed":0.048},"optimized_scores":{"best_composite_score":-0.33451,"best_fitness_score":0.13549,"best_task_score":0.1065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62917,-0.0017,-0.00047],"force_p95":194.32708,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1642.3474,"mean_force":200.06789,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38687,-0.00177,0.12241]},{"body_a":"world","body_b":"link6","contact_count":985.0,"contact_point_centroid":[0.62491,-0.00566,-0.00022],"force_p95":455.52351,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":913.19638,"mean_force":278.74852,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42516,-0.0089,0.1882]},{"body_a":"world","body_b":"link6","contact_count":448.0,"contact_point_centroid":[0.66597,-0.02293,-0.00013],"force_p95":76.48728,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.83889,"mean_force":70.72022,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46339,-0.02099,0.18291]},{"body_a":"link5","body_b":"hand","contact_count":568.0,"contact_point_centroid":[0.52719,0.0873,0.14828],"force_p95":129.21389,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.9753,"mean_force":34.96143,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.47697,-0.01901,0.15878]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.6661,-0.02298,-0.0001],"force_p95":133.69247,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.44712,"mean_force":104.02518,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46338,-0.02101,0.1828]},{"body_a":"link5","body_b":"hand","contact_count":146.0,"contact_point_centroid":[0.52271,0.07962,0.14267],"force_p95":67.50321,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.737,"mean_force":56.72112,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47567,-0.02743,0.15216]},{"body_a":"world","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.69972,0.02498,-5e-05],"force_p95":66.75339,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.12634,"mean_force":56.30598,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47605,-0.02348,0.15022]},{"body_a":"grasp_target","body_b":"link7","contact_count":294.0,"contact_point_centroid":[0.48806,-0.01536,0.03838],"force_p95":1.20193,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.31125,"mean_force":0.51303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38351,-0.00135,0.10287]},{"body_a":"grasp_target","body_b":"hand","contact_count":260.0,"contact_point_centroid":[0.48048,-0.02719,0.05368],"force_p95":2.26676,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.23436,"mean_force":0.52163,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38324,-0.00134,0.10071]},{"body_a":"world","body_b":"grasp_target","contact_count":3361.0,"contact_point_centroid":[0.47319,-0.01972,-0.00281],"force_p95":0.4118,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24921,"mean_force":0.19128,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40181,-0.00169,0.13531]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4625,-0.02115,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42566,-0.00902,0.18839]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4625,-0.02115,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46339,-0.02099,0.18291]},{"body_a":"world","body_b":"grasp_target","contact_count":2344.0,"contact_point_centroid":[0.4625,-0.02115,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45975,-0.0211,0.19042]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.4625,-0.02115,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.47,-0.01007,0.17469]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4625,-0.02115,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47596,-0.02623,0.15173]},{"body_a":"left_finger","body_b":"right_finger","contact_count":344.0,"contact_point_centroid":[0.46509,-0.02102,0.18139],"force_p95":0.01467,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01102,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46338,-0.02101,0.18279]}],"total_contact_groups":20},"final_pose_error":0.26357,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.4625,-0.02115,0.01602],"final_tcp_position":[0.48031,-0.02254,0.15975],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1642.3474,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4625,-0.02115,0.01602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.33595,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":191.35167,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4819.0,"raw_peak_contact_force":1642.3474,"subtask_id":"approach_1","tcp_end":[0.39108,-0.00254,0.14294],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14682,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4625,-0.02115,0.01602],"object_pos_start":[0.4625,-0.02115,0.01602],"object_to_goal_dist_end":0.33595,"object_to_goal_dist_start":0.33595,"object_z_max":0.01602,"peak_contact_force":375.70914,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4985.0,"raw_peak_contact_force":913.19638,"subtask_id":"descend_1","tcp_end":[0.46354,-0.02118,0.18412],"tcp_start":[0.39108,-0.00254,0.14294],"tcp_to_object_dist_end":0.16811,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4625,-0.02115,0.01602],"object_pos_start":[0.4625,-0.02115,0.01602],"object_to_goal_dist_end":0.33595,"object_to_goal_dist_start":0.33595,"object_z_max":0.01602,"peak_contact_force":68.8126,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2592.0,"raw_peak_contact_force":211.83889,"subtask_id":"grasp_1","tcp_end":[0.46338,-0.02101,0.18278],"tcp_start":[0.46354,-0.02118,0.18412],"tcp_to_object_dist_end":0.16677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":186.0,"n_steps_budget":600.0,"object_pos_end":[0.4625,-0.02115,0.01602],"object_pos_start":[0.4625,-0.02115,0.01602],"object_to_goal_dist_end":0.33595,"object_to_goal_dist_start":0.33595,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4820.0,"raw_peak_contact_force":136.44712,"tcp_end":[0.4586,-0.02111,0.19014],"tcp_start":[0.46338,-0.02101,0.18278],"tcp_to_object_dist_end":0.17417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4625,-0.02115,0.01602],"object_pos_start":[0.4625,-0.02115,0.01602],"object_to_goal_dist_end":0.33595,"object_to_goal_dist_start":0.33595,"object_z_max":0.01602,"peak_contact_force":2.12128,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12260.0,"raw_peak_contact_force":193.9753,"subtask_id":"transport_arc","tcp_end":[0.47786,-0.02286,0.15339],"tcp_start":[0.4586,-0.02111,0.19014],"tcp_to_object_dist_end":0.13823,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4625,-0.02115,0.01602],"object_pos_start":[0.4625,-0.02115,0.01602],"object_to_goal_dist_end":0.33595,"object_to_goal_dist_start":0.33595,"object_z_max":0.01602,"peak_contact_force":66.10944,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1238.0,"raw_peak_contact_force":69.737,"subtask_id":"release_1","tcp_end":[0.47488,-0.03673,0.15615],"tcp_start":[0.47786,-0.02286,0.15339],"tcp_to_object_dist_end":0.14153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```