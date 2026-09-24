## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0338 | 0.03 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2402 | 0.81 | ✅ accepted |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2405 | 0.81 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.8813 | 0.78 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2398 | 0.81 | ✅ accepted |

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

## Current Skill (Q=-0.034) — your mutation base

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

- **Composite score**: -0.034
- **task_score** (E): 0.032
- **fitness_score**: 0.185  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1676 |
| contact_object | 1.00 | 1.00 | 0.1272 |
| push_to_goal | 0.67 | 1.00 | 0.0053 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.068, 0.151) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 1.00 / step_budget | (0.495, 0.068, 0.151)→(0.492, 0.033, 0.028) | (0.496, 0.001, 0.025)→(0.497, -0.003, 0.025) | 0.152→0.148 | 1.00 / 5.000 | 18.458 | 32.819 |
| push_to_goal | push | 0.67 / step_budget | (0.492, 0.033, 0.028)→(0.491, 0.037, 0.026) | (0.497, -0.003, 0.025)→(0.496, -0.004, 0.025) | 0.148→0.147 | 1.00 / 4.333 | 3.004 | 12.982 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.036
- lateral_force_integral: None
- approach_alignment: 0.485
- goal_progress: 0.035
- terminal_score: 0.035
- phase_score: 0.291
- phase_breakdown.approach_score: 0.071
- phase_breakdown.contact_score: 0.804
- phase_breakdown.push_score: 0.071

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.189
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.035
- **Median Q (composite search score)**: -0.141
- **K-run variance**: 0.0255
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.301


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37662,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.1386,"approach_object.approach_tolerance":0.02434,"contact_object.contact_force_threshold":8.31337,"push_to_goal.push_distance":0.04852,"push_to_goal.push_speed":0.08832,"push_to_goal.push_tolerance":0.02247},"optimized_scores":{"best_composite_score":0.19184,"best_fitness_score":0.1885,"best_task_score":0.03489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":25.0,"contact_point_centroid":[0.51217,-0.00375,0.04096],"force_p95":22.06581,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.88741,"mean_force":12.78941,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.51152,0.00822,0.03975]},{"body_a":"world","body_b":"push_box","contact_count":2738.0,"contact_point_centroid":[0.51661,-0.02783,-2e-05],"force_p95":0.39508,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.22051,"mean_force":0.36398,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.51008,0.02315,0.09088]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51192,-0.00641,0.03041],"force_p95":7.76539,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.85974,"mean_force":6.91625,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51182,0.00557,0.03042]},{"body_a":"world","body_b":"push_box","contact_count":59.0,"contact_point_centroid":[0.51744,-0.03404,-9e-05],"force_p95":1.61731,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.81362,"mean_force":0.52304,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51152,0.00594,0.02911]},{"body_a":"world","body_b":"push_box","contact_count":760.0,"contact_point_centroid":[0.51644,-0.02763,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50537,0.01963,0.23083]}],"total_contact_groups":5},"final_pose_error":0.01401,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51681,-0.03203,0.02478],"final_tcp_position":[0.5118,0.00684,0.0279],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":33.88741,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":840.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":760.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51135,0.04124,0.15673],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":701.0,"n_steps_budget":870.0,"object_pos_end":[0.51778,-0.03128,0.02483],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12004,"object_to_goal_dist_start":0.12347,"object_z_max":0.02517,"peak_contact_force":23.00408,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2763.0,"raw_peak_contact_force":33.88741,"subtask_id":"contact","tcp_end":[0.51186,0.00558,0.03048],"tcp_start":[0.51135,0.04124,0.15673],"tcp_to_object_dist_end":0.03776,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.51681,-0.03203,0.02478],"object_pos_start":[0.51778,-0.03128,0.02483],"object_to_goal_dist_end":0.11917,"object_to_goal_dist_start":0.12004,"object_z_max":0.02512,"peak_contact_force":0.27585,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":61.0,"raw_peak_contact_force":7.85974,"subtask_id":"push","tcp_end":[0.5118,0.00684,0.0279],"tcp_start":[0.51186,0.00558,0.03048],"tcp_to_object_dist_end":0.03931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00617,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03413,"approach_object.approach_tolerance":0.01593,"contact_object.contact_force_threshold":14.96211,"push_to_goal.push_distance":0.05324,"push_to_goal.push_speed":0.01503,"push_to_goal.push_tolerance":0.00972},"optimized_scores":{"best_composite_score":-0.1523,"best_fitness_score":0.1777,"best_task_score":0.0267},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":80.0,"contact_point_centroid":[0.49734,0.07637,0.03631],"force_p95":22.34662,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.65272,"mean_force":16.70658,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.49717,0.08835,0.03623]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.49682,0.07379,0.02619],"force_p95":25.88894,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.35197,"mean_force":17.71651,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49662,0.08574,0.02613]},{"body_a":"world","body_b":"push_box","contact_count":2394.0,"contact_point_centroid":[0.50114,0.05317,-2e-05],"force_p95":5.45422,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.6838,"mean_force":0.80104,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.49651,0.10074,0.08342]},{"body_a":"world","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.50056,0.04788,-9e-05],"force_p95":6.9315,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56203,"mean_force":2.19842,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49674,0.08594,0.02628]},{"body_a":"world","body_b":"push_box","contact_count":1372.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49886,0.0556,0.22326]}],"total_contact_groups":5},"final_pose_error":0.06224,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50037,0.04861,0.02481],"final_tcp_position":[0.49628,0.08531,0.0257],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":28.65272,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49877,0.11609,0.14274],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":620.0,"n_steps_budget":780.0,"object_pos_end":[0.50101,0.04948,0.0249],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.19948,"object_to_goal_dist_start":0.20406,"object_z_max":0.02502,"peak_contact_force":17.20967,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2474.0,"raw_peak_contact_force":28.65272,"subtask_id":"contact","tcp_end":[0.49746,0.08642,0.02713],"tcp_start":[0.49877,0.11609,0.14274],"tcp_to_object_dist_end":0.03717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.50039,0.04867,0.02479],"object_pos_start":[0.50101,0.04948,0.0249],"object_to_goal_dist_end":0.19867,"object_to_goal_dist_start":0.19948,"object_z_max":0.0251,"peak_contact_force":8.49107,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":51.0,"raw_peak_contact_force":26.35197,"subtask_id":"push","tcp_end":[0.49628,0.08531,0.0257],"tcp_start":[0.49633,0.0854,0.02578],"tcp_to_object_dist_end":0.03689,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64557,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12586,"approach_object.approach_tolerance":0.02057,"contact_object.contact_force_threshold":12.64134,"push_to_goal.push_distance":0.08823,"push_to_goal.push_speed":0.06816,"push_to_goal.push_tolerance":0.02499},"optimized_scores":{"best_composite_score":-0.14089,"best_fitness_score":0.18911,"best_task_score":0.0341},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.46987,-0.00124,0.03885],"force_p95":20.61747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.91763,"mean_force":14.56041,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.46796,0.01072,0.03572]},{"body_a":"world","body_b":"push_box","contact_count":2714.0,"contact_point_centroid":[0.47146,-0.02457,-1e-05],"force_p95":2.9022,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.60257,"mean_force":0.57128,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.46974,0.02657,0.08843]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.46778,-0.00365,0.02718],"force_p95":4.54708,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.73362,"mean_force":2.9209,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46763,0.00833,0.02721]},{"body_a":"world","body_b":"push_box","contact_count":100.0,"contact_point_centroid":[0.47101,-0.03079,-9e-05],"force_p95":0.87766,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.37908,"mean_force":0.34849,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4658,0.01259,0.02584]},{"body_a":"world","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.47139,-0.02418,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48767,0.02165,0.22859]}],"total_contact_groups":5},"final_pose_error":0.0343,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47087,-0.02882,0.02484],"final_tcp_position":[0.46371,0.02029,0.0245],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":35.91763,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":930.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":860.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47476,0.04528,0.15295],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":696.0,"n_steps_budget":840.0,"object_pos_end":[0.47146,-0.02851,0.02474],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1248,"object_to_goal_dist_start":0.12903,"object_z_max":0.02504,"peak_contact_force":15.15951,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2775.0,"raw_peak_contact_force":35.91763,"subtask_id":"contact","tcp_end":[0.46772,0.00835,0.02731],"tcp_start":[0.47476,0.04528,0.15295],"tcp_to_object_dist_end":0.03714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":29.0,"n_steps_budget":600.0,"object_pos_end":[0.47087,-0.02882,0.02484],"object_pos_start":[0.47146,-0.02851,0.02474],"object_to_goal_dist_end":0.12463,"object_to_goal_dist_start":0.1248,"object_z_max":0.02508,"peak_contact_force":0.24548,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":103.0,"raw_peak_contact_force":4.73362,"subtask_id":"push","tcp_end":[0.46371,0.02029,0.0245],"tcp_start":[0.46772,0.00835,0.02731],"tcp_to_object_dist_end":0.04963,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```