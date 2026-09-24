## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0191 | 0.03 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1042 | 0.07 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0570 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0670 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2337 | 0.80 | ✅ accepted |

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

## Current Skill (Q=0.019) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: push_1
  type: push
  generator: impedance_motion
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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.019
- **task_score** (E): 0.029
- **fitness_score**: 0.268  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2814 |
| contact_1 | 0.67 | 1.00 | 0.0426 |
| push_1 | 0.00 | 1.00 | 0.0026 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.077, 0.033) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / step_budget | (0.493, 0.077, 0.033)→(0.492, 0.036, 0.021) | (0.496, 0.001, 0.025)→(0.497, -0.001, 0.025) | 0.152→0.150 | 1.00 / 3.667 | 9.774 | 8.868 |
| push_1 | push | 0.00 / guard_failure | (0.492, 0.036, 0.021)→(0.491, 0.033, 0.020) | (0.497, -0.001, 0.025)→(0.497, -0.003, 0.025) | 0.150→0.148 | 1.00 / 3.333 | 19.265 | 25.383 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.018
- lateral_force_integral: None
- approach_alignment: 0.352
- goal_progress: 0.018
- terminal_score: 0.018
- phase_score: 0.400
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.763
- phase_breakdown.push_score: 0.014

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.279
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.036
- **Median Q (composite search score)**: -0.081
- **K-run variance**: 0.0203
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95918,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04048,"contact_1.contact_force_threshold":18.57956,"push_1.push_depth":0.11631,"push_1.push_speed":0.03075,"retract_1.retract_height":0.05387,"retract_1.retract_speed":0.03908},"optimized_scores":{"best_composite_score":-0.08069,"best_fitness_score":0.27931,"best_task_score":0.03571},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5419,-0.00678,0.04988],"force_p95":25.18383,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.18383,"mean_force":25.18383,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51083,0.00495,0.01977]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.52473,-0.00586,0.04942],"force_p95":14.88023,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.43185,"mean_force":8.87492,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51154,0.00602,0.0204]},{"body_a":"world","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.51603,-0.04301,-4e-05],"force_p95":12.58649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.53129,"mean_force":4.45889,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51135,0.00576,0.02023]},{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.51443,-0.00407,0.02717],"force_p95":8.07221,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.03683,"mean_force":3.91021,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51149,0.00784,0.02084]},{"body_a":"world","body_b":"push_box","contact_count":1994.0,"contact_point_centroid":[0.51643,-0.02798,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.67653,"mean_force":0.32749,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50976,0.02793,0.02478]},{"body_a":"world","body_b":"push_box","contact_count":3812.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50478,0.02449,0.16599]}],"total_contact_groups":6},"final_pose_error":0.2415,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51704,-0.03216,0.02496],"final_tcp_position":[0.51074,0.00476,0.01969],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":25.18383,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51152,0.04942,0.03315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":516.0,"n_steps_budget":600.0,"object_pos_end":[0.51723,-0.03064,0.02498],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.1206,"object_to_goal_dist_start":0.12347,"object_z_max":0.02503,"peak_contact_force":6.66149,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2036.0,"raw_peak_contact_force":10.03683,"subtask_id":"contact","tcp_end":[0.51171,0.00622,0.02058],"tcp_start":[0.51152,0.04942,0.03315],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.51704,-0.03216,0.02496],"object_pos_start":[0.51723,-0.03064,0.02498],"object_to_goal_dist_end":0.11906,"object_to_goal_dist_start":0.1206,"object_z_max":0.02509,"peak_contact_force":6.82912,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":25.18383,"subtask_id":"push","tcp_end":[0.51074,0.00476,0.01969],"tcp_start":[0.51171,0.00622,0.02058],"tcp_to_object_dist_end":0.03783,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82609,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14807,"contact_1.contact_force_threshold":14.10585,"push_1.push_depth":0.10699,"push_1.push_speed":0.04649,"retract_1.retract_height":0.11254,"retract_1.retract_speed":0.0828},"optimized_scores":{"best_composite_score":0.22072,"best_fitness_score":0.24738,"best_task_score":0.01807},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.49823,0.05489,-4e-05],"force_p95":9.89793,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.5588,"mean_force":4.17092,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49584,0.08975,0.02045]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.52577,0.06687,0.05008],"force_p95":17.28497,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.08369,"mean_force":8.29144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4952,0.08785,0.01972]},{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.50321,0.07768,0.03547],"force_p95":16.61426,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.99818,"mean_force":6.72311,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49573,0.08939,0.02031]},{"body_a":"world","body_b":"push_box","contact_count":3716.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49779,0.06371,0.16414]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49517,0.10861,0.02403]}],"total_contact_groups":5},"final_pose_error":0.31412,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50125,0.05037,0.02513],"final_tcp_position":[0.49502,0.08705,0.01949],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":26.5588,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3716.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49729,0.12761,0.03116],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":21.33917,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49639,0.09101,0.02107],"tcp_start":[0.49729,0.12761,0.03116],"tcp_to_object_dist_end":0.0375,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.50125,0.05037,0.02513],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20037,"object_to_goal_dist_start":0.20406,"object_z_max":0.02515,"peak_contact_force":26.5588,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":77.0,"raw_peak_contact_force":26.5588,"subtask_id":"push","tcp_end":[0.49502,0.08705,0.01949],"tcp_start":[0.49639,0.09101,0.02107],"tcp_to_object_dist_end":0.03763,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68182,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09005,"contact_1.contact_force_threshold":17.92949,"push_1.push_depth":0.14201,"push_1.push_speed":0.08705,"retract_1.retract_height":0.12383,"retract_1.retract_speed":0.05475},"optimized_scores":{"best_composite_score":-0.08267,"best_fitness_score":0.27733,"best_task_score":0.03365},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.49723,-0.00291,0.04996],"force_p95":23.94245,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.40748,"mean_force":19.75721,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46698,0.00882,0.02097]},{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.47306,-0.00058,0.03191],"force_p95":10.41968,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.32255,"mean_force":4.52863,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46697,0.01126,0.02169]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.47557,-0.00255,0.03561],"force_p95":15.05839,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.28658,"mean_force":6.52389,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46704,0.00934,0.02122]},{"body_a":"world","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.46631,-0.04021,-3e-05],"force_p95":13.84925,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.21803,"mean_force":5.02525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46703,0.00927,0.02118]},{"body_a":"world","body_b":"push_box","contact_count":1965.0,"contact_point_centroid":[0.4715,-0.0247,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.88521,"mean_force":0.34486,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46621,0.03141,0.02588]},{"body_a":"world","body_b":"push_box","contact_count":3460.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48367,0.02607,0.16658]}],"total_contact_groups":6},"final_pose_error":0.27474,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47241,-0.0284,0.02504],"final_tcp_position":[0.46696,0.00855,0.02087],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":24.40748,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3460.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46885,0.05267,0.03388],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":514.0,"n_steps_budget":600.0,"object_pos_end":[0.47226,-0.02721,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12588,"object_to_goal_dist_start":0.12903,"object_z_max":0.02511,"peak_contact_force":1.32096,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":16.32255,"subtask_id":"contact","tcp_end":[0.4671,0.00965,0.0214],"tcp_start":[0.46885,0.05267,0.03388],"tcp_to_object_dist_end":0.03741,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.47241,-0.0284,0.02504],"object_pos_start":[0.47226,-0.02721,0.02504],"object_to_goal_dist_end":0.12469,"object_to_goal_dist_start":0.12588,"object_z_max":0.02504,"peak_contact_force":24.40748,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":24.40748,"subtask_id":"push","tcp_end":[0.46696,0.00855,0.02087],"tcp_start":[0.4671,0.00965,0.0214],"tcp_to_object_dist_end":0.03759,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```