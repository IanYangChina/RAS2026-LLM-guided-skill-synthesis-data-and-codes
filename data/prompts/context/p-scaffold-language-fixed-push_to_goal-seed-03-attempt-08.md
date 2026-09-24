## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 4 | 0.2665 | 0.04 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4540 | 0.64 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4710 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.4194 | 0.05 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.267) — your mutation base

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

- **Composite score**: 0.267
- **task_score** (E): 0.044
- **fitness_score**: 0.277  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2842 |
| contact_1 | 1.00 | 1.00 | 0.0452 |
| push_1 | 1.00 | 1.00 | 0.0016 |
| retract_1 | 1.00 | 1.00 | 0.1639 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.034, 0.020) | (0.513, 0.002, 0.025)→(0.515, -0.002, 0.025) | 0.160→0.155 | 1.00 / 3.000 | 2.486 | 7.675 |
| push_1 | push | 1.00 / force_exceeded | (0.509, 0.034, 0.020)→(0.508, 0.033, 0.020) | (0.515, -0.002, 0.025)→(0.514, -0.004, 0.025) | 0.155→0.154 | 1.00 / 4.333 | 22.476 | 23.228 |
| retract_1 | retract | 1.00 / step_budget | (0.508, 0.033, 0.020)→(0.505, 0.033, 0.183) | (0.514, -0.004, 0.025)→(0.513, -0.005, 0.025) | 0.154→0.153 | 1.00 / 4.000 | 0.245 | 20.521 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.043
- lateral_force_integral: None
- approach_alignment: 0.412
- goal_progress: 0.042
- terminal_score: 0.042
- phase_score: 0.446
- phase_breakdown.contact_score: 0.833
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.065

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.285
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.048
- **Median Q (composite search score)**: 0.265
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.251


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7013,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07175,"contact_1.speed":0.03079,"push_1.force_threshold":17.74873,"push_1.push_depth":0.06432},"optimized_scores":{"best_composite_score":0.27452,"best_fitness_score":0.28452,"best_task_score":0.04173},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.47621,-0.01097,0.04997],"force_p95":25.40298,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.01186,"mean_force":17.42933,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44623,0.00079,0.02143]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.44304,-0.03339,-2e-05],"force_p95":20.16159,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.47376,"mean_force":10.98099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44623,0.00079,0.02142]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47603,-0.02138,0.04997],"force_p95":16.72898,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.18967,"mean_force":8.25493,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44603,0.00053,0.02139]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.45092,-0.01114,0.02856],"force_p95":15.5841,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.64031,"mean_force":12.62344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44623,0.00079,0.02143]},{"body_a":"world","body_b":"push_box","contact_count":3967.0,"contact_point_centroid":[0.45107,-0.037,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.37034,"mean_force":0.26162,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44311,0.00056,0.10421]},{"body_a":"attachment","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.45246,-0.00874,0.03156],"force_p95":6.4277,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.18528,"mean_force":3.29184,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44613,0.00317,0.02192]},{"body_a":"world","body_b":"push_box","contact_count":3234.0,"contact_point_centroid":[0.45019,-0.03233,-1e-05],"force_p95":0.85278,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.75357,"mean_force":0.34726,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44574,0.02261,0.026]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.45007,-0.01134,0.02705],"force_p95":5.51442,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.65568,"mean_force":4.24307,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44626,0.00062,0.02131]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47616,-0.0108,0.05004],"force_p95":2.78575,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.79656,"mean_force":2.68233,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44623,0.00092,0.02148]},{"body_a":"world","body_b":"push_box","contact_count":3508.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47378,0.02259,0.16682]}],"total_contact_groups":10},"final_pose_error":0.0347,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45123,-0.037,0.02499],"final_tcp_position":[0.44346,0.00059,0.18674],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":27.01186,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3508.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.4489,0.04565,0.03438],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":852.0,"n_steps_budget":990.0,"object_pos_end":[0.45138,-0.03604,0.025],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.1239,"object_to_goal_dist_start":0.12843,"object_z_max":0.02505,"peak_contact_force":3.30232,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3336.0,"raw_peak_contact_force":10.18528,"subtask_id":"contact","tcp_end":[0.44623,0.00084,0.02147],"tcp_start":[0.4489,0.04565,0.03438],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.45142,-0.03628,0.02496],"object_pos_start":[0.45138,-0.03604,0.025],"object_to_goal_dist_end":0.12366,"object_to_goal_dist_start":0.1239,"object_z_max":0.025,"peak_contact_force":27.01186,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":17.0,"raw_peak_contact_force":27.01186,"subtask_id":"push","tcp_end":[0.44626,0.00064,0.02133],"tcp_start":[0.44623,0.00084,0.02147],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45123,-0.037,0.02499],"object_pos_start":[0.45142,-0.03628,0.02496],"object_to_goal_dist_end":0.12307,"object_to_goal_dist_start":0.12366,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3976.0,"raw_peak_contact_force":17.18967,"tcp_end":[0.44346,0.00059,0.18674],"tcp_start":[0.44626,0.00064,0.02133],"tcp_to_object_dist_end":0.16624,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68613,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0898,"contact_1.speed":0.03127,"push_1.force_threshold":12.96653,"push_1.push_depth":0.11434},"optimized_scores":{"best_composite_score":0.26535,"best_fitness_score":0.27535,"best_task_score":0.0478},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.55842,0.02106,0.04905],"force_p95":18.04574,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.2572,"mean_force":11.80009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54781,0.03305,0.01919]},{"body_a":"world","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.56566,-0.01565,-5e-05],"force_p95":9.49654,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.79174,"mean_force":3.44765,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5476,0.03285,0.01905]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.55762,0.01989,0.04991],"force_p95":7.83375,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.98674,"mean_force":2.96426,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54623,0.03186,0.01877]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.57643,0.01266,0.05058],"force_p95":5.63843,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.97934,"mean_force":1.2918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54608,0.03171,0.0185]},{"body_a":"attachment","body_b":"push_box","contact_count":101.0,"contact_point_centroid":[0.55409,0.02412,0.03737],"force_p95":6.51688,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.37865,"mean_force":2.45038,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54794,0.0361,0.01991]},{"body_a":"world","body_b":"push_box","contact_count":3938.0,"contact_point_centroid":[0.55151,-0.00606,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.88668,"mean_force":0.25584,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54334,0.03182,0.09922]},{"body_a":"world","body_b":"push_box","contact_count":3016.0,"contact_point_centroid":[0.55325,0.00013,-1e-05],"force_p95":0.62836,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.61824,"mean_force":0.33111,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54536,0.05555,0.02287]},{"body_a":"world","body_b":"push_box","contact_count":3852.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03843,0.1645]}],"total_contact_groups":8},"final_pose_error":0.03758,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55148,-0.00618,0.02499],"final_tcp_position":[0.54395,0.03189,0.1811],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":18.2572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54657,0.07719,0.0312],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":814.0,"n_steps_budget":930.0,"object_pos_end":[0.55438,-0.00334,0.0251],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15641,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":3.632,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3117.0,"raw_peak_contact_force":7.37865,"subtask_id":"contact","tcp_end":[0.5483,0.03355,0.01955],"tcp_start":[0.54657,0.07719,0.0312],"tcp_to_object_dist_end":0.0378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.55312,-0.00486,0.02483],"object_pos_start":[0.55438,-0.00334,0.0251],"object_to_goal_dist_end":0.15456,"object_to_goal_dist_start":0.15641,"object_z_max":0.02526,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":18.2572,"subtask_id":"push","tcp_end":[0.54692,0.03212,0.01856],"tcp_start":[0.5483,0.03355,0.01955],"tcp_to_object_dist_end":0.03801,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55148,-0.00618,0.02499],"object_pos_start":[0.55312,-0.00486,0.02483],"object_to_goal_dist_end":0.15276,"object_to_goal_dist_start":0.15456,"object_z_max":0.02532,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3953.0,"raw_peak_contact_force":8.98674,"tcp_end":[0.54395,0.03189,0.1811],"tcp_start":[0.54692,0.03212,0.01856],"tcp_to_object_dist_end":0.16086,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55072,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09592,"contact_1.speed":0.028,"push_1.force_threshold":23.99113,"push_1.push_depth":0.07466},"optimized_scores":{"best_composite_score":0.25963,"best_fitness_score":0.26963,"best_task_score":0.0439},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.56212,0.04554,0.04981],"force_p95":29.58011,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.38661,"mean_force":7.14346,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53024,0.06693,0.01882]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.5625,0.05311,0.04991],"force_p95":24.06234,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.41595,"mean_force":20.49549,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53079,0.06757,0.01893]},{"body_a":"world","body_b":"push_box","contact_count":3970.0,"contact_point_centroid":[0.5358,0.02857,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.0604,"mean_force":0.26483,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52709,0.06665,0.09999]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.54235,0.05628,0.04767],"force_p95":16.24611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.76311,"mean_force":8.66774,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53127,0.06823,0.01932]},{"body_a":"world","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.53569,0.02456,-9e-05],"force_p95":17.7544,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.79237,"mean_force":6.33288,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53113,0.06807,0.01921]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.54282,0.0551,0.05008],"force_p95":11.03063,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.12343,"mean_force":3.33851,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53034,0.06697,0.01875]},{"body_a":"attachment","body_b":"push_box","contact_count":118.0,"contact_point_centroid":[0.53736,0.05949,0.03534],"force_p95":4.93306,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.46029,"mean_force":1.99698,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5315,0.07146,0.02011]},{"body_a":"world","body_b":"push_box","contact_count":3291.0,"contact_point_centroid":[0.53671,0.03571,-1e-05],"force_p95":0.67973,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.86343,"mean_force":0.32019,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52933,0.09001,0.02279]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.03634,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53578,0.02859,0.02499],"final_tcp_position":[0.52758,0.06673,0.18253],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":35.38661,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53088,0.11128,0.03074],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.53828,0.03212,0.02505],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1861,"object_to_goal_dist_start":0.1905,"object_z_max":0.02506,"peak_contact_force":0.52329,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3409.0,"raw_peak_contact_force":5.46029,"subtask_id":"contact","tcp_end":[0.53184,0.06897,0.0198],"tcp_start":[0.53088,0.11128,0.03074],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.53802,0.03045,0.02489],"object_pos_start":[0.53828,0.03212,0.02505],"object_to_goal_dist_end":0.18441,"object_to_goal_dist_start":0.1861,"object_z_max":0.02508,"peak_contact_force":24.41595,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":57.0,"raw_peak_contact_force":24.41595,"subtask_id":"push","tcp_end":[0.53057,0.06715,0.01875],"tcp_start":[0.53184,0.06897,0.0198],"tcp_to_object_dist_end":0.03795,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53578,0.02859,0.02499],"object_pos_start":[0.53802,0.03045,0.02489],"object_to_goal_dist_end":0.18214,"object_to_goal_dist_start":0.18441,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3986.0,"raw_peak_contact_force":35.38661,"tcp_end":[0.52758,0.06673,0.18253],"tcp_start":[0.53057,0.06715,0.01875],"tcp_to_object_dist_end":0.1623,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```