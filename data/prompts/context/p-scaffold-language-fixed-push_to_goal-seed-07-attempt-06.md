## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2819 | 0.69 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2790 | 0.71 | ✅ accepted |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2811 | 0.69 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2685 | 0.70 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0216 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.282) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
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
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.282
- **task_score** (E): 0.689
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2848 |
| contact_1 | 1.00 | 1.00 | 0.0549 |
| push_1 | 1.00 | 1.00 | 0.1269 |
| retract_1 | 0.00 | 1.00 | 0.1396 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.106, 0.040) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.106, 0.040)→(0.508, 0.054, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 2.667 | 0.407 | 9.481 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.054, 0.021)→(0.501, -0.071, 0.024) | (0.515, 0.018, 0.025)→(0.508, -0.104, 0.028) | 0.171→0.058 | 1.00 / 3.333 | 51.332 | 87.445 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.071, 0.024)→(0.497, 0.051, 0.091) | (0.508, -0.104, 0.028)→(0.506, -0.100, 0.025) | 0.058→0.057 | 1.00 / 4.000 | 0.245 | 39.504 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.864
- lateral_force_integral: None
- approach_alignment: 0.489
- goal_progress: 0.756
- terminal_score: 0.756
- phase_score: 0.805
- phase_breakdown.push_score: 0.799
- phase_breakdown.approach_score: 0.734
- phase_breakdown.contact_score: 0.863

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.785
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.756
- **Median Q (composite search score)**: 0.218
- **K-run variance**: 0.0103
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.374


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60588,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09713,"contact_1.speed":0.0348,"push_1.push_depth":0.0974,"push_1.push_distance":0.03734,"push_1.push_speed":0.09949,"retract_1.speed":0.06406},"optimized_scores":{"best_composite_score":0.21823,"best_fitness_score":0.57823,"best_task_score":0.66023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1333.0,"contact_point_centroid":[0.52266,-0.04292,-0.00014],"force_p95":57.54541,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.52189,"mean_force":34.15431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50476,0.01174,0.02171]},{"body_a":"push_box","body_b":"link7","contact_count":766.0,"contact_point_centroid":[0.53134,-0.00493,0.05423],"force_p95":55.85964,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.78177,"mean_force":43.62064,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50478,0.01332,0.02157]},{"body_a":"attachment","body_b":"push_box","contact_count":770.0,"contact_point_centroid":[0.52233,0.00335,0.04968],"force_p95":56.99417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.50622,"mean_force":38.75785,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50481,0.01365,0.02156]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.52669,-0.07441,0.05415],"force_p95":40.16454,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.34996,"mean_force":20.89276,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49889,-0.04836,0.02258]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.51863,-0.05641,0.05531],"force_p95":29.46231,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.29075,"mean_force":7.11493,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49802,-0.04592,0.02309]},{"body_a":"world","body_b":"push_box","contact_count":3868.0,"contact_point_centroid":[0.50414,-0.08334,-1e-05],"force_p95":0.24536,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.35679,"mean_force":0.28898,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49565,0.00925,0.05508]},{"body_a":"attachment","body_b":"push_box","contact_count":170.0,"contact_point_centroid":[0.51498,0.06815,0.03252],"force_p95":7.70892,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.6238,"mean_force":3.5127,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50999,0.08001,0.0217]},{"body_a":"world","body_b":"push_box","contact_count":3160.0,"contact_point_centroid":[0.51526,0.04601,-1e-05],"force_p95":1.97645,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.48249,"mean_force":0.43575,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5083,0.10025,0.02668]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50357,0.0767,0.17827]}],"total_contact_groups":9},"final_pose_error":0.10968,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50405,-0.08277,0.02499],"final_tcp_position":[0.49595,0.0599,0.08758],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":79.52189,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51009,0.12536,0.03735],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":868.0,"n_steps_budget":990.0,"object_pos_end":[0.51702,0.03813,0.025],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.1889,"object_to_goal_dist_start":0.19823,"object_z_max":0.02513,"peak_contact_force":0.60633,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3330.0,"raw_peak_contact_force":8.6238,"tcp_end":[0.5105,0.07492,0.02053],"tcp_start":[0.51009,0.12536,0.03735],"tcp_to_object_dist_end":0.03763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":870.0,"object_pos_end":[0.5053,-0.0864,0.0285],"object_pos_start":[0.51702,0.03813,0.025],"object_to_goal_dist_end":0.06392,"object_to_goal_dist_start":0.1889,"object_z_max":0.02911,"peak_contact_force":43.91901,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2869.0,"raw_peak_contact_force":79.52189,"tcp_end":[0.49932,-0.04874,0.02249],"tcp_start":[0.5105,0.07492,0.02053],"tcp_to_object_dist_end":0.0386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50405,-0.08277,0.02499],"object_pos_start":[0.5053,-0.0864,0.0285],"object_to_goal_dist_end":0.06735,"object_to_goal_dist_start":0.06392,"object_z_max":0.0285,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3923.0,"raw_peak_contact_force":41.34996,"tcp_end":[0.49595,0.0599,0.08758],"tcp_start":[0.49932,-0.04874,0.02249],"tcp_to_object_dist_end":0.15601,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48205,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08982,"contact_1.speed":0.03762,"push_1.push_depth":0.09993,"push_1.push_distance":0.14551,"push_1.push_speed":0.04809,"retract_1.speed":0.09574},"optimized_scores":{"best_composite_score":0.20203,"best_fitness_score":0.56203,"best_task_score":0.65226},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1355.0,"contact_point_centroid":[0.48772,-0.03315,-9e-05],"force_p95":47.22277,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.26571,"mean_force":11.97381,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48498,0.01341,0.01957]},{"body_a":"attachment","body_b":"push_box","contact_count":839.0,"contact_point_centroid":[0.49156,0.013,0.03426],"force_p95":34.74791,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.02764,"mean_force":12.78554,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48333,0.02435,0.01964]},{"body_a":"push_box","body_b":"link7","contact_count":353.0,"contact_point_centroid":[0.50635,0.03709,0.05128],"force_p95":35.01502,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.29694,"mean_force":25.37824,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47803,0.06062,0.02004]},{"body_a":"attachment","body_b":"push_box","contact_count":165.0,"contact_point_centroid":[0.48037,0.07895,0.03306],"force_p95":9.56037,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.49738,"mean_force":4.3219,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47465,0.09065,0.02319]},{"body_a":"world","body_b":"push_box","contact_count":2879.0,"contact_point_centroid":[0.47951,0.05663,-1e-05],"force_p95":2.48831,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.28968,"mean_force":0.49729,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47355,0.11039,0.03044]},{"body_a":"world","body_b":"push_box","contact_count":3967.0,"contact_point_centroid":[0.48197,-0.07947,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51325,"mean_force":0.24733,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49279,0.02432,0.06142]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49146,-0.05565,0.02165],"force_p95":0.51162,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51162,"mean_force":0.51162,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49462,-0.04419,0.02001]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4851,0.08067,0.18133]}],"total_contact_groups":8},"final_pose_error":0.07546,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4822,-0.07935,0.02499],"final_tcp_position":[0.4948,0.08962,0.10505],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":55.26571,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47584,0.13481,0.04323],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":800.0,"n_steps_budget":930.0,"object_pos_end":[0.48118,0.04903,0.02504],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19992,"object_to_goal_dist_start":0.2095,"object_z_max":0.02509,"peak_contact_force":0.61513,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3044.0,"raw_peak_contact_force":10.49738,"tcp_end":[0.47499,0.08574,0.02145],"tcp_start":[0.47584,0.13481,0.04323],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.48234,-0.07895,0.02501],"object_pos_start":[0.48118,0.04903,0.02504],"object_to_goal_dist_end":0.07322,"object_to_goal_dist_start":0.19992,"object_z_max":0.03029,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2547.0,"raw_peak_contact_force":55.26571,"tcp_end":[0.49462,-0.04419,0.02001],"tcp_start":[0.47499,0.08574,0.02145],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4822,-0.07935,0.02499],"object_pos_start":[0.48234,-0.07895,0.02501],"object_to_goal_dist_end":0.07285,"object_to_goal_dist_start":0.07322,"object_z_max":0.02501,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3968.0,"raw_peak_contact_force":0.51325,"tcp_end":[0.4948,0.08962,0.10505],"tcp_start":[0.49462,-0.04419,0.02001],"tcp_to_object_dist_end":0.1874,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10526,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04891,"contact_1.speed":0.03589,"push_1.push_depth":0.09788,"push_1.push_distance":0.07106,"push_1.push_speed":0.07984,"retract_1.speed":0.01001},"optimized_scores":{"best_composite_score":0.42529,"best_fitness_score":0.78529,"best_task_score":0.75566},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":974.0,"contact_point_centroid":[0.55547,-0.07583,0.05416],"force_p95":110.08429,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.54782,"mean_force":75.35667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52211,-0.05943,0.0235]},{"body_a":"attachment","body_b":"push_box","contact_count":981.0,"contact_point_centroid":[0.54126,-0.06768,0.05342],"force_p95":86.21882,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.08622,"mean_force":50.82649,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52223,-0.05899,0.02348]},{"body_a":"world","body_b":"push_box","contact_count":1895.0,"contact_point_centroid":[0.54911,-0.11063,-0.00034],"force_p95":73.85449,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.73077,"mean_force":49.20212,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52185,-0.06067,0.02366]},{"body_a":"push_box","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54773,-0.12581,0.05661],"force_p95":69.66345,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.65012,"mean_force":30.01955,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50722,-0.11394,0.02973]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.5308,-0.11693,0.05967],"force_p95":50.16827,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.59577,"mean_force":19.16212,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50676,-0.11193,0.03009]},{"body_a":"world","body_b":"push_box","contact_count":3630.0,"contact_point_centroid":[0.53095,-0.1388,-3e-05],"force_p95":0.27912,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.10998,"mean_force":0.58721,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50233,-0.04897,0.0553]},{"body_a":"attachment","body_b":"push_box","contact_count":165.0,"contact_point_centroid":[0.5447,-0.00487,0.03586],"force_p95":7.0067,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.32253,"mean_force":3.45691,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53906,0.00703,0.0212]},{"body_a":"world","body_b":"push_box","contact_count":3401.0,"contact_point_centroid":[0.54445,-0.02729,-1e-05],"force_p95":1.7632,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.63661,"mean_force":0.41728,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53628,0.03045,0.02696]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51678,0.0436,0.17331]}],"total_contact_groups":9},"final_pose_error":0.16144,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53028,-0.13882,0.02499],"final_tcp_position":[0.50073,0.00472,0.0796],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":127.54782,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53721,0.05709,0.0384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.54707,-0.03448,0.02495],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12474,"object_to_goal_dist_start":0.13211,"object_z_max":0.02515,"peak_contact_force":0.0006,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3566.0,"raw_peak_contact_force":9.32253,"tcp_end":[0.53968,0.00224,0.02009],"tcp_start":[0.53721,0.05709,0.0384],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.5362,-0.14676,0.0311],"object_pos_start":[0.54707,-0.03448,0.02495],"object_to_goal_dist_end":0.03686,"object_to_goal_dist_start":0.12474,"object_z_max":0.03112,"peak_contact_force":110.07585,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3850.0,"raw_peak_contact_force":127.54782,"tcp_end":[0.50844,-0.1187,0.02888],"tcp_start":[0.53968,0.00224,0.02009],"tcp_to_object_dist_end":0.03954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53028,-0.13882,0.02499],"object_pos_start":[0.5362,-0.14676,0.0311],"object_to_goal_dist_end":0.03228,"object_to_goal_dist_start":0.03686,"object_z_max":0.03485,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3767.0,"raw_peak_contact_force":76.65012,"tcp_end":[0.50073,0.00472,0.0796],"tcp_start":[0.50844,-0.1187,0.02888],"tcp_to_object_dist_end":0.15639,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```