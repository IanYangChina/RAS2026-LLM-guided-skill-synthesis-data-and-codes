## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5949 | 0.76 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5811 | 0.74 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5898 | 0.76 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

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

## Current Skill (Q=0.595) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.595
- **task_score** (E): 0.758
- **fitness_score**: 0.805  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2755 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1420 |
| retract_1 | 0.00 | 1.00 | 0.1672 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.058, 0.035) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.058, 0.035)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 3.333 | 5.064 | 14.944 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.125, 0.023) | (0.493, -0.026, 0.025)→(0.499, -0.149, 0.027) | 0.132→0.037 | 1.00 / 3.333 | 49.088 | 87.131 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.125, 0.023)→(0.496, 0.014, 0.115) | (0.499, -0.149, 0.027)→(0.495, -0.147, 0.025) | 0.037→0.034 | 1.00 / 4.000 | 0.245 | 27.436 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.467
- goal_progress: 0.867
- terminal_score: 0.867
- phase_score: 0.853
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.855
- phase_breakdown.contact_score: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.858
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.867
- **Median Q (composite search score)**: 0.573
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.168


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78912,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11472,"approach_1.speed":0.09744,"push_1.push_distance":0.10269},"optimized_scores":{"best_composite_score":0.64848,"best_fitness_score":0.85848,"best_task_score":0.86737},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1216.0,"contact_point_centroid":[0.48715,-0.11308,-0.0001],"force_p95":56.64526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.00579,"mean_force":13.25953,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48151,-0.06796,0.01955]},{"body_a":"attachment","body_b":"push_box","contact_count":731.0,"contact_point_centroid":[0.48825,-0.07007,0.03409],"force_p95":39.8726,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.92603,"mean_force":15.0634,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47974,-0.05837,0.01971]},{"body_a":"push_box","body_b":"link7","contact_count":305.0,"contact_point_centroid":[0.50061,-0.04589,0.05111],"force_p95":38.76234,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.25469,"mean_force":27.80745,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47269,-0.02099,0.02033]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.47026,-0.0027,0.02776],"force_p95":11.67129,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.28184,"mean_force":4.039,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46687,0.0092,0.0221]},{"body_a":"world","body_b":"push_box","contact_count":1937.0,"contact_point_centroid":[0.47161,-0.02489,-1e-05],"force_p95":0.90375,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.68279,"mean_force":0.40373,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.0302,0.02609]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.49073,-0.16441,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98566,"mean_force":0.24625,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49212,-0.06008,0.06999]},{"body_a":"world","body_b":"push_box","contact_count":3436.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48367,0.02608,0.16654]}],"total_contact_groups":7},"final_pose_error":0.14359,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49076,-0.1644,0.02499],"final_tcp_position":[0.49371,0.01131,0.11333],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":70.00579,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3436.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46885,0.05266,0.03392],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.47306,-0.03185,0.02485],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12903,"object_z_max":0.02517,"peak_contact_force":0.56951,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2012.0,"raw_peak_contact_force":16.28184,"tcp_end":[0.46711,0.00512,0.02141],"tcp_start":[0.46885,0.05266,0.03392],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.49082,-0.16383,0.02502],"object_pos_start":[0.47306,-0.03185,0.02485],"object_to_goal_dist_end":0.0166,"object_to_goal_dist_start":0.12118,"object_z_max":0.0308,"peak_contact_force":1.65758,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2252.0,"raw_peak_contact_force":70.00579,"tcp_end":[0.49441,-0.12693,0.01987],"tcp_start":[0.46711,0.00512,0.02141],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49076,-0.1644,0.02499],"object_pos_start":[0.49082,-0.16383,0.02502],"object_to_goal_dist_end":0.01711,"object_to_goal_dist_start":0.0166,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.98566,"tcp_end":[0.49371,0.01131,0.11333],"tcp_start":[0.49441,-0.12693,0.01987],"tcp_to_object_dist_end":0.19669,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29381,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20867,"approach_1.speed":0.0537,"push_1.push_distance":0.09424},"optimized_scores":{"best_composite_score":0.56341,"best_fitness_score":0.77341,"best_task_score":0.66114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1370.0,"contact_point_centroid":[0.45954,-0.11341,-8e-05],"force_p95":42.39415,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.63811,"mean_force":8.36115,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47326,-0.07547,0.01959]},{"body_a":"attachment","body_b":"push_box","contact_count":636.0,"contact_point_centroid":[0.47414,-0.06832,0.0346],"force_p95":30.9547,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.90988,"mean_force":12.13111,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46636,-0.05686,0.01975]},{"body_a":"push_box","body_b":"link7","contact_count":277.0,"contact_point_centroid":[0.48163,-0.04688,0.05075],"force_p95":27.48839,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.25105,"mean_force":20.14253,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45417,-0.02314,0.02028]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.4514,-0.01027,0.03057],"force_p95":10.59402,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.8276,"mean_force":3.96273,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44606,0.00162,0.02243]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48733,-0.13636,0.02271],"force_p95":8.05835,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.05835,"mean_force":8.05835,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49337,-0.12639,0.01987]},{"body_a":"world","body_b":"push_box","contact_count":1932.0,"contact_point_centroid":[0.45026,-0.0324,-1e-05],"force_p95":1.74996,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.84813,"mean_force":0.41285,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4458,0.02306,0.02658]},{"body_a":"world","body_b":"push_box","contact_count":3984.0,"contact_point_centroid":[0.45664,-0.14626,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.13863,"mean_force":0.24782,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49133,-0.05949,0.07012]},{"body_a":"world","body_b":"push_box","contact_count":3704.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47372,0.02261,0.1667]}],"total_contact_groups":8},"final_pose_error":0.14339,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45664,-0.14626,0.02499],"final_tcp_position":[0.4932,0.01155,0.11329],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":56.63811,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3704.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44886,0.04567,0.03426],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45154,-0.03914,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12099,"object_to_goal_dist_start":0.12843,"object_z_max":0.02505,"peak_contact_force":7.82742,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2013.0,"raw_peak_contact_force":13.8276,"tcp_end":[0.4462,-0.00219,0.02177],"tcp_start":[0.44886,0.04567,0.03426],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.45735,-0.14546,0.02496],"object_pos_start":[0.45154,-0.03914,0.02499],"object_to_goal_dist_end":0.04289,"object_to_goal_dist_start":0.12099,"object_z_max":0.03227,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2283.0,"raw_peak_contact_force":56.63811,"tcp_end":[0.49337,-0.12639,0.01987],"tcp_start":[0.4462,-0.00219,0.02177],"tcp_to_object_dist_end":0.04108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45664,-0.14626,0.02499],"object_pos_start":[0.45735,-0.14546,0.02496],"object_to_goal_dist_end":0.04352,"object_to_goal_dist_start":0.04289,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3985.0,"raw_peak_contact_force":8.05835,"tcp_end":[0.4932,0.01155,0.11329],"tcp_start":[0.49337,-0.12639,0.01987],"tcp_to_object_dist_end":0.18449,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45789,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08587,"approach_1.speed":0.06031,"push_1.push_distance":0.13478},"optimized_scores":{"best_composite_score":0.57271,"best_fitness_score":0.78271,"best_task_score":0.74443},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":985.0,"contact_point_centroid":[0.56349,-0.05766,0.05456],"force_p95":130.24345,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.74991,"mean_force":87.17866,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52795,-0.04611,0.02447]},{"body_a":"world","body_b":"push_box","contact_count":1906.0,"contact_point_centroid":[0.56119,-0.09081,-0.00039],"force_p95":100.91922,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.05307,"mean_force":57.72342,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52762,-0.04789,0.0247]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.54813,-0.0526,0.055],"force_p95":89.04181,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.13619,"mean_force":56.74617,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52814,-0.0454,0.02444]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55107,-0.12511,0.05655],"force_p95":53.92427,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.26385,"mean_force":22.35863,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50808,-0.12074,0.03048]},{"body_a":"world","body_b":"push_box","contact_count":3602.0,"contact_point_centroid":[0.53825,-0.13124,-2e-05],"force_p95":0.44518,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.95033,"mean_force":0.45999,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50313,-0.04795,0.08205]},{"body_a":"attachment","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.52933,-0.11553,0.05923],"force_p95":29.75354,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.35161,"mean_force":7.09265,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50649,-0.11328,0.03545]},{"body_a":"attachment","body_b":"push_box","contact_count":93.0,"contact_point_centroid":[0.5545,0.0225,0.04152],"force_p95":12.12151,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.72298,"mean_force":4.16331,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54743,0.03442,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.55327,-0.00033,-1e-05],"force_p95":1.58037,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.88975,"mean_force":0.45817,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54465,0.05451,0.02684]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52172,0.03756,0.16746]}],"total_contact_groups":9},"final_pose_error":0.13462,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53628,-0.1309,0.02499],"final_tcp_position":[0.50104,0.01901,0.11893],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":134.74991,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54548,0.07546,0.03715],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.55504,-0.00652,0.02507],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15367,"object_to_goal_dist_start":0.16043,"object_z_max":0.02512,"peak_contact_force":6.79657,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1965.0,"raw_peak_contact_force":14.72298,"tcp_end":[0.54812,0.03038,0.02033],"tcp_start":[0.54548,0.07546,0.03715],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54912,-0.13875,0.03043],"object_pos_start":[0.55504,-0.00652,0.02507],"object_to_goal_dist_end":0.05068,"object_to_goal_dist_start":0.15367,"object_z_max":0.03107,"peak_contact_force":129.60737,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3885.0,"raw_peak_contact_force":134.74991,"tcp_end":[0.50939,-0.12289,0.02902],"tcp_start":[0.54812,0.03038,0.02033],"tcp_to_object_dist_end":0.0428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53628,-0.1309,0.02499],"object_pos_start":[0.54912,-0.13875,0.03043],"object_to_goal_dist_end":0.041,"object_to_goal_dist_start":0.05068,"object_z_max":0.03233,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3740.0,"raw_peak_contact_force":73.26385,"tcp_end":[0.50104,0.01901,0.11893],"tcp_start":[0.50939,-0.12289,0.02902],"tcp_to_object_dist_end":0.18039,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```