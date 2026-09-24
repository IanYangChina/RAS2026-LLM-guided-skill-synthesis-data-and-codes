## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0821 | 0.13 | ❌ rejected |
| 10 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 0.1452 | 0.00 | ❌ rejected |
| 8 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 7 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.082) — your mutation base

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

- **Composite score**: -0.082
- **task_score** (E): 0.129
- **fitness_score**: 0.248  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2459 |
| contact | 0.00 | 1.00 | 0.0311 |
| push | 0.00 | 1.00 | 0.1241 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.073, 0.071) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 0.00 / step_budget | (0.489, 0.073, 0.071)→(0.488, 0.089, 0.048) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push | push | 0.00 / guard_failure | (0.488, 0.089, 0.048)→(0.503, -0.030, 0.038) | (0.492, -0.018, 0.025)→(0.490, -0.039, 0.025) | 0.139→0.123 | 1.00 / 2.000 | 0.687 | 51.090 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.488
- lateral_force_integral: None
- approach_alignment: 0.716
- goal_progress: 0.386
- terminal_score: 0.386
- phase_score: 0.434
- phase_breakdown.approach_obj_score: 0.546
- phase_breakdown.push_goal_score: 0.386

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.415
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.386
- **Median Q (composite search score)**: -0.160
- **K-run variance**: 0.0139
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.348


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75641,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_lateral":0.1047,"approach.approach_z":0.03924,"contact.contact_force_threshold":11.03883,"contact.contact_lateral":0.12923,"push.push_distance":0.23673,"push.push_speed":0.87108},"optimized_scores":{"best_composite_score":-0.15993,"best_fitness_score":0.17007,"best_task_score":0.00068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48097,0.00063,0.03923],"force_p95":58.90914,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.90914,"mean_force":58.90914,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48105,0.01245,0.03916]},{"body_a":"world","body_b":"push_box","contact_count":564.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.25105,"mean_force":0.34871,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47243,0.06352,0.04284]},{"body_a":"world","body_b":"push_box","contact_count":3076.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.484,0.03751,0.18558]},{"body_a":"world","body_b":"push_box","contact_count":1860.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4672,0.0897,0.0575]}],"total_contact_groups":4},"final_pose_error":0.39921,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47142,-0.02427,0.02504],"final_tcp_position":[0.4812,0.0117,0.03914],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":58.90914,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":769.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3076.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_obj","tcp_end":[0.46957,0.07569,0.07262],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46754,0.10191,0.04751],"tcp_start":[0.46957,0.07569,0.07262],"tcp_to_object_dist_end":0.12814,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":141.0,"n_steps_budget":600.0,"object_pos_end":[0.47142,-0.02427,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12894,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.9205,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":565.0,"raw_peak_contact_force":58.90914,"subtask_id":"push_goal","tcp_end":[0.4812,0.0117,0.03914],"tcp_start":[0.46754,0.10191,0.04751],"tcp_to_object_dist_end":0.03985,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55963,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_lateral":0.07386,"approach.approach_z":0.03106,"contact.contact_force_threshold":4.99386,"contact.contact_lateral":0.06176,"push.push_distance":0.3166,"push.push_speed":0.10737},"optimized_scores":{"best_composite_score":0.08463,"best_fitness_score":0.41463,"best_task_score":0.38585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":360.0,"contact_point_centroid":[0.46623,-0.05055,0.04464],"force_p95":15.54332,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.10647,"mean_force":4.49369,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47065,-0.04001,0.04365]},{"body_a":"world","body_b":"push_box","contact_count":2813.0,"contact_point_centroid":[0.44507,-0.07548,-2e-05],"force_p95":4.8253,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.45106,"mean_force":0.8704,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47823,-0.06034,0.04245]},{"body_a":"world","body_b":"push_box","contact_count":3016.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47418,0.01963,0.18225]},{"body_a":"world","body_b":"push_box","contact_count":436.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44766,0.03671,0.05835]}],"total_contact_groups":4},"final_pose_error":0.32695,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.44449,-0.09396,0.02499],"final_tcp_position":[0.50611,-0.13664,0.03709],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":24.10647,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":754.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3016.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_obj","tcp_end":[0.44969,0.03968,0.06548],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":436.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44688,0.03322,0.05189],"tcp_start":[0.44969,0.03968,0.06548],"tcp_to_object_dist_end":0.07024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44449,-0.09396,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.07888,"object_to_goal_dist_start":0.12843,"object_z_max":0.02592,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3173.0,"raw_peak_contact_force":24.10647,"subtask_id":"push_goal","tcp_end":[0.50611,-0.13664,0.03709],"tcp_start":[0.44688,0.03322,0.05189],"tcp_to_object_dist_end":0.07593,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_lateral":0.10727,"approach.approach_z":0.04566,"contact.contact_force_threshold":2.67439,"contact.contact_lateral":0.1344,"push.push_distance":0.32038,"push.push_speed":0.51848},"optimized_scores":{"best_composite_score":-0.1711,"best_fitness_score":0.1589,"best_task_score":0.00098},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52823,0.0262,0.04997],"force_p95":70.2531,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.2531,"mean_force":70.2531,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52059,0.03698,0.03753]},{"body_a":"world","body_b":"push_box","contact_count":612.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.38127,"mean_force":0.35984,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53484,0.09046,0.04072]},{"body_a":"world","body_b":"push_box","contact_count":3484.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52253,0.0513,0.18641]},{"body_a":"world","body_b":"push_box","contact_count":1980.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54618,0.11781,0.05801]}],"total_contact_groups":4},"final_pose_error":0.50479,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55328,0.00115,0.02516],"final_tcp_position":[0.52034,0.03625,0.03752],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":70.2531,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3484.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_obj","tcp_end":[0.54688,0.1028,0.07568],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54845,0.13209,0.04607],"tcp_start":[0.54688,0.1028,0.07568],"tcp_to_object_dist_end":0.1325,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":153.0,"n_steps_budget":750.0,"object_pos_end":[0.55328,0.00115,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16027,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.89452,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":613.0,"raw_peak_contact_force":70.2531,"subtask_id":"push_goal","tcp_end":[0.52034,0.03625,0.03752],"tcp_start":[0.54845,0.13209,0.04607],"tcp_to_object_dist_end":0.04969,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```