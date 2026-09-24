## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2849 | 0.11 | ❌ rejected |
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0213 | 0.00 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ✅ accepted |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.285) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.285
- **task_score** (E): 0.112
- **fitness_score**: 0.232  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2506 |
| contact | 1.00 | 1.00 | 0.0412 |
| push | 0.00 | 0.67 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.058, 0.061) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.489, 0.058, 0.061)→(0.487, 0.019, 0.047) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push | push | 0.00 / guard_failure | (0.484, 0.001, 0.045)→(0.484, 0.001, 0.045) | (0.492, -0.018, 0.025)→(0.490, -0.035, 0.025) | 0.139→0.123 | 0.67 / 1.000 | 0.560 | 46.297 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.239
- lateral_force_integral: None
- approach_alignment: 0.484
- goal_progress: 0.235
- terminal_score: 0.235
- phase_score: 0.316
- phase_breakdown.push_score: 0.077
- phase_breakdown.contact_score: 0.608
- phase_breakdown.approach_score: 0.475

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.284
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.235
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push.push_speed
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92308,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.1989,"contact.contact_force_threshold":11.44775,"contact.contact_speed":0.09864,"push.push_depth":0.14577,"push.push_speed":0.181},"optimized_scores":{"best_composite_score":0.24084,"best_fitness_score":0.18751,"best_task_score":0.00446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.46742,0.00059,0.04715],"force_p95":49.69291,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.23526,"mean_force":21.35778,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4674,0.01253,0.04714]},{"body_a":"world","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.47307,-0.0326,-2e-05],"force_p95":26.15116,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.39152,"mean_force":8.70588,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4674,0.01255,0.04715]},{"body_a":"world","body_b":"push_box","contact_count":2720.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48404,0.02604,0.17875]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46695,0.03217,0.05139]}],"total_contact_groups":4},"final_pose_error":0.31111,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47137,-0.02478,0.02514],"final_tcp_position":[0.46741,0.0121,0.04697],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":810.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2720.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46945,0.05247,0.05904],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":470.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4674,0.01278,0.04725],"tcp_start":[0.46945,0.05247,0.05904],"tcp_to_object_dist_end":0.04333,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.47142,-0.02441,0.02498],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1288,"object_to_goal_dist_start":0.12903,"object_z_max":0.02506,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":50.23526,"subtask_id":"push","tcp_end":[0.46741,0.0121,0.04697],"tcp_start":[0.46744,0.01219,0.04703],"tcp_to_object_dist_end":0.04281,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78261,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.78065,"contact.contact_force_threshold":11.41945,"contact.contact_speed":0.08989,"push.push_depth":0.11387,"push.push_speed":0.18255},"optimized_scores":{"best_composite_score":0.27693,"best_fitness_score":0.2236,"best_task_score":0.09577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.44798,-0.01187,0.04726],"force_p95":18.64461,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.53847,"mean_force":6.78291,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4481,0.00011,0.04722]},{"body_a":"world","body_b":"push_box","contact_count":33.0,"contact_point_centroid":[0.45162,-0.0565,-3e-05],"force_p95":14.00102,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.75523,"mean_force":4.35623,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44802,0.00045,0.04729]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47523,0.02171,0.18345]},{"body_a":"world","body_b":"push_box","contact_count":1876.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44708,0.02469,0.05362]}],"total_contact_groups":4},"final_pose_error":0.26518,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45272,-0.04393,0.02566],"final_tcp_position":[0.44987,-0.00713,0.04628],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45032,0.0449,0.06246],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":469.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44674,0.00541,0.04813],"tcp_start":[0.45032,0.0449,0.06246],"tcp_to_object_dist_end":0.04377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":34.0,"n_steps_budget":960.0,"object_pos_end":[0.45264,-0.0432,0.02543],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11683,"object_to_goal_dist_start":0.12843,"object_z_max":0.02556,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":52.0,"raw_peak_contact_force":31.53847,"subtask_id":"push","tcp_end":[0.44987,-0.00713,0.04628],"tcp_start":[0.44995,-0.0069,0.04634],"tcp_to_object_dist_end":0.04175,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.78466,"contact.contact_force_threshold":10.03105,"contact.contact_speed":0.05532,"push.push_depth":0.07799,"push.push_speed":0.19999},"optimized_scores":{"best_composite_score":0.3369,"best_fitness_score":0.28357,"best_task_score":0.23485},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":31.0,"contact_point_centroid":[0.54431,0.01102,0.04855],"force_p95":27.68445,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.11857,"mean_force":8.98092,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54171,0.02277,0.04398]},{"body_a":"world","body_b":"push_box","contact_count":80.0,"contact_point_centroid":[0.55498,-0.04066,-5e-05],"force_p95":14.25376,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.75999,"mean_force":4.19654,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53995,0.0177,0.04356]},{"body_a":"world","body_b":"push_box","contact_count":2228.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52149,0.03628,0.18328]},{"body_a":"world","body_b":"push_box","contact_count":1852.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54531,0.05634,0.05121]}],"total_contact_groups":4},"final_pose_error":0.22883,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54662,-0.03645,0.02588],"final_tcp_position":[0.53332,-0.00268,0.0422],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2228.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5462,0.07541,0.06112],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54779,0.0383,0.04615],"tcp_start":[0.5462,0.07541,0.06112],"tcp_to_object_dist_end":0.0429,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":92.0,"n_steps_budget":870.0,"object_pos_end":[0.54636,-0.03603,0.02566],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.12304,"object_to_goal_dist_start":0.16043,"object_z_max":0.02623,"peak_contact_force":1.68015,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":111.0,"raw_peak_contact_force":57.11857,"subtask_id":"push","tcp_end":[0.53332,-0.00268,0.0422],"tcp_start":[0.53331,-0.0024,0.04221],"tcp_to_object_dist_end":0.03944,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```