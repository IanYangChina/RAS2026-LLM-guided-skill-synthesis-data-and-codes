## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0216 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2838 | 0.69 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2751 | 0.69 | ✅ accepted |

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

## Current Skill (Q=-0.022) — your mutation base

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

- **Composite score**: -0.022
- **task_score** (E): 0.003
- **fitness_score**: 0.138  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2584 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.00 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.034, 0.048) | (0.513, 0.027, 0.025)→(0.516, 0.027, 0.024) | 0.180→0.180 | 1.00 / 5.000 | 226.035 | 241.169 |
| contact_1 | contact | 1.00 / force_exceeded | (0.518, 0.034, 0.048)→(0.518, 0.034, 0.048) | (0.516, 0.027, 0.024)→(0.516, 0.027, 0.024) | 0.180→0.180 | 1.00 / 5.000 | 97.045 | 97.045 |
| push_1 | push | 0.00 / guard_failure | (0.518, 0.034, 0.049)→(0.519, 0.034, 0.049) | (0.516, 0.027, 0.024)→(0.516, 0.027, 0.024) | 0.180→0.180 | 1.00 / 5.000 | 126.591 | 126.591 |
| retract_1 | retract | 0.00 / step_budget | (0.519, 0.034, 0.049)→(0.505, 0.018, 0.175) | (0.516, 0.027, 0.024)→(0.515, 0.026, 0.025) | 0.180→0.179 | 1.00 / 4.000 | 0.245 | 131.516 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.015
- lateral_force_integral: None
- approach_alignment: 0.500
- goal_progress: 0.003
- terminal_score: 0.003
- phase_score: 0.263
- phase_breakdown.push_score: 0.087
- phase_breakdown.approach_score: 0.234
- phase_breakdown.contact_score: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.159
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.030
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.277


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1519,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0459,"contact_1.force_threshold":12.75958,"contact_1.speed":0.03224,"push_1.guard_force_threshold":5.93688,"push_1.push_depth":0.20315,"push_1.speed":0.06815,"retract_1.speed":0.07743},"optimized_scores":{"best_composite_score":-0.03018,"best_fitness_score":0.12982,"best_task_score":0.00232},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.52589,0.05265,0.04728],"force_p95":234.5646,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":245.05333,"mean_force":191.86676,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5148,0.05274,0.05029]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51511,0.04765,-5e-05],"force_p95":23.28466,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.1608,"mean_force":4.92249,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5045,0.04075,0.16866]},{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.53108,0.05186,0.04829],"force_p95":71.94267,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.57965,"mean_force":24.61199,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51994,0.05182,0.0517]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53162,0.05228,0.04619],"force_p95":124.25139,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.08757,"mean_force":115.70487,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52044,0.05243,0.04849]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53148,0.05223,0.04615],"force_p95":94.26684,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.26684,"mean_force":94.26684,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5203,0.05244,0.04845]},{"body_a":"world","body_b":"push_box","contact_count":3990.0,"contact_point_centroid":[0.51646,0.04707,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.85365,"mean_force":0.50401,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51172,0.03798,0.11173]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.51706,0.0474,-0.00057],"force_p95":55.1687,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.41386,"mean_force":29.20166,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52044,0.05243,0.04849]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51706,0.04741,-0.00058],"force_p95":36.142,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.64061,"mean_force":24.04983,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5203,0.05244,0.04845]}],"total_contact_groups":8},"final_pose_error":0.12848,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51652,0.04708,0.02499],"final_tcp_position":[0.50681,0.02498,0.17416],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":245.05333,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51784,0.04761,0.02383],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19841,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":231.0458,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4097.0,"raw_peak_contact_force":245.05333,"subtask_id":"approach","tcp_end":[0.5203,0.05244,0.04845],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51783,0.0476,0.02384],"object_pos_start":[0.51784,0.04761,0.02383],"object_to_goal_dist_end":0.19841,"object_to_goal_dist_start":0.19841,"object_z_max":0.02383,"peak_contact_force":94.26684,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":94.26684,"subtask_id":"contact","tcp_end":[0.52037,0.05243,0.04845],"tcp_start":[0.5203,0.05244,0.04845],"tcp_to_object_dist_end":0.02521,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51782,0.04759,0.02385],"object_pos_start":[0.51783,0.0476,0.02384],"object_to_goal_dist_end":0.1984,"object_to_goal_dist_start":0.19841,"object_z_max":0.02386,"peak_contact_force":125.08757,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":125.08757,"subtask_id":"push","tcp_end":[0.52056,0.05242,0.04859],"tcp_start":[0.5205,0.05242,0.04853],"tcp_to_object_dist_end":0.02536,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51652,0.04708,0.02499],"object_pos_start":[0.51779,0.04758,0.02387],"object_to_goal_dist_end":0.19777,"object_to_goal_dist_start":0.19839,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4032.0,"raw_peak_contact_force":130.57965,"tcp_end":[0.50681,0.02498,0.17416],"tcp_start":[0.52056,0.05242,0.04859],"tcp_to_object_dist_end":0.15111,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04286,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05702,"contact_1.force_threshold":6.42552,"contact_1.speed":0.02125,"push_1.guard_force_threshold":6.14434,"push_1.push_depth":0.18405,"push_1.speed":0.0687,"retract_1.speed":0.06754},"optimized_scores":{"best_composite_score":-0.03388,"best_fitness_score":0.12612,"best_task_score":0.00342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.49392,0.06269,0.04687],"force_p95":258.14803,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":258.64761,"mean_force":210.80146,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48316,0.0625,0.05047]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.49929,0.062,0.04804],"force_p95":72.96541,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.6734,"mean_force":28.78752,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4885,0.06168,0.05214]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49943,0.06257,0.04547],"force_p95":144.49215,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.35524,"mean_force":135.42967,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48857,0.06247,0.04825]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47933,0.05846,-6e-05],"force_p95":55.72966,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.09217,"mean_force":6.06504,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48804,0.04606,0.16801]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49929,0.06257,0.04543],"force_p95":108.90951,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.90951,"mean_force":108.90951,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48843,0.06247,0.04819]},{"body_a":"world","body_b":"push_box","contact_count":3958.0,"contact_point_centroid":[0.48085,0.05778,-2e-05],"force_p95":0.24543,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.27407,"mean_force":0.60356,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48818,0.04692,0.10531]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.48095,0.0583,-0.00065],"force_p95":72.2594,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.99398,"mean_force":34.16259,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48857,0.06247,0.04825]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.48094,0.05831,-0.00065],"force_p95":32.03194,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.2184,"mean_force":27.47701,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48843,0.06247,0.04819]}],"total_contact_groups":8},"final_pose_error":0.1449,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48083,0.05791,0.02499],"final_tcp_position":[0.49079,0.03349,0.15932],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":258.64761,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48192,0.05853,0.02367],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.20931,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":255.97816,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4110.0,"raw_peak_contact_force":258.64761,"subtask_id":"approach","tcp_end":[0.48843,0.06247,0.04819],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.48192,0.05852,0.02368],"object_pos_start":[0.48192,0.05853,0.02367],"object_to_goal_dist_end":0.20931,"object_to_goal_dist_start":0.20931,"object_z_max":0.02367,"peak_contact_force":108.90951,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":108.90951,"subtask_id":"contact","tcp_end":[0.4885,0.06247,0.0482],"tcp_start":[0.48843,0.06247,0.04819],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4819,0.05852,0.02369],"object_pos_start":[0.48192,0.05852,0.02368],"object_to_goal_dist_end":0.20931,"object_to_goal_dist_start":0.20931,"object_z_max":0.0237,"peak_contact_force":145.35524,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":145.35524,"subtask_id":"push","tcp_end":[0.48871,0.06247,0.04837],"tcp_start":[0.48864,0.06247,0.0483],"tcp_to_object_dist_end":0.02591,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48083,0.05791,0.02499],"object_pos_start":[0.48188,0.05851,0.02372],"object_to_goal_dist_end":0.20879,"object_to_goal_dist_start":0.2093,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4007.0,"raw_peak_contact_force":150.6734,"tcp_end":[0.49079,0.03349,0.15932],"tcp_start":[0.48871,0.06247,0.04837],"tcp_to_object_dist_end":0.13689,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15484,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01609,"contact_1.force_threshold":5.23589,"contact_1.speed":0.02441,"push_1.guard_force_threshold":9.31647,"push_1.push_depth":0.21824,"push_1.speed":0.08635,"retract_1.speed":0.08941},"optimized_scores":{"best_composite_score":-0.00087,"best_fitness_score":0.15913,"best_task_score":0.00276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":94.0,"contact_point_centroid":[0.55181,-0.01237,0.04769],"force_p95":198.13343,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":219.80498,"mean_force":164.66111,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54048,-0.01202,0.05035]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.5446,-0.02556,-4e-05],"force_p95":29.85642,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.96119,"mean_force":4.14679,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51858,0.00678,0.16446]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.55671,-0.01453,0.04862],"force_p95":71.58274,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.29618,"mean_force":21.3192,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54536,-0.01429,0.05153]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.55756,-0.01464,0.04679],"force_p95":108.69658,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.32938,"mean_force":102.07229,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54617,-0.01424,0.0488]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.55744,-0.01459,0.04675],"force_p95":87.95993,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.95993,"mean_force":87.95993,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54605,-0.01418,0.04875]},{"body_a":"world","body_b":"push_box","contact_count":3967.0,"contact_point_centroid":[0.54596,-0.02657,-2e-05],"force_p95":0.2454,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.72363,"mean_force":0.44061,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52885,-0.00995,0.12057]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.54664,-0.02679,-0.00048],"force_p95":52.76737,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.97607,"mean_force":25.7961,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54617,-0.01424,0.0488]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.54663,-0.02677,-0.00048],"force_p95":45.27245,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.96583,"mean_force":22.39455,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54605,-0.01418,0.04875]}],"total_contact_groups":8},"final_pose_error":0.10889,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54616,-0.0266,0.02499],"final_tcp_position":[0.51598,-0.00585,0.19244],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":219.80498,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54724,-0.02645,0.02402],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13228,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":191.08183,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4082.0,"raw_peak_contact_force":219.80498,"subtask_id":"approach","tcp_end":[0.54605,-0.01418,0.04875],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.54723,-0.02646,0.02403],"object_pos_start":[0.54724,-0.02645,0.02402],"object_to_goal_dist_end":0.13227,"object_to_goal_dist_start":0.13228,"object_z_max":0.02402,"peak_contact_force":87.95993,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":87.95993,"subtask_id":"contact","tcp_end":[0.54611,-0.01421,0.04876],"tcp_start":[0.54605,-0.01418,0.04875],"tcp_to_object_dist_end":0.02762,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54722,-0.02646,0.02404],"object_pos_start":[0.54723,-0.02646,0.02403],"object_to_goal_dist_end":0.13225,"object_to_goal_dist_start":0.13227,"object_z_max":0.02405,"peak_contact_force":109.32938,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":109.32938,"subtask_id":"push","tcp_end":[0.54628,-0.01428,0.04889],"tcp_start":[0.54623,-0.01426,0.04884],"tcp_to_object_dist_end":0.02769,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54616,-0.0266,0.02499],"object_pos_start":[0.54719,-0.02648,0.02406],"object_to_goal_dist_end":0.13175,"object_to_goal_dist_start":0.13223,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4003.0,"raw_peak_contact_force":113.29618,"tcp_end":[0.51598,-0.00585,0.19244],"tcp_start":[0.54628,-0.01428,0.04889],"tcp_to_object_dist_end":0.17142,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```