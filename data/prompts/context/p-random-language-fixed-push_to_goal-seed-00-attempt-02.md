## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0570 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0670 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2337 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.057) — your mutation base

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

- **Composite score**: 0.057
- **task_score** (E): 0.004
- **fitness_score**: 0.167  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_side | 1.00 | 1.00 | 0.1882 |
| descend_contact | 1.00 | 1.00 | 0.1179 |
| push_to_goal | 0.00 | 0.33 | 0.0001 |
| retract_lift | 0.33 | 1.00 | 0.1017 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.075, 0.132) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_contact | contact | 1.00 / force_exceeded | (0.493, 0.075, 0.132)→(0.492, 0.038, 0.020) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 1311.554 | 9.770 |
| push_to_goal | push | 0.00 / guard_failure | (0.492, 0.037, 0.020)→(0.491, 0.037, 0.020) | (0.496, 0.001, 0.025)→(0.496, 0.000, 0.025) | 0.152→0.152 | 0.33 / 0.333 | 0.138 | 6.450 |
| retract_lift | retract | 0.33 / step_budget | (0.491, 0.037, 0.020)→(0.488, 0.074, 0.112) | (0.496, 0.000, 0.025)→(0.495, 0.000, 0.025) | 0.152→0.151 | 1.00 / 4.000 | 0.245 | 13.537 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.016
- lateral_force_integral: None
- approach_alignment: 0.352
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.283
- phase_breakdown.approach_score: 0.116
- phase_breakdown.contact_score: 0.755
- phase_breakdown.push_score: 0.067

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.171
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.008
- **Median Q (composite search score)**: 0.060
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.514


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39259,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.09067,"descend_contact.contact_force_threshold":6.11487,"push_to_goal.push_depth":0.16104,"push_to_goal.push_speed":0.02028,"retract_lift.retract_arc_height":0.05623,"retract_lift.retract_speed":0.02416},"optimized_scores":{"best_composite_score":0.06065,"best_fitness_score":0.17065,"best_task_score":0.00143},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":121.0,"contact_point_centroid":[0.53983,-0.02111,0.0539],"force_p95":19.88239,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.36671,"mean_force":11.46736,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50914,0.01746,0.02056]},{"body_a":"world","body_b":"push_box","contact_count":3666.0,"contact_point_centroid":[0.51448,-0.02571,-3e-05],"force_p95":4.08431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.0286,"mean_force":0.64441,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5072,0.05081,0.0525]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.5113,-0.00263,0.01989],"force_p95":10.71371,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.71371,"mean_force":10.71371,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.5113,0.00936,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51127,-0.00268,0.01971],"force_p95":4.88127,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.13818,"mean_force":2.56909,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51126,0.00931,0.01968]},{"body_a":"world","body_b":"push_box","contact_count":2664.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.81906,"mean_force":0.24916,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.51023,0.0283,0.07306]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":2.83335,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99126,"mean_force":1.31474,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5113,0.00932,0.01973]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54128,-0.00276,0.05007],"force_p95":0.41291,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41291,"mean_force":0.41291,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51115,0.00927,0.01952]},{"body_a":"world","body_b":"push_box","contact_count":2296.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.50502,0.02364,0.2163]}],"total_contact_groups":8},"final_pose_error":0.09722,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5145,-0.02756,0.02499],"final_tcp_position":[0.5073,0.06486,0.08977],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":21.36671,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51195,0.04823,0.13267],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":666.0,"n_steps_budget":870.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":10.71371,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2665.0,"raw_peak_contact_force":10.71371,"subtask_id":"contact","tcp_end":[0.5113,0.00932,0.01973],"tcp_start":[0.51195,0.04823,0.13267],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51637,-0.0277,0.02506],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12339,"object_to_goal_dist_start":0.12347,"object_z_max":0.02509,"peak_contact_force":0.41291,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":5.13818,"subtask_id":"push","tcp_end":[0.51107,0.00925,0.01942],"tcp_start":[0.51115,0.00927,0.01952],"tcp_to_object_dist_end":0.03775,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5145,-0.02756,0.02499],"object_pos_start":[0.51623,-0.02784,0.02508],"object_to_goal_dist_end":0.1233,"object_to_goal_dist_start":0.12323,"object_z_max":0.0304,"peak_contact_force":0.24525,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3787.0,"raw_peak_contact_force":21.36671,"tcp_end":[0.5073,0.06486,0.08977],"tcp_start":[0.51107,0.00925,0.01942],"tcp_to_object_dist_end":0.11309,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41803,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.11494,"descend_contact.contact_force_threshold":18.90599,"push_to_goal.push_depth":0.08576,"push_to_goal.push_speed":0.01204,"retract_lift.retract_arc_height":0.15337,"retract_lift.retract_speed":0.03344},"optimized_scores":{"best_composite_score":0.05041,"best_fitness_score":0.16041,"best_task_score":0.0085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.49672,0.07885,0.02199],"force_p95":18.34649,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.35069,"mean_force":14.31317,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49665,0.09078,0.02187]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49682,0.07842,0.02031],"force_p95":9.6778,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.6778,"mean_force":9.6778,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49676,0.09042,0.02019]},{"body_a":"world","body_b":"push_box","contact_count":2407.0,"contact_point_centroid":[0.50143,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.13883,"mean_force":0.33951,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49596,0.10763,0.07265]},{"body_a":"world","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.49636,0.05332,-5e-05],"force_p95":3.42601,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.10298,"mean_force":1.19888,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4967,0.09038,0.0201]},{"body_a":"world","body_b":"push_box","contact_count":3984.0,"contact_point_centroid":[0.50056,0.05233,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62036,"mean_force":0.24592,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49275,0.11594,0.05629]},{"body_a":"world","body_b":"push_box","contact_count":2916.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.49816,0.06257,0.21361]}],"total_contact_groups":6},"final_pose_error":0.07945,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50055,0.05233,0.02499],"final_tcp_position":[0.49295,0.12555,0.09876],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":3919.3748,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":729.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2916.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49808,0.12587,0.12962],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":604.0,"n_steps_budget":840.0,"object_pos_end":[0.50139,0.05343,0.02484],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20343,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":3919.3748,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2423.0,"raw_peak_contact_force":18.35069,"subtask_id":"contact","tcp_end":[0.49676,0.09042,0.02019],"tcp_start":[0.49808,0.12587,0.12962],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50129,0.0533,0.02493],"object_pos_start":[0.50139,0.05343,0.02484],"object_to_goal_dist_end":0.20331,"object_to_goal_dist_start":0.20343,"object_z_max":0.02502,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":9.6778,"subtask_id":"push","tcp_end":[0.49652,0.09028,0.01986],"tcp_start":[0.49663,0.09032,0.01996],"tcp_to_object_dist_end":0.03763,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50055,0.05233,0.02499],"object_pos_start":[0.50113,0.0531,0.02508],"object_to_goal_dist_end":0.20233,"object_to_goal_dist_start":0.2031,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3984.0,"raw_peak_contact_force":0.62036,"tcp_end":[0.49295,0.12555,0.09876],"tcp_start":[0.49652,0.09028,0.01986],"tcp_to_object_dist_end":0.10422,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81633,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.12143,"descend_contact.contact_force_threshold":3.42339,"push_to_goal.push_depth":0.0738,"push_to_goal.push_speed":0.04312,"retract_lift.retract_arc_height":0.14989,"retract_lift.retract_speed":0.07557},"optimized_scores":{"best_composite_score":0.05988,"best_fitness_score":0.16988,"best_task_score":0.00218},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":3971.0,"contact_point_centroid":[0.47039,-0.02454,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.62317,"mean_force":0.25215,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4633,0.04002,0.08186]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.49601,0.00061,0.05001],"force_p95":16.78716,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.54064,"mean_force":10.00582,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.46663,0.01267,0.02051]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.46705,0.00077,0.02093],"force_p95":4.30763,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53435,"mean_force":2.26717,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.467,0.01276,0.02088]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":2.62189,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.79364,"mean_force":1.14803,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46705,0.01278,0.02093]},{"body_a":"world","body_b":"push_box","contact_count":2164.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.48471,0.02501,0.21722]},{"body_a":"world","body_b":"push_box","contact_count":2660.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.46735,0.03172,0.07502]}],"total_contact_groups":6},"final_pose_error":0.02856,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47052,-0.02467,0.02499],"final_tcp_position":[0.46363,0.03026,0.14834],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":18.62317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":541.0,"n_steps_budget":960.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2164.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47041,0.05125,0.13384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":665.0,"n_steps_budget":870.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":4.57433,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46705,0.01278,0.02093],"tcp_start":[0.47041,0.05125,0.13384],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47133,-0.02424,0.02506],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12899,"object_to_goal_dist_start":0.12903,"object_z_max":0.02509,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":4.53435,"subtask_id":"push","tcp_end":[0.46676,0.01269,0.02064],"tcp_start":[0.46689,0.01271,0.02073],"tcp_to_object_dist_end":0.03747,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47052,-0.02467,0.02499],"object_pos_start":[0.4712,-0.02436,0.02508],"object_to_goal_dist_end":0.12875,"object_to_goal_dist_start":0.1289,"object_z_max":0.02508,"peak_contact_force":0.24525,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3973.0,"raw_peak_contact_force":18.62317,"tcp_end":[0.46363,0.03026,0.14834],"tcp_start":[0.46676,0.01269,0.02064],"tcp_to_object_dist_end":0.13521,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```