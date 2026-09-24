## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.2468 | 0.15 | ❌ rejected |
| 4 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 2 | approach → descend → grasp → lift → push → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1013 | 0.25 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | -0.3188 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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

## Current Skill (Q=-0.247) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
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
  control: admittance_control
  termination: pose_tolerance
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
  control: position_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: -0.247
- **task_score** (E): 0.146
- **fitness_score**: 0.153  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1649 |
| descend_1 | 0.00 | 1.00 | 0.0730 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 1.00 | 0.0264 |
| transport_arc_1 | 0.00 | 1.00 | 0.0674 |
| descend_to_goal | 0.00 | 1.00 | 0.0613 |
| release_1 | 1.00 | 1.00 | 0.0220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.415, 0.011, 0.161) | (0.511, 0.022, 0.030)→(0.471, 0.025, 0.016) | 0.271→0.294 | 1.00 / 5.000 | 253.205 | 1575.996 |
| descend_1 | descend | 0.00 / step_budget | (0.415, 0.011, 0.161)→(0.461, 0.037, 0.185) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.294→0.294 | 1.00 / 5.000 | 362.882 | 915.725 |
| grasp_1 | grasp | 1.00 / step_budget | (0.461, 0.037, 0.184)→(0.461, 0.037, 0.184) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.294→0.294 | 1.00 / 9.667 | 182031.301 | 471.922 |
| lift_1 | lift | 0.67 / step_budget | (0.474, 0.034, 0.249)→(0.486, 0.021, 0.230) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.294→0.294 | 1.00 / 9.333 | 91098.023 | 674.554 |
| transport_arc_1 | approach | 0.00 / step_budget | (0.486, 0.021, 0.230)→(0.489, 0.029, 0.294) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.294→0.294 | 1.00 / 8.667 | 97.538 | 245.718 |
| descend_to_goal | descend | 0.00 / step_budget | (0.489, 0.029, 0.294)→(0.522, 0.070, 0.268) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.294→0.294 | 1.00 / 9.333 | 291.545 | 327.247 |
| release_1 | release | 1.00 / step_budget | (0.522, 0.070, 0.268)→(0.523, 0.073, 0.289) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.294→0.294 | 1.00 / 5.667 | 231.594 | 273.260 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.207
- phase_score: 0.172
- phase_breakdown.approach_1_score: 0.034
- phase_breakdown.descend_1_score: 0.045
- phase_breakdown.transport_arc_score: 0.019
- phase_breakdown.release_1_score: 0.035
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.179

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.179
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.207
- **Median Q (composite search score)**: -0.254
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.377


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":25.0,"average_failure_rate":0.16026,"average_mean_iterations":36.24359,"average_solve_count":156.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01437,"descend_to_goal.speed":0.06399,"lift_1.speed":0.03323,"transport_arc_1.arc_height":0.10588,"transport_arc_1.speed":0.03839},"optimized_scores":{"best_composite_score":-0.22101,"best_fitness_score":0.17899,"best_task_score":0.20653},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62945,0.00922,-0.00047],"force_p95":196.94328,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1636.11902,"mean_force":202.35369,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38849,0.00855,0.12478]},{"body_a":"world","body_b":"link6","contact_count":309.0,"contact_point_centroid":[0.6885,0.03924,-0.00017],"force_p95":478.07167,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1133.35754,"mean_force":270.14269,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47337,0.04933,0.1794]},{"body_a":"world","body_b":"link6","contact_count":983.0,"contact_point_centroid":[0.62112,0.0234,-0.00023],"force_p95":471.80003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":938.81429,"mean_force":289.69443,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42273,0.02498,0.19092]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.66285,0.04097,-0.00013],"force_p95":76.66822,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":592.00864,"mean_force":71.74416,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45894,0.04475,0.19471]},{"body_a":"link5","body_b":"hand","contact_count":57.0,"contact_point_centroid":[0.53779,0.00703,0.20676],"force_p95":323.8026,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.14114,"mean_force":302.80407,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.50843,0.0953,0.22213]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53357,0.00849,0.19487],"force_p95":254.93741,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.29018,"mean_force":235.92663,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51068,0.09722,0.22314]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.69612,0.04014,-0.00024],"force_p95":241.37607,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":246.72661,"mean_force":167.71302,"phase_index":4.0,"phase_name":"transport_arc_1","phase_type":"approach","tcp_position_centroid":[0.4759,0.05035,0.1753]},{"body_a":"grasp_target","body_b":"link7","contact_count":237.0,"contact_point_centroid":[0.48979,0.02383,0.04076],"force_p95":3.12919,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.08189,"mean_force":0.61794,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38351,0.00572,0.09956]},{"body_a":"grasp_target","body_b":"hand","contact_count":201.0,"contact_point_centroid":[0.48299,0.02528,0.05295],"force_p95":1.97051,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.67958,"mean_force":0.59694,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38291,0.0056,0.0966]},{"body_a":"world","body_b":"grasp_target","contact_count":3486.0,"contact_point_centroid":[0.48191,0.04686,-0.00255],"force_p95":0.36116,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32238,"mean_force":0.17338,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40284,0.00834,0.13706]},{"body_a":"grasp_target","body_b":"link6","contact_count":16.0,"contact_point_centroid":[0.52633,0.02675,0.00077],"force_p95":0.57622,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58097,"mean_force":0.45281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37096,0.00501,0.05779]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47275,0.04856,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42314,0.02515,0.1912]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.47275,0.04856,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45895,0.04475,0.19472]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.47275,0.04856,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4729,0.04917,0.17978]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47275,0.04856,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_arc_1","phase_type":"approach","tcp_position_centroid":[0.47539,0.05327,0.21953]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.47275,0.04856,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.50171,0.08766,0.23196]}],"total_contact_groups":23},"final_pose_error":0.15913,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.47275,0.04856,0.01602],"final_tcp_position":[0.51083,0.09594,0.22138],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.12067,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":195.58003,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4844.0,"raw_peak_contact_force":1636.11902,"subtask_id":"approach_1","tcp_end":[0.39437,0.01308,0.14815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15767,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.47275,0.04856,0.01602],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.2366,"object_z_max":0.01602,"peak_contact_force":354.59939,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4983.0,"raw_peak_contact_force":938.81429,"subtask_id":"descend_1","tcp_end":[0.45916,0.04482,0.196],"tcp_start":[0.39437,0.01308,0.14815],"tcp_to_object_dist_end":0.18054,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.47275,0.04856,0.01602],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.2366,"object_z_max":0.01602,"peak_contact_force":273004.12067,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":592.00864,"subtask_id":"grasp_1","tcp_end":[0.45894,0.04473,0.1946],"tcp_start":[0.45894,0.04473,0.19461],"tcp_to_object_dist_end":0.17916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":327.0,"n_steps_budget":600.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.47275,0.04856,0.01602],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.2366,"object_z_max":0.01602,"peak_contact_force":238.81282,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3025.0,"raw_peak_contact_force":1133.35754,"tcp_end":[0.47582,0.05006,0.17504],"tcp_start":[0.47606,0.05016,0.17575],"tcp_to_object_dist_end":0.15906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.47275,0.04856,0.01602],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.2366,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8364.0,"raw_peak_contact_force":246.72661,"subtask_id":"transport_arc","tcp_end":[0.49078,0.07554,0.25074],"tcp_start":[0.47582,0.05006,0.17504],"tcp_to_object_dist_end":0.23695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.47275,0.04856,0.01602],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.2366,"object_z_max":0.01602,"peak_contact_force":291.67441,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1460.0,"raw_peak_contact_force":327.14114,"tcp_end":[0.51083,0.09594,0.22138],"tcp_start":[0.49078,0.07554,0.25074],"tcp_to_object_dist_end":0.21417,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47275,0.04856,0.01602],"object_pos_start":[0.47275,0.04856,0.01602],"object_to_goal_dist_end":0.2366,"object_to_goal_dist_start":0.2366,"object_z_max":0.01602,"peak_contact_force":255.98516,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1223.0,"raw_peak_contact_force":277.29018,"subtask_id":"release_1","tcp_end":[0.51211,0.10064,0.24311],"tcp_start":[0.51083,0.09594,0.22138],"tcp_to_object_dist_end":0.23628,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.41818,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01551,"descend_to_goal.speed":0.05387,"lift_1.speed":0.04044,"transport_arc_1.arc_height":0.14476,"transport_arc_1.speed":0.02237},"optimized_scores":{"best_composite_score":-0.26517,"best_fitness_score":0.13483,"best_task_score":0.12395},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.6274,0.00939,-0.00048],"force_p95":198.14706,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1637.31948,"mean_force":203.6272,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38501,0.0087,0.12226]},{"body_a":"world","body_b":"link6","contact_count":985.0,"contact_point_centroid":[0.61768,0.0265,-0.00022],"force_p95":446.83195,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":895.26403,"mean_force":289.60692,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42052,0.0273,0.19166]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.65474,0.04745,-0.00013],"force_p95":80.11562,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":651.46394,"mean_force":73.88078,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45646,0.04833,0.20046]},{"body_a":"link5","body_b":"hand","contact_count":141.0,"contact_point_centroid":[0.54007,0.05645,0.2274],"force_p95":296.3815,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.3897,"mean_force":276.54793,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.50344,0.13083,0.2482]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.5381,0.0603,0.21375],"force_p95":224.62005,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.63593,"mean_force":189.1893,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50808,0.13604,0.24883]},{"body_a":"world","body_b":"link6","contact_count":1010.0,"contact_point_centroid":[0.6504,0.05608,-0.00027],"force_p95":228.92039,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.60309,"mean_force":206.05848,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45045,0.04874,0.18738]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.65357,0.05843,-0.0002],"force_p95":149.76432,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":162.1153,"mean_force":80.85232,"phase_index":4.0,"phase_name":"transport_arc_1","phase_type":"approach","tcp_position_centroid":[0.44635,0.04906,0.17726]},{"body_a":"grasp_target","body_b":"hand","contact_count":47.0,"contact_point_centroid":[0.46107,0.03385,0.04108],"force_p95":3.67116,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.05111,"mean_force":1.66316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37835,0.00501,0.06084]},{"body_a":"grasp_target","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.48272,0.02957,0.01653],"force_p95":2.33353,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.04656,"mean_force":0.72149,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3712,0.00495,0.05988]},{"body_a":"world","body_b":"grasp_target","contact_count":3883.0,"contact_point_centroid":[0.44678,0.04909,-0.00215],"force_p95":0.13842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48449,"mean_force":0.14147,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39781,0.00823,0.13231]},{"body_a":"left_finger","body_b":"link5","contact_count":60.0,"contact_point_centroid":[0.50394,0.09772,0.25464],"force_p95":0.63498,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.66343,"mean_force":0.58603,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5086,0.13789,0.25979]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44128,0.04908,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42082,0.02742,0.19194]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44128,0.04908,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45646,0.04833,0.20046]},{"body_a":"world","body_b":"grasp_target","contact_count":4040.0,"contact_point_centroid":[0.44128,0.04908,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45045,0.04874,0.18738]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44128,0.04908,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_arc_1","phase_type":"approach","tcp_position_centroid":[0.43591,0.03711,0.22887]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44128,0.04908,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.47676,0.09896,0.24651]}],"total_contact_groups":23},"final_pose_error":0.12071,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44128,0.04908,0.01602],"final_tcp_position":[0.50837,0.13456,0.24712],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273003.95419,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":197.56123,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4866.0,"raw_peak_contact_force":1637.31948,"subtask_id":"approach_1","tcp_end":[0.38913,0.01362,0.1426],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14142,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.44128,0.04908,0.01602],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.31318,"object_z_max":0.01602,"peak_contact_force":373.13389,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4985.0,"raw_peak_contact_force":895.26403,"subtask_id":"descend_1","tcp_end":[0.45666,0.04827,0.20157],"tcp_start":[0.38913,0.01362,0.1426],"tcp_to_object_dist_end":0.18619,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.44128,0.04908,0.01602],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.31318,"object_z_max":0.01602,"peak_contact_force":85.6624,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3502.0,"raw_peak_contact_force":651.46394,"subtask_id":"grasp_1","tcp_end":[0.45646,0.0483,0.20035],"tcp_start":[0.45646,0.04831,0.20035],"tcp_to_object_dist_end":0.18496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1010.0,"n_steps_budget":600.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.44128,0.04908,0.01602],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.31318,"object_z_max":0.01602,"peak_contact_force":273003.95419,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9284.0,"raw_peak_contact_force":247.60309,"tcp_end":[0.44648,0.04917,0.17709],"tcp_start":[0.44833,0.04906,0.18218],"tcp_to_object_dist_end":0.16116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.44128,0.04908,0.01602],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.31318,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8228.0,"raw_peak_contact_force":162.1153,"subtask_id":"transport_arc","tcp_end":[0.43738,0.03848,0.28107],"tcp_start":[0.44648,0.04917,0.17709],"tcp_to_object_dist_end":0.2653,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.44128,0.04908,0.01602],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.31318,"object_z_max":0.01602,"peak_contact_force":263.28574,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8444.0,"raw_peak_contact_force":319.3897,"tcp_end":[0.50837,0.13456,0.24712],"tcp_start":[0.43738,0.03848,0.28107],"tcp_to_object_dist_end":0.25537,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44128,0.04908,0.01602],"object_pos_start":[0.44128,0.04908,0.01602],"object_to_goal_dist_end":0.31318,"object_to_goal_dist_start":0.31318,"object_z_max":0.01602,"peak_contact_force":226.75213,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1286.0,"raw_peak_contact_force":250.63593,"subtask_id":"release_1","tcp_end":[0.50909,0.13928,0.2688],"tcp_start":[0.50837,0.13456,0.24712],"tcp_to_object_dist_end":0.27683,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":180.0,"average_failure_rate":0.65934,"average_mean_iterations":135.60806,"average_solve_count":273.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07015,"descend_to_goal.speed":0.02553,"lift_1.speed":0.07026,"transport_arc_1.arc_height":0.08865,"transport_arc_1.speed":0.05122},"optimized_scores":{"best_composite_score":-0.25429,"best_fitness_score":0.14571,"best_task_score":0.10832},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":879.0,"contact_point_centroid":[0.64094,0.00823,-0.00045],"force_p95":443.9019,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1454.54844,"mean_force":238.02716,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42535,0.00561,0.16326]},{"body_a":"world","body_b":"link6","contact_count":978.0,"contact_point_centroid":[0.64262,-0.00204,-0.00023],"force_p95":432.53946,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":913.0967,"mean_force":279.11768,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44438,0.00656,0.19174]},{"body_a":"link5","body_b":"hand","contact_count":802.0,"contact_point_centroid":[0.54268,0.0009,0.29882],"force_p95":406.46284,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":642.69991,"mean_force":325.891,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50193,-0.00367,0.34321]},{"body_a":"world","body_b":"link6","contact_count":76.0,"contact_point_centroid":[0.69585,-0.02654,-0.0001],"force_p95":452.21325,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":486.18708,"mean_force":326.12769,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47051,0.00812,0.15915]},{"body_a":"link5","body_b":"hand","contact_count":153.0,"contact_point_centroid":[0.54945,0.04988,0.39543],"force_p95":319.9346,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.20925,"mean_force":309.49277,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54494,-0.02103,0.33865]},{"body_a":"link5","body_b":"hand","contact_count":106.0,"contact_point_centroid":[0.55052,0.05606,0.37291],"force_p95":315.50022,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.31121,"mean_force":295.68506,"phase_index":4.0,"phase_name":"transport_arc_1","phase_type":"approach","tcp_position_centroid":[0.53697,-0.02937,0.34447]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.55023,0.04175,0.40163],"force_p95":290.25109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.85404,"mean_force":237.92858,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54859,-0.02148,0.33626]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.68675,-0.0167,-0.00013],"force_p95":73.87604,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.29475,"mean_force":69.23968,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4667,0.01828,0.15769]},{"body_a":"grasp_target","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.50944,-0.01683,0.03661],"force_p95":3.2954,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.78344,"mean_force":0.82276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39247,0.00377,0.09299]},{"body_a":"grasp_target","body_b":"link6","contact_count":108.0,"contact_point_centroid":[0.53994,-0.00321,0.0245],"force_p95":0.75897,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.19237,"mean_force":0.4425,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38812,0.00369,0.091]},{"body_a":"grasp_target","body_b":"hand","contact_count":111.0,"contact_point_centroid":[0.49397,-0.02726,0.04799],"force_p95":2.6186,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.40326,"mean_force":0.98645,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38983,0.00363,0.08404]},{"body_a":"world","body_b":"grasp_target","contact_count":3704.0,"contact_point_centroid":[0.50506,-0.02138,-0.00219],"force_p95":0.25408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.93839,"mean_force":0.1522,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43703,0.00538,0.17295]},{"body_a":"left_finger","body_b":"link5","contact_count":27.0,"contact_point_centroid":[0.52909,0.00669,0.37881],"force_p95":0.27489,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.27512,"mean_force":0.25399,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54917,-0.02196,0.35186]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49932,-0.02166,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4448,0.00658,0.19154]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49932,-0.02166,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4667,0.01828,0.15769]},{"body_a":"world","body_b":"grasp_target","contact_count":3484.0,"contact_point_centroid":[0.49932,-0.02166,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49937,-0.00262,0.32861]}],"total_contact_groups":25},"final_pose_error":0.28586,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49932,-0.02166,0.01602],"final_tcp_position":[0.5483,-0.02057,0.33471],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.121,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":366.47231,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4974.0,"raw_peak_contact_force":1454.54844,"subtask_id":"approach_1","tcp_end":[0.46199,0.00576,0.19226],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.49932,-0.02166,0.01602],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.3334,"object_z_max":0.01602,"peak_contact_force":360.91313,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4978.0,"raw_peak_contact_force":913.0967,"subtask_id":"descend_1","tcp_end":[0.46673,0.01801,0.15844],"tcp_start":[0.46199,0.00576,0.19226],"tcp_to_object_dist_end":0.15139,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.49932,-0.02166,0.01602],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.3334,"object_z_max":0.01602,"peak_contact_force":273004.121,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3546.0,"raw_peak_contact_force":172.29475,"subtask_id":"grasp_1","tcp_end":[0.46668,0.0183,0.15759],"tcp_start":[0.46668,0.01829,0.15759],"tcp_to_object_dist_end":0.15068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":871.0,"n_steps_budget":600.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.49932,-0.02166,0.01602],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.3334,"object_z_max":0.01602,"peak_contact_force":51.30228,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8197.0,"raw_peak_contact_force":642.69991,"tcp_end":[0.53542,-0.03611,0.33832],"tcp_start":[0.49885,0.00333,0.38759],"tcp_to_object_dist_end":0.32464,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.49932,-0.02166,0.01602],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.3334,"object_z_max":0.01602,"peak_contact_force":292.37005,"phase_name":"transport_arc_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1001.0,"raw_peak_contact_force":328.31121,"subtask_id":"transport_arc","tcp_end":[0.53893,-0.02564,0.34999],"tcp_start":[0.53542,-0.03611,0.33832],"tcp_to_object_dist_end":0.33633,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":153.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.49932,-0.02166,0.01602],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.3334,"object_z_max":0.01602,"peak_contact_force":319.67435,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1453.0,"raw_peak_contact_force":335.20925,"tcp_end":[0.5483,-0.02057,0.33471],"tcp_start":[0.53893,-0.02564,0.34999],"tcp_to_object_dist_end":0.32244,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49932,-0.02166,0.01602],"object_pos_start":[0.49932,-0.02166,0.01602],"object_to_goal_dist_end":0.3334,"object_to_goal_dist_start":0.3334,"object_z_max":0.01602,"peak_contact_force":212.04447,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1252.0,"raw_peak_contact_force":291.85404,"subtask_id":"release_1","tcp_end":[0.5492,-0.02197,0.35615],"tcp_start":[0.5483,-0.02057,0.33471],"tcp_to_object_dist_end":0.34376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```