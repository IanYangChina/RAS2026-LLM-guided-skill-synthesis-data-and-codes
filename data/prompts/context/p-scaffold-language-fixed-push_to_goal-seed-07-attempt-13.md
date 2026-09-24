## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2762 | 0.68 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2628 | 0.66 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2942 | 0.02 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2629 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2670 | 0.68 | ❌ rejected |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.276) — your mutation base

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

- **Composite score**: 0.276
- **task_score** (E): 0.682
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2859 |
| contact_1 | 1.00 | 1.00 | 0.0541 |
| push_1 | 1.00 | 1.00 | 0.1248 |
| retract_1 | 0.00 | 1.00 | 0.1222 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.105, 0.039) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.105, 0.039)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 4.667 | 7.665 | 11.752 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.501, -0.068, 0.024) | (0.515, 0.018, 0.025)→(0.512, -0.102, 0.028) | 0.171→0.059 | 1.00 / 3.667 | 49.406 | 85.739 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.068, 0.024)→(0.497, 0.039, 0.082) | (0.512, -0.102, 0.028)→(0.510, -0.098, 0.025) | 0.059→0.058 | 1.00 / 4.000 | 0.245 | 40.633 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.831
- lateral_force_integral: None
- approach_alignment: 0.486
- goal_progress: 0.736
- terminal_score: 0.736
- phase_score: 0.809
- phase_breakdown.push_score: 0.777
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.856

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.780
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.736
- **Median Q (composite search score)**: 0.206
- **K-run variance**: 0.0103
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: approach_1.speed
- **Final σ (mean)**: 0.422


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44767,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.1,"contact_1.speed":0.04679,"push_1.push_depth":0.09174,"push_1.push_distance":0.02203,"push_1.push_speed":0.07025,"retract_1.speed":0.05603},"optimized_scores":{"best_composite_score":0.20295,"best_fitness_score":0.56295,"best_task_score":0.63736},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1774.0,"contact_point_centroid":[0.52,-0.0415,-0.00014],"force_p95":48.37906,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.07195,"mean_force":28.69269,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50422,0.01384,0.02142]},{"body_a":"push_box","body_b":"link7","contact_count":945.0,"contact_point_centroid":[0.53008,-0.00215,0.05421],"force_p95":48.48216,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.2148,"mean_force":39.34836,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50418,0.01452,0.02131]},{"body_a":"attachment","body_b":"push_box","contact_count":951.0,"contact_point_centroid":[0.52264,0.00437,0.05159],"force_p95":44.39548,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.66096,"mean_force":33.91293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50422,0.01491,0.02131]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.52576,-0.06853,0.0542],"force_p95":36.06422,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.13057,"mean_force":18.33937,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49868,-0.04338,0.02226]},{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.51784,-0.05148,0.05454],"force_p95":28.28247,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.80003,"mean_force":5.02158,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49761,-0.04078,0.02275]},{"body_a":"world","body_b":"push_box","contact_count":3846.0,"contact_point_centroid":[0.50233,-0.07852,-1e-05],"force_p95":0.24535,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.08378,"mean_force":0.28018,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49536,0.01041,0.05325]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.51656,0.06849,0.03614],"force_p95":7.48044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.46167,"mean_force":2.9432,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.08033,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2352.0,"contact_point_centroid":[0.5152,0.04612,-1e-05],"force_p95":1.65642,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77995,"mean_force":0.40194,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50825,0.10195,0.02677]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":9},"final_pose_error":0.11422,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50242,-0.07815,0.02499],"final_tcp_position":[0.49574,0.05691,0.08395],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":68.07195,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":660.0,"n_steps_budget":750.0,"object_pos_end":[0.51706,0.03872,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18949,"object_to_goal_dist_start":0.19823,"object_z_max":0.02511,"peak_contact_force":1.02954,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2472.0,"raw_peak_contact_force":12.46167,"tcp_end":[0.51039,0.07559,0.02061],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.50439,-0.08118,0.02851],"object_pos_start":[0.51706,0.03872,0.02494],"object_to_goal_dist_end":0.06905,"object_to_goal_dist_start":0.18949,"object_z_max":0.0288,"peak_contact_force":37.13566,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3670.0,"raw_peak_contact_force":68.07195,"tcp_end":[0.49898,-0.04352,0.02228],"tcp_start":[0.51039,0.07559,0.02061],"tcp_to_object_dist_end":0.03855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50242,-0.07815,0.02499],"object_pos_start":[0.50439,-0.08118,0.02851],"object_to_goal_dist_end":0.07189,"object_to_goal_dist_start":0.06905,"object_z_max":0.02859,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3896.0,"raw_peak_contact_force":36.13057,"tcp_end":[0.49574,0.05691,0.08395],"tcp_start":[0.49898,-0.04352,0.02228],"tcp_to_object_dist_end":0.14752,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23846,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08147,"contact_1.speed":0.03128,"push_1.push_depth":0.09958,"push_1.push_distance":0.05932,"push_1.push_speed":0.03341,"retract_1.speed":0.02379},"optimized_scores":{"best_composite_score":0.20574,"best_fitness_score":0.56574,"best_task_score":0.6731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1442.0,"contact_point_centroid":[0.49379,-0.03092,-0.00012],"force_p95":50.4371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.53848,"mean_force":13.46291,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48477,0.01508,0.01964]},{"body_a":"attachment","body_b":"push_box","contact_count":876.0,"contact_point_centroid":[0.49406,0.01197,0.0368],"force_p95":35.35902,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.616,"mean_force":14.44472,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48361,0.0233,0.01976]},{"body_a":"push_box","body_b":"link7","contact_count":401.0,"contact_point_centroid":[0.50675,0.03577,0.05141],"force_p95":37.77332,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.70757,"mean_force":27.60575,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47843,0.05872,0.02017]},{"body_a":"attachment","body_b":"push_box","contact_count":212.0,"contact_point_centroid":[0.47759,0.07872,0.02844],"force_p95":8.80444,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.41393,"mean_force":4.17257,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47466,0.09057,0.02366]},{"body_a":"world","body_b":"push_box","contact_count":3499.0,"contact_point_centroid":[0.47941,0.05697,-1e-05],"force_p95":2.42202,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.96954,"mean_force":0.49671,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47366,0.10882,0.03158]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.4948,-0.05624,0.02004],"force_p95":1.96478,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.05008,"mean_force":1.13591,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49465,-0.04425,0.02003]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.49571,-0.08173,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76581,"mean_force":0.2471,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49222,0.00682,0.04969]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48518,0.08013,0.18271]}],"total_contact_groups":8},"final_pose_error":0.11855,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49562,-0.08165,0.02499],"final_tcp_position":[0.4936,0.05379,0.08103],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":57.53848,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47593,0.13438,0.04646],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.48143,0.04856,0.02495],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19943,"object_to_goal_dist_start":0.2095,"object_z_max":0.02505,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3711.0,"raw_peak_contact_force":11.41393,"tcp_end":[0.475,0.08529,0.02143],"tcp_start":[0.47593,0.13438,0.04646],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.49588,-0.08114,0.02495],"object_pos_start":[0.48143,0.04856,0.02495],"object_to_goal_dist_end":0.06898,"object_to_goal_dist_start":0.19943,"object_z_max":0.03014,"peak_contact_force":0.59339,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2719.0,"raw_peak_contact_force":57.53848,"tcp_end":[0.49467,-0.04416,0.02005],"tcp_start":[0.475,0.08529,0.02143],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49562,-0.08165,0.02499],"object_pos_start":[0.49588,-0.08114,0.02495],"object_to_goal_dist_end":0.06849,"object_to_goal_dist_start":0.06898,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3986.0,"raw_peak_contact_force":2.05008,"tcp_end":[0.4936,0.05379,0.08103],"tcp_start":[0.49467,-0.04416,0.02005],"tcp_to_object_dist_end":0.1466,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51244,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07199,"contact_1.speed":0.04272,"push_1.push_depth":0.09771,"push_1.push_distance":0.10665,"push_1.push_speed":0.08947,"retract_1.speed":0.02989},"optimized_scores":{"best_composite_score":0.41988,"best_fitness_score":0.77988,"best_task_score":0.73617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":881.0,"contact_point_centroid":[0.55592,-0.07312,0.05413],"force_p95":114.68014,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.60596,"mean_force":77.16059,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5226,-0.05715,0.02342]},{"body_a":"attachment","body_b":"push_box","contact_count":884.0,"contact_point_centroid":[0.54125,-0.06558,0.05259],"force_p95":89.448,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.05835,"mean_force":52.56818,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52267,-0.05692,0.02342]},{"body_a":"world","body_b":"push_box","contact_count":1713.0,"contact_point_centroid":[0.55005,-0.10725,-0.00034],"force_p95":79.64059,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.47475,"mean_force":50.67992,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52235,-0.05837,0.02359]},{"body_a":"push_box","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.54829,-0.12429,0.05665],"force_p95":76.24262,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.71792,"mean_force":31.6847,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50767,-0.11226,0.02979]},{"body_a":"world","body_b":"push_box","contact_count":3630.0,"contact_point_centroid":[0.53193,-0.13464,-3e-05],"force_p95":0.45641,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.79535,"mean_force":0.60492,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50258,-0.04731,0.05541]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.53144,-0.11495,0.06065],"force_p95":56.8472,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.15828,"mean_force":19.94084,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50711,-0.10989,0.0302]},{"body_a":"attachment","body_b":"push_box","contact_count":119.0,"contact_point_centroid":[0.5458,-0.00449,0.03804],"force_p95":7.10342,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.38,"mean_force":2.82246,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53908,0.00739,0.02047]},{"body_a":"world","body_b":"push_box","contact_count":2739.0,"contact_point_centroid":[0.5446,-0.02697,-1e-05],"force_p95":0.96756,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.95788,"mean_force":0.37313,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.03088,0.02392]},{"body_a":"world","body_b":"push_box","contact_count":3844.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51724,0.04382,0.17053]}],"total_contact_groups":9},"final_pose_error":0.16007,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53129,-0.13464,0.02499],"final_tcp_position":[0.5009,0.00616,0.07978],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":131.60596,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3844.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5381,0.05611,0.03245],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.54711,-0.0341,0.0247],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12511,"object_to_goal_dist_start":0.13211,"object_z_max":0.02509,"peak_contact_force":5.96613,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2858.0,"raw_peak_contact_force":11.38,"tcp_end":[0.5396,0.00273,0.01985],"tcp_start":[0.5381,0.05611,0.03245],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":890.0,"n_steps_budget":990.0,"object_pos_end":[0.53664,-0.14434,0.03117],"object_pos_start":[0.54711,-0.0341,0.0247],"object_to_goal_dist_end":0.03759,"object_to_goal_dist_start":0.12511,"object_z_max":0.03122,"peak_contact_force":110.48849,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3478.0,"raw_peak_contact_force":131.60596,"tcp_end":[0.50878,-0.11678,0.02886],"tcp_start":[0.5396,0.00273,0.01985],"tcp_to_object_dist_end":0.03926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53129,-0.13464,0.02499],"object_pos_start":[0.53664,-0.14434,0.03117],"object_to_goal_dist_end":0.03486,"object_to_goal_dist_start":0.03759,"object_z_max":0.03476,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3766.0,"raw_peak_contact_force":83.71792,"tcp_end":[0.5009,0.00616,0.07978],"tcp_start":[0.50878,-0.11678,0.02886],"tcp_to_object_dist_end":0.15411,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```