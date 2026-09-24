## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0392 | 0.03 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7979 | 0.90 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7432 | 0.79 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8088 | 0.91 | ✅ accepted |
| 6 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6468 | 0.90 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.039) — your mutation base

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

- **Composite score**: 0.039
- **task_score** (E): 0.032
- **fitness_score**: 0.233  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1620 |
| contact_1 | 0.67 | 1.00 | 0.1223 |
| push_1 | 0.33 | 1.00 | 0.0479 |
| retract_1 | 1.00 | 1.00 | 0.1706 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.073, 0.163) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.493, 0.073, 0.163)→(0.492, 0.038, 0.049) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.667 | 14.637 | 5.670 |
| push_1 | push | 0.33 / guard_failure | (0.492, 0.036, 0.048)→(0.486, -0.008, 0.031) | (0.496, 0.001, 0.025)→(0.496, -0.001, 0.025) | 0.152→0.150 | 1.00 / 2.000 | 0.118 | 36.791 |
| retract_1 | retract | 1.00 / step_budget | (0.486, -0.008, 0.031)→(0.486, -0.008, 0.201) | (0.496, -0.002, 0.025)→(0.496, -0.005, 0.025) | 0.150→0.147 | 1.00 / 4.000 | 0.245 | 1.113 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.067
- lateral_force_integral: None
- approach_alignment: 0.421
- goal_progress: 0.059
- terminal_score: 0.059
- phase_score: 0.298
- phase_breakdown.approach_score: 0.203
- phase_breakdown.contact_score: 0.755
- phase_breakdown.push_score: 0.063

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.311
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.059
- **Median Q (composite search score)**: 0.074
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.330


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84049,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26399,"contact_1.contact_force":11.11396,"push_1.push_distance":0.03134,"push_1.push_force_guard_threshold":8.4576,"push_1.push_speed":0.07199,"retract_1.retract_height":0.24481},"optimized_scores":{"best_composite_score":-0.04865,"best_fitness_score":0.31135,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":388.0,"contact_point_centroid":[0.51644,-0.02763,-0.0],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50407,0.01583,0.29698]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50932,0.02198,0.18502]},{"body_a":"world","body_b":"push_box","contact_count":916.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50272,-0.05352,0.05661]},{"body_a":"world","body_b":"push_box","contact_count":892.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4934,-0.12203,0.12143]}],"total_contact_groups":4},"final_pose_error":0.04989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51644,-0.02763,0.02499],"final_tcp_position":[0.49508,-0.12182,0.22547],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":0.24534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":97.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":388.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50938,0.03424,0.29161],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51112,0.00985,0.08373],"tcp_start":[0.50938,0.03424,0.29161],"tcp_to_object_dist_end":0.06988,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":916.0,"raw_peak_contact_force":0.24525,"subtask_id":"push","tcp_end":[0.49548,-0.12198,0.03054],"tcp_start":[0.51112,0.00985,0.08373],"tcp_to_object_dist_end":0.09681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":892.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49508,-0.12182,0.22547],"tcp_start":[0.49548,-0.12198,0.03054],"tcp_to_object_dist_end":0.22254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81102,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05028,"contact_1.contact_force":11.53679,"push_1.push_distance":0.17168,"push_1.push_force_guard_threshold":13.81276,"push_1.push_speed":0.05183,"retract_1.retract_height":0.19281},"optimized_scores":{"best_composite_score":0.07355,"best_fitness_score":0.18355,"best_task_score":0.03718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.49745,0.07798,0.03557],"force_p95":27.23283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.68023,"mean_force":7.58394,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49646,0.08993,0.03153]},{"body_a":"world","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.50544,0.05063,-3e-05],"force_p95":16.27776,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.52443,"mean_force":4.91718,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49639,0.08971,0.03146]},{"body_a":"world","body_b":"push_box","contact_count":616.0,"contact_point_centroid":[0.50077,0.04616,-5e-05],"force_p95":0.48229,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32388,"mean_force":0.26407,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49394,0.08705,0.10123]},{"body_a":"world","body_b":"push_box","contact_count":1988.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49881,0.07383,0.20583]},{"body_a":"world","body_b":"push_box","contact_count":1664.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4963,0.10923,0.06085]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50034,0.07582,0.05007],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49593,0.08772,0.03087]}],"total_contact_groups":6},"final_pose_error":0.04929,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50132,0.04647,0.02499],"final_tcp_position":[0.49517,0.08734,0.1744],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":55.68023,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49852,0.12821,0.09381],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":416.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":27.14622,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49699,0.09101,0.03219],"tcp_start":[0.49852,0.12821,0.09381],"tcp_to_object_dist_end":0.03791,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50064,0.05157,0.02495],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20157,"object_to_goal_dist_start":0.20406,"object_z_max":0.02509,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":36.0,"raw_peak_contact_force":55.68023,"subtask_id":"push","tcp_end":[0.49593,0.08772,0.03087],"tcp_start":[0.49596,0.08799,0.03096],"tcp_to_object_dist_end":0.03693,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.50132,0.04647,0.02499],"object_pos_start":[0.50073,0.0507,0.02521],"object_to_goal_dist_end":0.19647,"object_to_goal_dist_start":0.2007,"object_z_max":0.02535,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":617.0,"raw_peak_contact_force":1.32388,"tcp_end":[0.49517,0.08734,0.1744],"tcp_start":[0.49593,0.08772,0.03087],"tcp_to_object_dist_end":0.15502,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84677,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06018,"contact_1.contact_force":15.43378,"push_1.push_distance":0.08717,"push_1.push_force_guard_threshold":21.23156,"push_1.push_speed":0.07124,"retract_1.retract_height":0.2232},"optimized_scores":{"best_composite_score":0.09284,"best_fitness_score":0.20284,"best_task_score":0.05936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.46814,-0.00033,0.03406],"force_p95":27.37686,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.44614,"mean_force":7.73827,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46753,0.01162,0.03113]},{"body_a":"world","body_b":"push_box","contact_count":24.0,"contact_point_centroid":[0.47107,-0.0298,-6e-05],"force_p95":18.0226,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.9612,"mean_force":4.29428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46756,0.01123,0.031]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.46769,0.00077,0.03192],"force_p95":16.4465,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.52074,"mean_force":15.77835,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46769,0.01272,0.03191]},{"body_a":"world","body_b":"push_box","contact_count":1968.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.81834,"mean_force":0.26092,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46836,0.03466,0.0666]},{"body_a":"world","body_b":"push_box","contact_count":700.0,"contact_point_centroid":[0.46868,-0.03367,-4e-05],"force_p95":0.48092,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76978,"mean_force":0.27061,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46641,0.00906,0.11952]},{"body_a":"world","body_b":"push_box","contact_count":1616.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48618,0.03826,0.2071]}],"total_contact_groups":6},"final_pose_error":0.04974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46923,-0.0326,0.02499],"final_tcp_position":[0.4676,0.0092,0.20396],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":54.44614,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47182,0.05684,0.10475],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":492.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.0242,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12901,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":16.52074,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1970.0,"raw_peak_contact_force":16.52074,"subtask_id":"contact","tcp_end":[0.46768,0.01261,0.03172],"tcp_start":[0.47182,0.05684,0.10475],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.47109,-0.02695,0.02489],"object_pos_start":[0.47139,-0.0242,0.02499],"object_to_goal_dist_end":0.1264,"object_to_goal_dist_start":0.12901,"object_z_max":0.0251,"peak_contact_force":0.10776,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":37.0,"raw_peak_contact_force":54.44614,"subtask_id":"push","tcp_end":[0.46772,0.00932,0.0305],"tcp_start":[0.46776,0.00958,0.03057],"tcp_to_object_dist_end":0.03686,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.46923,-0.0326,0.02499],"object_pos_start":[0.47095,-0.02771,0.02517],"object_to_goal_dist_end":0.12137,"object_to_goal_dist_start":0.1257,"object_z_max":0.02561,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":700.0,"raw_peak_contact_force":1.76978,"tcp_end":[0.4676,0.0092,0.20396],"tcp_start":[0.46772,0.00932,0.0305],"tcp_to_object_dist_end":0.1838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```