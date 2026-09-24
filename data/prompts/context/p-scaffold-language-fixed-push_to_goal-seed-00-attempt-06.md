## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6468 | 0.90 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7965 | 0.91 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5286 | 0.76 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0519 | 0.08 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.3752 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.90 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

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

## Current Skill (Q=0.647) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
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

- **Composite score**: 0.647
- **task_score** (E): 0.900
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2213 |
| contact_1 | 1.00 | 1.00 | 0.0800 |
| push_1 | 1.00 | 1.00 | 0.1400 |
| retract_1 | 1.00 | 1.00 | 0.0955 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.080, 0.099) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.080, 0.099)→(0.492, 0.038, 0.032) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 18.262 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.492, 0.038, 0.032)→(0.497, -0.101, 0.021) | (0.496, 0.001, 0.025)→(0.507, -0.136, 0.026) | 0.152→0.017 | 1.00 / 2.667 | 21.180 | 47.350 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.101, 0.021)→(0.493, -0.100, 0.116) | (0.507, -0.136, 0.026)→(0.507, -0.140, 0.025) | 0.017→0.014 | 1.00 / 4.000 | 0.245 | 2.194 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.722
- goal_progress: 0.986
- terminal_score: 0.986
- phase_score: 0.662
- phase_breakdown.approach_score: 0.272
- phase_breakdown.contact_score: 0.763
- phase_breakdown.push_score: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.792
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.631
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.468


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0505,"contact_1.contact_force":3.48176,"push_1.push_speed":0.05779,"push_1.push_tolerance":0.02941,"retract_1.retract_height":0.18565},"optimized_scores":{"best_composite_score":0.578,"best_fitness_score":0.638,"best_task_score":0.77867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":125.0,"contact_point_centroid":[0.50902,-0.04657,0.03549],"force_p95":11.88125,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.03032,"mean_force":3.62527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50527,-0.03479,0.02374]},{"body_a":"world","body_b":"push_box","contact_count":137.0,"contact_point_centroid":[0.51925,-0.08618,-6e-05],"force_p95":11.81396,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.9827,"mean_force":3.97506,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50557,-0.03286,0.02397]},{"body_a":"world","body_b":"push_box","contact_count":3927.0,"contact_point_centroid":[0.51932,-0.13074,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36873,"mean_force":0.25074,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49593,-0.09078,0.10197]},{"body_a":"world","body_b":"push_box","contact_count":2940.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50471,0.03887,0.19628]},{"body_a":"world","body_b":"push_box","contact_count":1932.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51033,0.03116,0.05406]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50269,-0.10281,0.02018],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49926,-0.09144,0.02096]}],"total_contact_groups":6},"final_pose_error":0.02502,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51924,-0.13059,0.02499],"final_tcp_position":[0.49633,-0.09075,0.18178],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":46.03032,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2940.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51194,0.05355,0.0841],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":21.91276,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51169,0.00934,0.02829],"tcp_start":[0.51194,0.05355,0.0841],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.51867,-0.12441,0.02706],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.03174,"object_to_goal_dist_start":0.12347,"object_z_max":0.02749,"peak_contact_force":1.29863,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":262.0,"raw_peak_contact_force":46.03032,"subtask_id":"push","tcp_end":[0.4993,-0.09121,0.02097],"tcp_start":[0.51169,0.00934,0.02829],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51924,-0.13059,0.02499],"object_pos_start":[0.51867,-0.12441,0.02706],"object_to_goal_dist_end":0.02733,"object_to_goal_dist_start":0.03174,"object_z_max":0.02741,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3929.0,"raw_peak_contact_force":2.36873,"tcp_end":[0.49633,-0.09075,0.18178],"tcp_start":[0.4993,-0.09121,0.02097],"tcp_to_object_dist_end":0.16339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90141,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08942,"contact_1.contact_force":14.99142,"push_1.push_speed":0.08111,"push_1.push_tolerance":0.02306,"retract_1.retract_height":0.06927},"optimized_scores":{"best_composite_score":0.63051,"best_fitness_score":0.69051,"best_task_score":0.93508},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":289.0,"contact_point_centroid":[0.4981,-0.01923,0.03772],"force_p95":43.62849,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.29425,"mean_force":6.564,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49535,-0.00744,0.02717]},{"body_a":"world","body_b":"push_box","contact_count":411.0,"contact_point_centroid":[0.49999,-0.05064,-0.0001],"force_p95":22.00735,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.24941,"mean_force":5.15826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49538,-0.00308,0.02754]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.50269,-0.10985,0.04651],"force_p95":2.09034,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.78177,"mean_force":0.50945,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49629,-0.09821,0.02171]},{"body_a":"world","body_b":"push_box","contact_count":1938.0,"contact_point_centroid":[0.50399,-0.13739,-2e-05],"force_p95":0.24544,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57266,"mean_force":0.25138,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49302,-0.09721,0.0519]},{"body_a":"world","body_b":"push_box","contact_count":3112.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49839,0.07288,0.2207]},{"body_a":"world","body_b":"push_box","contact_count":1988.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49626,0.11004,0.07791]}],"total_contact_groups":6},"final_pose_error":0.01028,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50391,-0.13734,0.02499],"final_tcp_position":[0.49297,-0.09709,0.0813],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":68.29425,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3112.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49825,0.12947,0.12266],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":497.0,"n_steps_budget":690.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":15.4293,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49695,0.09101,0.03673],"tcp_start":[0.49825,0.12947,0.12266],"tcp_to_object_dist_end":0.03903,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.50435,-0.13355,0.02519],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.01702,"object_to_goal_dist_start":0.20406,"object_z_max":0.02649,"peak_contact_force":51.65225,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":700.0,"raw_peak_contact_force":68.29425,"subtask_id":"push","tcp_end":[0.49653,-0.09768,0.02166],"tcp_start":[0.49695,0.09101,0.03673],"tcp_to_object_dist_end":0.03688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.50391,-0.13734,0.02499],"object_pos_start":[0.50435,-0.13355,0.02519],"object_to_goal_dist_end":0.01325,"object_to_goal_dist_start":0.01702,"object_z_max":0.0255,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1945.0,"raw_peak_contact_force":2.78177,"tcp_end":[0.49297,-0.09709,0.0813],"tcp_start":[0.49653,-0.09768,0.02166],"tcp_to_object_dist_end":0.07008,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97573,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05533,"contact_1.contact_force":13.44963,"push_1.push_speed":0.02158,"push_1.push_tolerance":0.00996,"retract_1.retract_height":0.07594},"optimized_scores":{"best_composite_score":0.73175,"best_fitness_score":0.79175,"best_task_score":0.98619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":852.0,"contact_point_centroid":[0.48347,-0.06654,0.03565],"force_p95":14.65651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.72687,"mean_force":4.2681,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48052,-0.05462,0.02326]},{"body_a":"world","body_b":"push_box","contact_count":1557.0,"contact_point_centroid":[0.48478,-0.10426,-4e-05],"force_p95":7.93947,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.30142,"mean_force":2.679,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48067,-0.05503,0.0233]},{"body_a":"world","body_b":"push_box","contact_count":1999.0,"contact_point_centroid":[0.49856,-0.15095,-1e-05],"force_p95":0.24545,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43104,"mean_force":0.24831,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49116,-0.11237,0.05311]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49474,-0.125,0.02043],"force_p95":1.24994,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.25339,"mean_force":1.2189,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,-0.11303,0.02046]},{"body_a":"world","body_b":"push_box","contact_count":2828.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4849,0.0401,0.19936]},{"body_a":"world","body_b":"push_box","contact_count":1928.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46729,0.03451,0.05816]}],"total_contact_groups":6},"final_pose_error":0.01077,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49847,-0.15092,0.02499],"final_tcp_position":[0.49108,-0.11231,0.08628],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":27.72687,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2828.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46993,0.05676,0.09],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":17.44518,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46743,0.01274,0.02993],"tcp_start":[0.46993,0.05676,0.09],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.49898,-0.1499,0.02509],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00103,"object_to_goal_dist_start":0.12903,"object_z_max":0.02539,"peak_contact_force":10.58981,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2409.0,"raw_peak_contact_force":27.72687,"subtask_id":"push","tcp_end":[0.49465,-0.113,0.02047],"tcp_start":[0.46743,0.01274,0.02993],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":600.0,"object_pos_end":[0.49847,-0.15092,0.02499],"object_pos_start":[0.49898,-0.1499,0.02509],"object_to_goal_dist_end":0.00178,"object_to_goal_dist_start":0.00103,"object_z_max":0.0251,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2001.0,"raw_peak_contact_force":1.43104,"tcp_end":[0.49108,-0.11231,0.08628],"tcp_start":[0.49465,-0.113,0.02047],"tcp_to_object_dist_end":0.07281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```