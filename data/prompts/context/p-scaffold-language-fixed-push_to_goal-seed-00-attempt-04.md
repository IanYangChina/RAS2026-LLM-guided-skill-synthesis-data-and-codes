## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5286 | 0.76 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0519 | 0.08 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.3752 | 0.72 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1724 | 0.16 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7632 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.529) — your mutation base

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

- **Composite score**: 0.529
- **task_score** (E): 0.761
- **fitness_score**: 0.689  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2282 |
| contact | 1.00 | 1.00 | 0.0696 |
| push | 1.00 | 1.00 | 0.1557 |
| retract | 1.00 | 1.00 | 0.1599 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.076, 0.089) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.493, 0.076, 0.089)→(0.492, 0.038, 0.031) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 23.919 | 0.245 |
| push | push | 1.00 / step_budget | (0.492, 0.038, 0.031)→(0.495, -0.116, 0.021) | (0.496, 0.001, 0.025)→(0.525, -0.129, 0.027) | 0.152→0.040 | 1.00 / 2.667 | 12.503 | 36.407 |
| retract | retract | 1.00 / step_budget | (0.495, -0.116, 0.021)→(0.493, -0.116, 0.181) | (0.525, -0.129, 0.027)→(0.524, -0.130, 0.025) | 0.040→0.039 | 1.00 / 4.000 | 0.245 | 13.995 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.814
- goal_progress: 0.930
- terminal_score: 0.930
- phase_score: 0.701
- phase_breakdown.approach_score: 0.260
- phase_breakdown.contact_score: 0.755
- phase_breakdown.push_score: 0.845

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.793
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.930
- **Median Q (composite search score)**: 0.532
- **K-run variance**: 0.0075
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.395


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00355,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05189,"approach.approach_speed":0.09374,"contact.contact_force_threshold":10.20619,"push.push_distance":0.15208,"push.push_speed":0.01894,"retract.retract_height":0.24138,"retract.retract_speed":0.05159},"optimized_scores":{"best_composite_score":0.53214,"best_fitness_score":0.69214,"best_task_score":0.72168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":871.0,"contact_point_centroid":[0.5128,-0.07629,0.04904],"force_p95":15.27781,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.37249,"mean_force":5.69247,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50071,-0.06736,0.02298]},{"body_a":"push_box","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.5353,-0.10057,0.05514],"force_p95":23.57379,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.45448,"mean_force":17.92624,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49746,-0.10347,0.02221]},{"body_a":"world","body_b":"push_box","contact_count":1465.0,"contact_point_centroid":[0.53793,-0.11317,-6e-05],"force_p95":18.21158,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.23496,"mean_force":8.22586,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50043,-0.07092,0.02295]},{"body_a":"world","body_b":"push_box","contact_count":2921.0,"contact_point_centroid":[0.53442,-0.1518,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41259,"mean_force":0.24812,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49076,-0.13515,0.1315]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.51213,-0.13786,0.05106],"force_p95":0.6143,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62753,"mean_force":0.28955,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4932,-0.13599,0.02066]},{"body_a":"world","body_b":"push_box","contact_count":2872.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50504,0.02415,0.19219]},{"body_a":"world","body_b":"push_box","contact_count":1892.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5103,0.02883,0.05478]}],"total_contact_groups":7},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53432,-0.15175,0.02499],"final_tcp_position":[0.49141,-0.13525,0.24245],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":29.37249,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2872.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5119,0.04897,0.08486],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":473.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":23.91147,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51166,0.0093,0.02915],"tcp_start":[0.5119,0.04897,0.08486],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53474,-0.15122,0.02586],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.03477,"object_to_goal_dist_start":0.12347,"object_z_max":0.029,"peak_contact_force":0.88383,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2713.0,"raw_peak_contact_force":29.37249,"subtask_id":"push","tcp_end":[0.49357,-0.13578,0.02066],"tcp_start":[0.51166,0.0093,0.02915],"tcp_to_object_dist_end":0.04428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.53432,-0.15175,0.02499],"object_pos_start":[0.53474,-0.15122,0.02586],"object_to_goal_dist_end":0.03436,"object_to_goal_dist_start":0.03477,"object_z_max":0.02586,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2930.0,"raw_peak_contact_force":1.41259,"tcp_end":[0.49141,-0.13525,0.24245],"tcp_start":[0.49357,-0.13578,0.02066],"tcp_to_object_dist_end":0.22226,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20623,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05887,"approach.approach_speed":0.04715,"contact.contact_force_threshold":1.16058,"push.push_distance":0.19775,"push.push_speed":0.09019,"retract.retract_height":0.13456,"retract.retract_speed":0.03304},"optimized_scores":{"best_composite_score":0.42095,"best_fitness_score":0.58095,"best_task_score":0.63275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1363.0,"contact_point_centroid":[0.53665,-0.0382,-8e-05],"force_p95":26.57388,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.38915,"mean_force":6.65637,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49481,-0.0062,0.02447]},{"body_a":"push_box","body_b":"link7","contact_count":228.0,"contact_point_centroid":[0.5327,-0.05432,0.05538],"force_p95":29.62879,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.37154,"mean_force":15.26441,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49564,-0.06336,0.02242]},{"body_a":"attachment","body_b":"push_box","contact_count":758.0,"contact_point_centroid":[0.50742,-0.01294,0.05011],"force_p95":20.48258,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.09007,"mean_force":7.15207,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49479,-0.00557,0.02448]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53425,-0.09351,0.05482],"force_p95":26.4221,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.71859,"mean_force":8.27207,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49631,-0.09445,0.0219]},{"body_a":"world","body_b":"push_box","contact_count":1344.0,"contact_point_centroid":[0.53257,-0.08056,-2e-05],"force_p95":0.51536,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.58534,"mean_force":0.30705,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49355,-0.09369,0.08472]},{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.51164,-0.09142,0.05475],"force_p95":7.02212,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.87295,"mean_force":2.07846,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49462,-0.09411,0.0322]},{"body_a":"world","body_b":"push_box","contact_count":3684.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49799,0.06314,0.19335]},{"body_a":"world","body_b":"push_box","contact_count":1620.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49602,0.10853,0.05883]}],"total_contact_groups":8},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52924,-0.081,0.02499],"final_tcp_position":[0.4937,-0.09366,0.13681],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":48.38915,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3684.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49792,0.12663,0.08958],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":28.59585,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49684,0.09103,0.03194],"tcp_start":[0.49792,0.12663,0.08958],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5344,-0.08159,0.02984],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.07673,"object_to_goal_dist_start":0.20406,"object_z_max":0.02983,"peak_contact_force":35.03765,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2349.0,"raw_peak_contact_force":48.38915,"subtask_id":"push","tcp_end":[0.49668,-0.09413,0.02191],"tcp_start":[0.49684,0.09103,0.03194],"tcp_to_object_dist_end":0.04053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.52924,-0.081,0.02499],"object_pos_start":[0.5344,-0.08159,0.02984],"object_to_goal_dist_end":0.07494,"object_to_goal_dist_start":0.07673,"object_z_max":0.02985,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1401.0,"raw_peak_contact_force":32.71859,"tcp_end":[0.4937,-0.09366,0.13681],"tcp_start":[0.49668,-0.09413,0.02191],"tcp_to_object_dist_end":0.11801,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72414,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05821,"approach.approach_speed":0.06855,"contact.contact_force_threshold":16.50997,"push.push_distance":0.13534,"push.push_speed":0.07265,"retract.retract_height":0.16245,"retract.retract_speed":0.07355},"optimized_scores":{"best_composite_score":0.63263,"best_fitness_score":0.79263,"best_task_score":0.92974},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":702.0,"contact_point_centroid":[0.48531,-0.06856,0.04098],"force_p95":19.0871,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.45988,"mean_force":5.31081,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48108,-0.05664,0.024]},{"body_a":"world","body_b":"push_box","contact_count":1155.0,"contact_point_centroid":[0.4876,-0.10566,-5e-05],"force_p95":10.03378,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.57349,"mean_force":3.63774,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48014,-0.05261,0.02426]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.50216,-0.13097,0.04696],"force_p95":5.16462,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.85319,"mean_force":1.47707,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49532,-0.11904,0.02203]},{"body_a":"world","body_b":"push_box","contact_count":1764.0,"contact_point_centroid":[0.50707,-0.15605,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.97113,"mean_force":0.25381,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4931,-0.11843,0.09238]},{"body_a":"world","body_b":"push_box","contact_count":2860.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48423,0.02565,0.19586]},{"body_a":"world","body_b":"push_box","contact_count":1848.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46724,0.03216,0.05985]}],"total_contact_groups":6},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50701,-0.15575,0.02499],"final_tcp_position":[0.49324,-0.11841,0.16339],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":31.45988,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2860.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46982,0.05205,0.09219],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":19.25034,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46743,0.01277,0.03122],"tcp_start":[0.46982,0.05205,0.09219],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.50722,-0.15506,0.02536],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00883,"object_to_goal_dist_start":0.12903,"object_z_max":0.02557,"peak_contact_force":1.58784,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1857.0,"raw_peak_contact_force":31.45988,"subtask_id":"push","tcp_end":[0.49615,-0.119,0.02055],"tcp_start":[0.46743,0.01277,0.03122],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.15575,0.02499],"object_pos_start":[0.50722,-0.15506,0.02536],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.00883,"object_z_max":0.02556,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1773.0,"raw_peak_contact_force":7.85319,"tcp_end":[0.49324,-0.11841,0.16339],"tcp_start":[0.49615,-0.119,0.02055],"tcp_to_object_dist_end":0.14401,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```