## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.4194 | 0.05 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4714 | 0.74 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4584 | 0.64 | ✅ accepted |

**Proposal policy**: task_score is 0.05 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.419) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.419
- **task_score** (E): 0.053
- **fitness_score**: 0.041  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1552 |
| contact_1 | 0.00 | 1.00 | 0.0002 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| lift_1 | 0.00 | 1.00 | 0.0761 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, 0.069, 0.165) | (0.513, 0.002, 0.025)→(0.457, -0.007, 0.025) | 0.160→0.158 | 1.00 / 4.333 | 2747.130 | 1014.974 |
| contact_1 | contact | 0.00 / guard_failure | (0.491, 0.069, 0.165)→(0.491, 0.069, 0.165) | (0.457, -0.007, 0.025)→(0.457, -0.007, 0.025) | 0.158→0.158 | 1.00 / 5.000 | 219.004 | 269.820 |
| push_1 | push | 0.00 / guard_failure | (0.491, 0.070, 0.165)→(0.491, 0.070, 0.165) | (0.457, -0.007, 0.025)→(0.457, -0.007, 0.025) | 0.158→0.158 | 1.00 / 5.000 | 214.304 | 220.523 |
| lift_1 | lift | 0.00 / step_budget | (0.491, 0.070, 0.165)→(0.438, 0.101, 0.168) | (0.457, -0.007, 0.025)→(0.452, -0.011, 0.025) | 0.158→0.154 | 1.00 / 4.667 | 86.919 | 319.963 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.521
- lateral_force_integral: None
- approach_alignment: 0.321
- goal_progress: 0.133
- terminal_score: 0.133
- phase_score: 0.025
- phase_breakdown.contact_score: 0.041
- phase_breakdown.approach_score: 0.039
- phase_breakdown.push_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.068
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.133
- **Median Q (composite search score)**: -0.429
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.294


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.73611,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14437,"approach_1.approach_tolerance":0.01051,"contact_1.contact_force_threshold":7.17544,"contact_1.contact_speed":0.03585,"lift_1.lift_speed":0.0756,"push_1.push_distance":0.06703,"push_1.push_speed":0.07625,"push_1.push_tolerance":0.0471},"optimized_scores":{"best_composite_score":-0.43761,"best_fitness_score":0.02239,"best_task_score":0.02543},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":827.0,"contact_point_centroid":[0.55085,0.02388,-0.00013],"force_p95":645.27143,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":768.31109,"mean_force":356.05814,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43762,0.02317,0.18306]},{"body_a":"world","body_b":"link6","contact_count":386.0,"contact_point_centroid":[0.51338,0.0555,-8e-05],"force_p95":279.36284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.38469,"mean_force":202.03308,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42693,0.04656,0.20295]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56919,0.04192,-2e-05],"force_p95":274.32253,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.41396,"mean_force":246.06599,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46405,0.04675,0.19048]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.46615,-0.00584,0.05011],"force_p95":251.99341,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":254.69238,"mean_force":107.95915,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41069,0.00614,0.10729]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56893,0.04243,-4e-05],"force_p95":230.68679,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.74837,"mean_force":229.89336,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46381,0.04704,0.19046]},{"body_a":"world","body_b":"push_box","contact_count":3672.0,"contact_point_centroid":[0.41196,-0.06249,-4e-05],"force_p95":0.24971,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":229.99762,"mean_force":0.76729,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44769,0.02191,0.18716]},{"body_a":"world","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.40661,-0.06666,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46407,0.04667,0.1905]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.40661,-0.06666,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46381,0.04704,0.19046]},{"body_a":"world","body_b":"push_box","contact_count":2664.0,"contact_point_centroid":[0.40661,-0.06666,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.42096,0.04677,0.20771]}],"total_contact_groups":9},"final_pose_error":0.08403,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.40661,-0.06666,0.02499],"final_tcp_position":[0.40685,0.04759,0.22854],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":3994.77202,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.40661,-0.06666,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12517,"object_to_goal_dist_start":0.12843,"object_z_max":0.03494,"peak_contact_force":3994.77202,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4516.0,"raw_peak_contact_force":768.31109,"subtask_id":"approach","tcp_end":[0.46415,0.04643,0.19055],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20859,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.40661,-0.06666,0.02499],"object_pos_start":[0.40661,-0.06666,0.02499],"object_to_goal_dist_end":0.12517,"object_to_goal_dist_start":0.12517,"object_z_max":0.02499,"peak_contact_force":222.28432,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":19.0,"raw_peak_contact_force":278.41396,"subtask_id":"contact","tcp_end":[0.4639,0.04697,0.19046],"tcp_start":[0.46398,0.04688,0.19046],"tcp_to_object_dist_end":0.20874,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.40661,-0.06666,0.02499],"object_pos_start":[0.40661,-0.06666,0.02499],"object_to_goal_dist_end":0.12517,"object_to_goal_dist_start":0.12517,"object_z_max":0.02499,"peak_contact_force":228.79912,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":230.74837,"subtask_id":"push","tcp_end":[0.46363,0.04717,0.19048],"tcp_start":[0.46373,0.04711,0.19047],"tcp_to_object_dist_end":0.20879,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":666.0,"n_steps_budget":840.0,"object_pos_end":[0.40661,-0.06666,0.02499],"object_pos_start":[0.40661,-0.06666,0.02499],"object_to_goal_dist_end":0.12517,"object_to_goal_dist_start":0.12517,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3050.0,"raw_peak_contact_force":328.38469,"tcp_end":[0.40685,0.04759,0.22854],"tcp_start":[0.46363,0.04717,0.19048],"tcp_to_object_dist_end":0.23342,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.02299,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06836,"approach_1.approach_tolerance":0.04273,"contact_1.contact_force_threshold":3.92182,"contact_1.contact_speed":0.03198,"lift_1.lift_speed":0.05525,"push_1.push_distance":0.13814,"push_1.push_speed":0.05406,"push_1.push_tolerance":0.02941},"optimized_scores":{"best_composite_score":-0.39152,"best_fitness_score":0.06848,"best_task_score":0.13306},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":598.0,"contact_point_centroid":[0.58748,0.01891,-9e-05],"force_p95":776.21237,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":927.19563,"mean_force":539.6143,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47474,0.02778,0.18542]},{"body_a":"push_box","body_b":"link6","contact_count":356.0,"contact_point_centroid":[0.5316,0.01032,0.04836],"force_p95":272.06665,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":513.73118,"mean_force":177.62088,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.451,0.01441,0.17956]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.62647,0.03434,-0.00017],"force_p95":290.41078,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.91146,"mean_force":282.06796,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4942,0.04611,0.17214]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.62589,0.03499,-0.00028],"force_p95":278.41884,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.46986,"mean_force":270.39693,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49378,0.0466,0.17203]},{"body_a":"world","body_b":"link6","contact_count":845.0,"contact_point_centroid":[0.57691,0.03702,-0.00011],"force_p95":229.63463,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.10898,"mean_force":196.61706,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44378,0.07311,0.16301]},{"body_a":"world","body_b":"push_box","contact_count":3747.0,"contact_point_centroid":[0.5,0.00079,-9e-05],"force_p95":98.50585,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":170.64176,"mean_force":17.16188,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47393,0.022,0.18512]},{"body_a":"push_box","body_b":"link6","contact_count":108.0,"contact_point_centroid":[0.49512,0.02248,0.05005],"force_p95":13.59008,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.48723,"mean_force":3.1737,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43564,0.07918,0.17716]},{"body_a":"world","body_b":"push_box","contact_count":3273.0,"contact_point_centroid":[0.48523,-0.00276,-4e-05],"force_p95":0.55446,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.40292,"mean_force":0.36624,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44443,0.07266,0.16271]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53085,0.00867,0.04916],"force_p95":32.13547,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.76053,"mean_force":17.03441,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43943,0.00751,0.09859]},{"body_a":"world","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.48762,-0.00047,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49431,0.04589,0.17224]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.48762,-0.00047,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49378,0.0466,0.17203]}],"total_contact_groups":11},"final_pose_error":0.10283,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.471,-0.01398,0.02463],"final_tcp_position":[0.43507,0.0788,0.19369],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":3994.77202,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48762,-0.00047,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.15004,"object_to_goal_dist_start":0.16043,"object_z_max":0.02515,"peak_contact_force":3994.77202,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4705.0,"raw_peak_contact_force":927.19563,"subtask_id":"approach","tcp_end":[0.4945,0.04546,0.17242],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15457,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.48762,-0.00047,0.02499],"object_pos_start":[0.48762,-0.00047,0.02499],"object_to_goal_dist_end":0.15004,"object_to_goal_dist_start":0.15004,"object_z_max":0.02499,"peak_contact_force":285.9047,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":23.0,"raw_peak_contact_force":290.91146,"subtask_id":"contact","tcp_end":[0.49392,0.04645,0.17203],"tcp_start":[0.49406,0.0463,0.17207],"tcp_to_object_dist_end":0.15448,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48762,-0.00047,0.02499],"object_pos_start":[0.48762,-0.00047,0.02499],"object_to_goal_dist_end":0.15004,"object_to_goal_dist_start":0.15004,"object_z_max":0.02499,"peak_contact_force":262.76124,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":279.46986,"subtask_id":"push","tcp_end":[0.49347,0.04688,0.17207],"tcp_start":[0.49363,0.04674,0.17204],"tcp_to_object_dist_end":0.15462,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":908.0,"n_steps_budget":1000.0,"object_pos_end":[0.471,-0.01398,0.02463],"object_pos_start":[0.48762,-0.00047,0.02499],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.15004,"object_z_max":0.02589,"peak_contact_force":57.53532,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4226.0,"raw_peak_contact_force":277.10898,"tcp_end":[0.43507,0.0788,0.19369],"tcp_start":[0.49347,0.04688,0.17207],"tcp_to_object_dist_end":0.19616,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.02273,"average_mean_iterations":13.23864,"average_solve_count":88.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11109,"approach_1.approach_tolerance":0.02999,"contact_1.contact_force_threshold":7.58393,"contact_1.contact_speed":0.02157,"lift_1.lift_speed":0.04985,"push_1.push_distance":0.0973,"push_1.push_speed":0.0447,"push_1.push_tolerance":0.02292},"optimized_scores":{"best_composite_score":-0.42904,"best_fitness_score":0.03096,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":658.0,"contact_point_centroid":[0.59604,0.03952,-0.00017],"force_p95":845.38383,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.41483,"mean_force":531.3778,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47661,0.04893,0.17898]},{"body_a":"push_box","body_b":"link6","contact_count":141.0,"contact_point_centroid":[0.52252,0.02235,0.04869],"force_p95":341.4652,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":426.45735,"mean_force":156.87471,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4372,0.01469,0.16057]},{"body_a":"world","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.64972,0.09233,-0.0001],"force_p95":253.66401,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":354.39625,"mean_force":225.99201,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48658,0.16614,0.09596]},{"body_a":"world","body_b":"push_box","contact_count":3769.0,"contact_point_centroid":[0.48572,0.04547,-5e-05],"force_p95":48.0608,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":271.58444,"mean_force":6.16213,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48081,0.04561,0.17789]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.67627,0.09599,-0.00047],"force_p95":232.87884,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.13412,"mean_force":185.51271,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51424,0.11433,0.13178]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.67839,0.08476,-0.00024],"force_p95":150.64988,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.35042,"mean_force":146.11674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51444,0.11469,0.1326]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.52261,0.01707,0.04864],"force_p95":33.67688,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.46523,"mean_force":9.33721,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43425,0.01111,0.10356]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.4773,0.04758,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51424,0.11433,0.13178]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.4773,0.04758,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51444,0.11469,0.1326]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.4773,0.04758,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48663,0.16601,0.09601]}],"total_contact_groups":10},"final_pose_error":0.16826,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4773,0.04758,0.02499],"final_tcp_position":[0.47212,0.17557,0.08206],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":1349.41483,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4773,0.04758,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19888,"object_to_goal_dist_start":0.1905,"object_z_max":0.02612,"peak_contact_force":251.8445,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4579.0,"raw_peak_contact_force":1349.41483,"subtask_id":"approach","tcp_end":[0.51417,0.11425,0.13156],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.131,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4773,0.04758,0.02499],"object_pos_start":[0.4773,0.04758,0.02499],"object_to_goal_dist_end":0.19888,"object_to_goal_dist_start":0.19888,"object_z_max":0.02499,"peak_contact_force":148.8227,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":240.13412,"subtask_id":"contact","tcp_end":[0.51437,0.11454,0.1323],"tcp_start":[0.51431,0.11442,0.13202],"tcp_to_object_dist_end":0.13181,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4773,0.04758,0.02499],"object_pos_start":[0.4773,0.04758,0.02499],"object_to_goal_dist_end":0.19888,"object_to_goal_dist_start":0.19888,"object_z_max":0.02499,"peak_contact_force":151.35042,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":151.35042,"subtask_id":"push","tcp_end":[0.51455,0.11499,0.1332],"tcp_start":[0.51451,0.11484,0.13291],"tcp_to_object_dist_end":0.13282,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.4773,0.04758,0.02499],"object_pos_start":[0.4773,0.04758,0.02499],"object_to_goal_dist_end":0.19888,"object_to_goal_dist_start":0.19888,"object_z_max":0.02499,"peak_contact_force":202.97646,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4983.0,"raw_peak_contact_force":354.39625,"tcp_end":[0.47212,0.17557,0.08206],"tcp_start":[0.51455,0.11499,0.1332],"tcp_to_object_dist_end":0.14024,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```