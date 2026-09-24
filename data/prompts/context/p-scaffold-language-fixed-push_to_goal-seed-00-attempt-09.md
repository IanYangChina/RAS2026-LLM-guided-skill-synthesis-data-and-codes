## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7979 | 0.90 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7432 | 0.79 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8088 | 0.91 | ✅ accepted |
| 6 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6468 | 0.90 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7965 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.798) — your mutation base

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

- **Composite score**: 0.798
- **task_score** (E): 0.903
- **fitness_score**: 0.808  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2801 |
| contact_1 | 1.00 | 1.00 | 0.0452 |
| push_1 | 1.00 | 1.00 | 0.1463 |
| retract_1 | 0.00 | 1.00 | 0.1659 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.081, 0.035) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.081, 0.035)→(0.491, 0.038, 0.023) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 18.633 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.491, 0.038, 0.023)→(0.496, -0.108, 0.021) | (0.496, 0.001, 0.025)→(0.498, -0.145, 0.028) | 0.152→0.018 | 1.00 / 3.333 | 24.211 | 51.502 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.108, 0.021)→(0.495, 0.042, 0.092) | (0.498, -0.145, 0.028)→(0.495, -0.145, 0.025) | 0.018→0.016 | 1.00 / 4.000 | 0.245 | 20.816 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.427
- goal_progress: 0.949
- terminal_score: 0.949
- phase_score: 0.844
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.763
- phase_breakdown.push_score: 0.901

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.886
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.949
- **Median Q (composite search score)**: 0.822
- **K-run variance**: 0.0057
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.200


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83553,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24118,"contact_1.contact_force":7.56837,"push_1.push_distance":0.10797,"push_1.push_speed":0.07477},"optimized_scores":{"best_composite_score":0.87605,"best_fitness_score":0.88605,"best_task_score":0.94907},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1804.0,"contact_point_centroid":[0.52145,-0.11515,-0.00014],"force_p95":51.32817,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.69114,"mean_force":30.14214,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50503,-0.05982,0.02167]},{"body_a":"push_box","body_b":"link7","contact_count":976.0,"contact_point_centroid":[0.5311,-0.0759,0.05437],"force_p95":50.41033,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.34584,"mean_force":41.29216,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50503,-0.05835,0.02155]},{"body_a":"attachment","body_b":"push_box","contact_count":990.0,"contact_point_centroid":[0.52269,-0.06796,0.05024],"force_p95":49.02839,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.68987,"mean_force":35.17654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50511,-0.05738,0.02155]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52668,-0.1455,0.05431],"force_p95":39.38255,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.54874,"mean_force":21.68066,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49955,-0.12031,0.02218]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.51847,-0.12788,0.05501],"force_p95":29.9613,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.44333,"mean_force":6.54571,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49864,-0.11728,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":3863.0,"contact_point_centroid":[0.50363,-0.15552,-1e-05],"force_p95":0.24565,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.09524,"mean_force":0.28128,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49611,-0.04043,0.05521]},{"body_a":"world","body_b":"push_box","contact_count":3584.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50457,0.04257,0.17098]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5095,0.03174,0.0254]}],"total_contact_groups":8},"final_pose_error":0.13274,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5037,-0.15509,0.02499],"final_tcp_position":[0.49627,0.03192,0.08947],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":69.69114,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51151,0.05414,0.03326],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":23.86761,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.511,0.0093,0.02161],"tcp_start":[0.51151,0.05414,0.03326],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,-0.15875,0.02854],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.01114,"object_to_goal_dist_start":0.12347,"object_z_max":0.0289,"peak_contact_force":41.68569,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3770.0,"raw_peak_contact_force":69.69114,"tcp_end":[0.49995,-0.12066,0.02215],"tcp_start":[0.511,0.0093,0.02161],"tcp_to_object_dist_end":0.03908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,-0.15509,0.02499],"object_pos_start":[0.50591,-0.15875,0.02854],"object_to_goal_dist_end":0.00629,"object_to_goal_dist_start":0.01114,"object_z_max":0.02854,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3912.0,"raw_peak_contact_force":40.54874,"tcp_end":[0.49627,0.03192,0.08947],"tcp_start":[0.49995,-0.12066,0.02215],"tcp_to_object_dist_end":0.19795,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82609,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16805,"contact_1.contact_force":6.03248,"push_1.push_distance":0.15592,"push_1.push_speed":0.0877},"optimized_scores":{"best_composite_score":0.69626,"best_fitness_score":0.70626,"best_task_score":0.86818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1468.0,"contact_point_centroid":[0.49893,-0.0348,-9e-05],"force_p95":20.29599,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.22451,"mean_force":5.08378,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49403,0.01158,0.01969]},{"body_a":"attachment","body_b":"push_box","contact_count":858.0,"contact_point_centroid":[0.50204,-0.01542,0.03453],"force_p95":20.74118,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.09603,"mean_force":6.19222,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49427,-0.00367,0.01974]},{"body_a":"push_box","body_b":"link7","contact_count":231.0,"contact_point_centroid":[0.52391,-0.03129,0.05079],"force_p95":19.13413,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.18167,"mean_force":8.72395,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,-0.01393,0.02005]},{"body_a":"world","body_b":"push_box","contact_count":3909.0,"contact_point_centroid":[0.49574,-0.12353,-2e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.73035,"mean_force":0.25966,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49399,-0.00789,0.05819]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52584,-0.10793,0.05181],"force_p95":15.25013,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.87531,"mean_force":5.6696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49654,-0.08379,0.02096]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.51478,-0.094,0.05286],"force_p95":7.38186,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.10974,"mean_force":2.82944,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49611,-0.08276,0.02109]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49807,0.07938,0.1793]},{"body_a":"world","body_b":"push_box","contact_count":1704.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49517,0.11069,0.02883]}],"total_contact_groups":8},"final_pose_error":0.10262,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49546,-0.12349,0.02499],"final_tcp_position":[0.49516,0.06229,0.09694],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":37.22451,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49747,0.13125,0.03852],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":10.02121,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49618,0.09104,0.02329],"tcp_start":[0.49747,0.13125,0.03852],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,-0.12109,0.02907],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.02921,"object_to_goal_dist_start":0.20406,"object_z_max":0.02903,"peak_contact_force":29.54036,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2557.0,"raw_peak_contact_force":37.22451,"tcp_end":[0.49676,-0.08377,0.02099],"tcp_start":[0.49618,0.09104,0.02329],"tcp_to_object_dist_end":0.03842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49546,-0.12349,0.02499],"object_pos_start":[0.50095,-0.12109,0.02907],"object_to_goal_dist_end":0.0269,"object_to_goal_dist_start":0.02921,"object_z_max":0.02908,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3931.0,"raw_peak_contact_force":20.73035,"tcp_end":[0.49516,0.06229,0.09694],"tcp_start":[0.49676,-0.08377,0.02099],"tcp_to_object_dist_end":0.19922,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51136,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16359,"contact_1.contact_force":11.66557,"push_1.push_distance":0.11216,"push_1.push_speed":0.04587},"optimized_scores":{"best_composite_score":0.82152,"best_fitness_score":0.83152,"best_task_score":0.89047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1546.0,"contact_point_centroid":[0.48404,-0.10682,-7e-05],"force_p95":39.73284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.59026,"mean_force":9.03357,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47999,-0.06111,0.01982]},{"body_a":"attachment","body_b":"push_box","contact_count":917.0,"contact_point_centroid":[0.48596,-0.06421,0.03265],"force_p95":28.91899,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.72002,"mean_force":10.6389,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47835,-0.05248,0.01994]},{"body_a":"push_box","body_b":"link7","contact_count":324.0,"contact_point_centroid":[0.49847,-0.03545,0.05132],"force_p95":28.84123,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.03222,"mean_force":20.72267,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47064,-0.0118,0.02054]},{"body_a":"world","body_b":"push_box","contact_count":3992.0,"contact_point_centroid":[0.48706,-0.15566,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1694,"mean_force":0.24615,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4906,-0.0412,0.05258]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49046,-0.13023,0.02064],"force_p95":1.04789,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.04789,"mean_force":1.04789,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49212,-0.11838,0.01982]},{"body_a":"world","body_b":"push_box","contact_count":3528.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48423,0.04423,0.17157]},{"body_a":"world","body_b":"push_box","contact_count":1780.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46615,0.035,0.02673]}],"total_contact_groups":7},"final_pose_error":0.13245,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48704,-0.15563,0.02499],"final_tcp_position":[0.49287,0.03291,0.08851],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":47.59026,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3528.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46891,0.05747,0.03438],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":445.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":22.00887,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4667,0.01281,0.02262],"tcp_start":[0.46891,0.05747,0.03438],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48726,-0.15504,0.02502],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.0137,"object_to_goal_dist_start":0.12903,"object_z_max":0.03114,"peak_contact_force":1.40581,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2787.0,"raw_peak_contact_force":47.59026,"tcp_end":[0.49212,-0.11838,0.01982],"tcp_start":[0.4667,0.01281,0.02262],"tcp_to_object_dist_end":0.03735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48704,-0.15563,0.02499],"object_pos_start":[0.48726,-0.15504,0.02502],"object_to_goal_dist_end":0.01413,"object_to_goal_dist_start":0.0137,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3993.0,"raw_peak_contact_force":1.1694,"tcp_end":[0.49287,0.03291,0.08851],"tcp_start":[0.49212,-0.11838,0.01982],"tcp_to_object_dist_end":0.19904,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```