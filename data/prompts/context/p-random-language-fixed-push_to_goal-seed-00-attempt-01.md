## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=0.067) — your mutation base

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

- **Composite score**: 0.067
- **task_score** (E): 0.001
- **fitness_score**: 0.127  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_side | 1.00 | 1.00 | 0.1883 |
| descend_contact | 1.00 | 1.00 | 0.0884 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |
| retract_lift | 1.00 | 1.00 | 0.0994 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.075, 0.132) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_contact | contact | 1.00 / force_exceeded | (0.493, 0.075, 0.132)→(0.492, 0.035, 0.053) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push_to_goal | push | 0.00 / guard_failure | (0.492, 0.035, 0.053)→(0.492, 0.035, 0.053) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 3.000 | 2.000 | 39.120 |
| retract_lift | retract | 1.00 / step_budget | (0.492, 0.035, 0.053)→(0.489, 0.034, 0.153) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 23.897 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.001
- lateral_force_integral: None
- approach_alignment: 0.472
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.222
- phase_breakdown.approach_score: 0.116
- phase_breakdown.contact_score: 0.551
- phase_breakdown.push_score: 0.067

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.133
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: 0.069
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.378


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7156,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.07268,"descend_contact.contact_force":9.7103,"push_to_goal.push_distance":0.08732,"push_to_goal.push_speed":0.06839,"retract_lift.retract_speed":0.06971},"optimized_scores":{"best_composite_score":0.07327,"best_fitness_score":0.13327,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51885,-0.00264,0.04996],"force_p95":41.4057,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.4057,"mean_force":41.4057,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51195,0.0067,0.05291]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":28.77743,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.95271,"mean_force":10.68421,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51195,0.0067,0.05291]},{"body_a":"attachment","body_b":"push_box","contact_count":18.0,"contact_point_centroid":[0.51818,-0.00267,0.05026],"force_p95":18.09726,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.94579,"mean_force":4.02323,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.51119,0.00648,0.05307]},{"body_a":"world","body_b":"push_box","contact_count":3834.0,"contact_point_centroid":[0.51594,-0.02759,-1e-05],"force_p95":0.24536,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.49335,"mean_force":0.26757,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50843,0.00651,0.10819]},{"body_a":"world","body_b":"push_box","contact_count":2340.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.50498,0.02356,0.21655]},{"body_a":"world","body_b":"push_box","contact_count":2052.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.51054,0.02745,0.09086]}],"total_contact_groups":6},"final_pose_error":0.01045,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51629,-0.02759,0.02499],"final_tcp_position":[0.50877,0.00654,0.16285],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2340.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51196,0.04824,0.13263],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51195,0.0067,0.05291],"tcp_start":[0.51196,0.04824,0.13263],"tcp_to_object_dist_end":0.04448,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.51638,-0.02762,0.02503],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":41.4057,"subtask_id":"push","tcp_end":[0.51188,0.00663,0.05282],"tcp_start":[0.51195,0.0067,0.05291],"tcp_to_object_dist_end":0.04434,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.51629,-0.02759,0.02499],"object_pos_start":[0.51638,-0.02762,0.02503],"object_to_goal_dist_end":0.12349,"object_to_goal_dist_start":0.12347,"object_z_max":0.02572,"peak_contact_force":0.24525,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3852.0,"raw_peak_contact_force":24.94579,"tcp_end":[0.50877,0.00654,0.16285],"tcp_start":[0.51188,0.00663,0.05282],"tcp_to_object_dist_end":0.14222,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87662,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.10714,"descend_contact.contact_force":11.98699,"push_to_goal.push_distance":0.11109,"push_to_goal.push_speed":0.01154,"retract_lift.retract_speed":0.02037},"optimized_scores":{"best_composite_score":0.05841,"best_fitness_score":0.11841,"best_task_score":0.0015},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50469,0.07905,0.04997],"force_p95":41.1712,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.1712,"mean_force":41.1712,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49712,0.08773,0.0533]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":24.27271,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.6305,"mean_force":10.55226,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49712,0.08773,0.0533]},{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.50392,0.07887,0.05011],"force_p95":17.53683,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.3582,"mean_force":6.98145,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49636,0.08743,0.05319]},{"body_a":"world","body_b":"push_box","contact_count":3942.0,"contact_point_centroid":[0.50045,0.05375,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.77399,"mean_force":0.2874,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49355,0.08703,0.09343]},{"body_a":"world","body_b":"push_box","contact_count":2936.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.49815,0.06267,0.21348]},{"body_a":"world","body_b":"push_box","contact_count":1860.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.49626,0.10662,0.08949]}],"total_contact_groups":6},"final_pose_error":0.03977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50076,0.05375,0.02499],"final_tcp_position":[0.49372,0.08707,0.13358],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2936.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49808,0.12595,0.12952],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49712,0.08773,0.0533],"tcp_start":[0.49808,0.12595,0.12952],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50137,0.05406,0.02502],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":41.1712,"subtask_id":"push","tcp_end":[0.49706,0.08766,0.05321],"tcp_start":[0.49712,0.08773,0.0533],"tcp_to_object_dist_end":0.04407,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50076,0.05375,0.02499],"object_pos_start":[0.50137,0.05406,0.02502],"object_to_goal_dist_end":0.20375,"object_to_goal_dist_start":0.20406,"object_z_max":0.02561,"peak_contact_force":0.24525,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3964.0,"raw_peak_contact_force":25.3582,"tcp_end":[0.49372,0.08707,0.13358],"tcp_start":[0.49706,0.08766,0.05321],"tcp_to_object_dist_end":0.1138,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24806,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.0444,"descend_contact.contact_force":2.76562,"push_to_goal.push_distance":0.02027,"push_to_goal.push_speed":0.06133,"retract_lift.retract_speed":0.12265},"optimized_scores":{"best_composite_score":0.06934,"best_fitness_score":0.12934,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.47414,0.00081,0.04997],"force_p95":34.78417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.78417,"mean_force":34.78417,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46745,0.01004,0.05365]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":24.40234,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.12313,"mean_force":9.02691,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46745,0.01004,0.05365]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.47362,0.00078,0.05024],"force_p95":18.73408,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.38802,"mean_force":3.98515,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.46684,0.00984,0.05385]},{"body_a":"world","body_b":"push_box","contact_count":2216.0,"contact_point_centroid":[0.47083,-0.02415,-2e-05],"force_p95":0.24571,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.1819,"mean_force":0.27312,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.46427,0.00984,0.10633]},{"body_a":"world","body_b":"push_box","contact_count":2420.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.48462,0.02504,0.21707]},{"body_a":"world","body_b":"push_box","contact_count":2100.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.46753,0.03051,0.09171]}],"total_contact_groups":6},"final_pose_error":0.01256,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47128,-0.02415,0.02499],"final_tcp_position":[0.46449,0.00987,0.16134],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47035,0.05132,0.13359],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":525.0,"n_steps_budget":630.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46745,0.01004,0.05365],"tcp_start":[0.47035,0.05132,0.13359],"tcp_to_object_dist_end":0.04482,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47134,-0.02418,0.02503],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12905,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":34.78417,"subtask_id":"push","tcp_end":[0.46737,0.00998,0.05357],"tcp_start":[0.46745,0.01004,0.05365],"tcp_to_object_dist_end":0.04469,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":630.0,"object_pos_end":[0.47128,-0.02415,0.02499],"object_pos_start":[0.47134,-0.02418,0.02503],"object_to_goal_dist_end":0.12909,"object_to_goal_dist_start":0.12905,"object_z_max":0.02556,"peak_contact_force":0.24525,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2229.0,"raw_peak_contact_force":21.38802,"tcp_end":[0.46449,0.00987,0.16134],"tcp_start":[0.46737,0.00998,0.05357],"tcp_to_object_dist_end":0.1407,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```