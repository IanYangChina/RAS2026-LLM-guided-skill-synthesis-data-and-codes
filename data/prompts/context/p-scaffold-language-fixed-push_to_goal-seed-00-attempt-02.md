## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.3752 | 0.72 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1724 | 0.16 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7632 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.375) — your mutation base

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

- **Composite score**: 0.375
- **task_score** (E): 0.724
- **fitness_score**: 0.552  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2004 |
| contact_1 | 1.00 | 1.00 | 0.0951 |
| push_1 | 0.67 | 1.00 | 0.0668 |
| retract_1 | 1.00 | 1.00 | 0.1243 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.079, 0.119) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.494, 0.079, 0.119)→(0.492, 0.037, 0.034) | (0.496, 0.001, 0.025)→(0.496, 0.000, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 16.276 | 8.821 |
| push_1 | push | 0.67 / step_budget | (0.492, 0.037, 0.034)→(0.490, -0.028, 0.028) | (0.496, 0.000, 0.025)→(0.513, -0.055, 0.025) | 0.152→0.104 | 1.00 / 3.667 | 9.436 | 14.667 |
| retract_1 | retract | 1.00 / step_budget | (0.490, -0.028, 0.028)→(0.495, -0.137, 0.070) | (0.513, -0.055, 0.025)→(0.522, -0.122, 0.030) | 0.104→0.042 | 1.00 / 2.667 | 0.398 | 19.640 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.722
- lateral_force_integral: None
- approach_alignment: 0.746
- goal_progress: 0.717
- terminal_score: 0.717
- phase_score: 0.280
- phase_breakdown.approach_score: 0.249
- phase_breakdown.contact_score: 0.746
- phase_breakdown.push_score: 0.013

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.640
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.865
- **Median Q (composite search score)**: 0.380
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.371


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84034,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08058,"approach_1.approach_speed":0.06117,"contact_1.contact_force":17.06084,"contact_1.contact_speed":0.01958,"push_1.push_distance":0.06482,"push_1.push_force_limit":21.89111,"push_1.push_speed":0.07719,"retract_1.retract_height":0.07045,"retract_1.retract_speed":0.06903},"optimized_scores":{"best_composite_score":0.38034,"best_fitness_score":0.64034,"best_task_score":0.59032},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":774.0,"contact_point_centroid":[0.51297,-0.0593,0.04611],"force_p95":14.82008,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.5986,"mean_force":5.27573,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50268,-0.04884,0.02542]},{"body_a":"push_box","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.54184,-0.06421,0.05446],"force_p95":14.82073,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.91421,"mean_force":9.30074,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50104,-0.06514,0.02477]},{"body_a":"world","body_b":"push_box","contact_count":1736.0,"contact_point_centroid":[0.53325,-0.09886,-5e-05],"force_p95":8.73161,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.91076,"mean_force":2.94957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50164,-0.06049,0.02511]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.51173,-0.00299,0.03319],"force_p95":14.11893,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.43727,"mean_force":8.96417,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51169,0.00898,0.03312]},{"body_a":"world","body_b":"push_box","contact_count":3293.0,"contact_point_centroid":[0.51646,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.47775,"mean_force":0.30158,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51014,0.02958,0.07424]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.51218,-0.12602,0.04992],"force_p95":3.61296,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.83578,"mean_force":0.9892,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49533,-0.11909,0.02623]},{"body_a":"world","body_b":"push_box","contact_count":781.0,"contact_point_centroid":[0.54516,-0.12665,-2e-05],"force_p95":0.26856,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.75833,"mean_force":0.25569,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49485,-0.13033,0.04937]},{"body_a":"world","body_b":"push_box","contact_count":1528.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50466,0.03487,0.21709]}],"total_contact_groups":8},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5449,-0.1267,0.02499],"final_tcp_position":[0.49588,-0.1432,0.07714],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":21.31521,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51153,0.05306,0.1247],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.51653,-0.02858,0.02491],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12254,"object_to_goal_dist_start":0.12347,"object_z_max":0.02502,"peak_contact_force":21.31521,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3314.0,"raw_peak_contact_force":14.43727,"subtask_id":"contact","tcp_end":[0.51182,0.00838,0.03164],"tcp_start":[0.51153,0.05306,0.1247],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54479,-0.1262,0.02481],"object_pos_start":[0.51653,-0.02858,0.02491],"object_to_goal_dist_end":0.05073,"object_to_goal_dist_start":0.12254,"object_z_max":0.02757,"peak_contact_force":10.73001,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2547.0,"raw_peak_contact_force":20.5986,"subtask_id":"push","tcp_end":[0.4961,-0.11721,0.02304],"tcp_start":[0.51182,0.00838,0.03164],"tcp_to_object_dist_end":0.04955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":750.0,"object_pos_end":[0.5449,-0.1267,0.02499],"object_pos_start":[0.54479,-0.1262,0.02481],"object_to_goal_dist_end":0.05058,"object_to_goal_dist_start":0.05073,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":788.0,"raw_peak_contact_force":4.83578,"tcp_end":[0.49588,-0.1432,0.07714],"tcp_start":[0.4961,-0.11721,0.02304],"tcp_to_object_dist_end":0.07345,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01843,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05053,"approach_1.approach_speed":0.05791,"contact_1.contact_force":8.78063,"contact_1.contact_speed":0.06866,"push_1.push_distance":0.02045,"push_1.push_force_limit":11.1031,"push_1.push_speed":0.07348,"retract_1.retract_height":0.05004,"retract_1.retract_speed":0.04993},"optimized_scores":{"best_composite_score":0.44501,"best_fitness_score":0.45501,"best_task_score":0.7171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":359.0,"contact_point_centroid":[0.50071,-0.01515,0.04646],"force_p95":21.50893,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.70068,"mean_force":6.04683,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49471,-0.00657,0.04507]},{"body_a":"world","body_b":"push_box","contact_count":731.0,"contact_point_centroid":[0.52587,-0.05535,-9e-05],"force_p95":15.05566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.05898,"mean_force":3.58797,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49503,-0.03189,0.04951]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49682,0.07886,0.03214],"force_p95":8.11661,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.63462,"mean_force":3.74064,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49676,0.09084,0.032]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50133,0.04139,-2e-05],"force_p95":4.59931,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.25797,"mean_force":2.04593,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49673,0.09081,0.03198]},{"body_a":"world","body_b":"push_box","contact_count":2092.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49867,0.07351,0.20639]},{"body_a":"world","body_b":"push_box","contact_count":1796.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49619,0.10919,0.06093]}],"total_contact_groups":6},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50727,-0.09297,0.03028],"final_tcp_position":[0.49628,-0.13213,0.06698],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":36.70068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49841,0.12824,0.09411],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":449.0,"n_steps_budget":750.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":15.73155,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1796.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49689,0.09101,0.03221],"tcp_start":[0.49841,0.12824,0.09411],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.05352,0.02497],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20353,"object_to_goal_dist_start":0.20406,"object_z_max":0.02508,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":8.63462,"subtask_id":"push","tcp_end":[0.49645,0.09044,0.03161],"tcp_start":[0.49689,0.09101,0.03221],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":623.0,"n_steps_budget":1000.0,"object_pos_end":[0.50727,-0.09297,0.03028],"object_pos_start":[0.50095,0.05352,0.02497],"object_to_goal_dist_end":0.05773,"object_to_goal_dist_start":0.20353,"object_z_max":0.03415,"peak_contact_force":0.46092,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1090.0,"raw_peak_contact_force":36.70068,"tcp_end":[0.49628,-0.13213,0.06698],"tcp_start":[0.49645,0.09044,0.03161],"tcp_to_object_dist_end":0.05478,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41358,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09309,"approach_1.approach_speed":0.08692,"contact_1.contact_force":8.91473,"contact_1.contact_speed":0.07469,"push_1.push_distance":0.09324,"push_1.push_force_limit":16.08935,"push_1.push_speed":0.04178,"retract_1.retract_height":0.05424,"retract_1.retract_speed":0.0469},"optimized_scores":{"best_composite_score":0.30013,"best_fitness_score":0.56013,"best_task_score":0.86481},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":152.0,"contact_point_centroid":[0.48813,-0.09821,0.04219],"force_p95":13.81862,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.38416,"mean_force":4.30303,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48307,-0.08751,0.04195]},{"body_a":"attachment","body_b":"push_box","contact_count":916.0,"contact_point_centroid":[0.47679,-0.03552,0.04481],"force_p95":10.44634,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.76729,"mean_force":4.01526,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47176,-0.0237,0.03117]},{"body_a":"world","body_b":"push_box","contact_count":382.0,"contact_point_centroid":[0.51315,-0.13985,-4e-05],"force_p95":10.2654,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.12629,"mean_force":2.23717,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48661,-0.10432,0.05057]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.46773,0.00079,0.03704],"force_p95":11.78004,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.78004,"mean_force":11.78004,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46772,0.01277,0.03702]},{"body_a":"world","body_b":"push_box","contact_count":1502.0,"contact_point_centroid":[0.48185,-0.08089,-4e-05],"force_p95":5.67856,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.71639,"mean_force":2.851,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47152,-0.02216,0.03134]},{"body_a":"world","body_b":"push_box","contact_count":2528.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.70581,"mean_force":0.24978,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46887,0.03387,0.08531]},{"body_a":"world","body_b":"push_box","contact_count":1380.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48681,0.03532,0.22365]}],"total_contact_groups":7},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51319,-0.14514,0.03533],"final_tcp_position":[0.49351,-0.13591,0.06708],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":17.38416,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47272,0.05555,0.13801],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02419,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":11.78004,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2529.0,"raw_peak_contact_force":11.78004,"subtask_id":"contact","tcp_end":[0.46771,0.01272,0.0369],"tcp_start":[0.47272,0.05555,0.13801],"tcp_to_object_dist_end":0.03896,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49289,-0.09354,0.02592],"object_pos_start":[0.47139,-0.02419,0.02499],"object_to_goal_dist_end":0.05691,"object_to_goal_dist_start":0.12902,"object_z_max":0.026,"peak_contact_force":1.57726,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2418.0,"raw_peak_contact_force":14.76729,"subtask_id":"push","tcp_end":[0.47889,-0.05851,0.0292],"tcp_start":[0.46771,0.01272,0.0369],"tcp_to_object_dist_end":0.03787,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.51319,-0.14514,0.03533],"object_pos_start":[0.49289,-0.09354,0.02592],"object_to_goal_dist_end":0.01744,"object_to_goal_dist_start":0.05691,"object_z_max":0.03533,"peak_contact_force":0.4883,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":534.0,"raw_peak_contact_force":17.38416,"tcp_end":[0.49351,-0.13591,0.06708],"tcp_start":[0.47889,-0.05851,0.0292],"tcp_to_object_dist_end":0.03847,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```