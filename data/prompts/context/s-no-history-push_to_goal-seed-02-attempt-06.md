## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

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
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.150) — your mutation base

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

- **Composite score**: 0.150
- **task_score** (E): 0.017
- **fitness_score**: 0.046  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 0.33 | 1.00 | 0.1280 |
| descend_to_contact | 1.00 | 1.00 | 0.0004 |
| push_phase | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.013, 0.179) | (0.492, -0.018, 0.025)→(0.463, -0.019, 0.025) | 0.139→0.143 | 1.00 / 4.667 | 361.441 | 1046.051 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.479, -0.013, 0.179)→(0.479, -0.013, 0.179) | (0.463, -0.019, 0.025)→(0.463, -0.019, 0.025) | 0.143→0.143 | 1.00 / 5.000 | 438.065 | 438.065 |
| push_phase | push | 0.00 / guard_failure | (0.479, -0.013, 0.179)→(0.479, -0.013, 0.179) | (0.463, -0.019, 0.025)→(0.463, -0.019, 0.025) | 0.143→0.143 | 1.00 / 5.000 | 588.497 | 608.705 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.212
- lateral_force_integral: None
- approach_alignment: 0.477
- goal_progress: 0.051
- terminal_score: 0.051
- phase_score: 0.089
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.approach_object_score: 0.406
- phase_breakdown.descend_to_contact_score: 0.075

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.074
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.051
- **Median Q (composite search score)**: 0.138
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.477


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.88889,"average_solve_count":36.0,"average_success_count":36.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.11298,"descend_to_contact.descend_force_threshold":9.14801,"push_phase.push_distance":0.24857,"push_phase.push_speed":0.26417},"optimized_scores":{"best_composite_score":0.13798,"best_fitness_score":0.03465,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":752.0,"contact_point_centroid":[0.54211,-0.01394,-8e-05],"force_p95":718.51415,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":804.14499,"mean_force":468.90604,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.44602,-0.0094,0.19555]},{"body_a":"push_box","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.48517,-0.00115,0.04947],"force_p95":242.17817,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":295.70904,"mean_force":61.35454,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.41067,-0.00285,0.12113]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.57235,-0.02892,-8e-05],"force_p95":229.80272,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":230.31348,"mean_force":225.20586,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.46702,-0.01957,0.19009]},{"body_a":"world","body_b":"push_box","contact_count":3552.0,"contact_point_centroid":[0.44373,-0.02584,-2e-05],"force_p95":0.24547,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.21635,"mean_force":0.65813,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.45361,-0.00838,0.1956]},{"body_a":"push_box","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.48462,-0.00469,0.04851],"force_p95":155.44124,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.5181,"mean_force":42.69642,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.40913,-0.00293,0.12586]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57218,-0.02892,-0.0001],"force_p95":102.86354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.86354,"mean_force":102.86354,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.46703,-0.01958,0.19015]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.43984,-0.02608,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.46703,-0.01958,0.19015]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.43984,-0.02608,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.46702,-0.01957,0.19009]}],"total_contact_groups":8},"final_pose_error":0.41551,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.43984,-0.02608,0.02499],"final_tcp_position":[0.46699,-0.01955,0.19008],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":804.14499,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.43984,-0.02608,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.13775,"object_to_goal_dist_start":0.12903,"object_z_max":0.02676,"peak_contact_force":576.7481,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4337.0,"raw_peak_contact_force":804.14499,"subtask_id":"approach_object","tcp_end":[0.46703,-0.01958,0.19015],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16751,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43984,-0.02608,0.02499],"object_pos_start":[0.43984,-0.02608,0.02499],"object_to_goal_dist_end":0.13775,"object_to_goal_dist_start":0.13775,"object_z_max":0.02499,"peak_contact_force":102.86354,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":102.86354,"subtask_id":"descend_to_contact","tcp_end":[0.46703,-0.01958,0.19011],"tcp_start":[0.46703,-0.01958,0.19015],"tcp_to_object_dist_end":0.16747,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":990.0,"object_pos_end":[0.43984,-0.02608,0.02499],"object_pos_start":[0.43984,-0.02608,0.02499],"object_to_goal_dist_end":0.13775,"object_to_goal_dist_start":0.13775,"object_z_max":0.02499,"peak_contact_force":220.09824,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":230.31348,"subtask_id":"push_to_goal","tcp_end":[0.46699,-0.01955,0.19008],"tcp_start":[0.46702,-0.01957,0.19008],"tcp_to_object_dist_end":0.16743,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.34783,"average_solve_count":23.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.29007,"descend_to_contact.descend_force_threshold":4.93643,"push_phase.push_distance":0.16837,"push_phase.push_speed":0.18076},"optimized_scores":{"best_composite_score":0.13378,"best_fitness_score":0.03044,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":391.0,"contact_point_centroid":[0.5551,-0.016,-0.00016],"force_p95":474.51439,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":663.93919,"mean_force":252.56699,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.43193,-0.0137,0.17437]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54588,-0.03081,-0.00011],"force_p95":287.35149,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.66917,"mean_force":266.49242,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.45256,-0.02185,0.19621]},{"body_a":"push_box","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.46663,-0.00904,0.05091],"force_p95":268.69563,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":288.25807,"mean_force":121.80017,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.41501,-0.0057,0.10643]},{"body_a":"world","body_b":"push_box","contact_count":1830.0,"contact_point_centroid":[0.43181,-0.03248,-6e-05],"force_p95":0.53243,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":235.89493,"mean_force":1.48976,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.45196,-0.01186,0.18295]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54579,-0.03085,-0.00012],"force_p95":92.35864,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.35864,"mean_force":92.35864,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.45258,-0.02188,0.19625]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.42872,-0.03177,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.45258,-0.02188,0.19625]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.42872,-0.03177,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.45256,-0.02185,0.19621]}],"total_contact_groups":7},"final_pose_error":0.34873,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.42872,-0.03177,0.02499],"final_tcp_position":[0.45251,-0.02175,0.19624],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":663.93919,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.42872,-0.03177,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.13806,"object_to_goal_dist_start":0.12843,"object_z_max":0.03357,"peak_contact_force":507.32946,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2239.0,"raw_peak_contact_force":663.93919,"subtask_id":"approach_object","tcp_end":[0.45258,-0.02188,0.19625],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1732,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.42872,-0.03177,0.02499],"object_pos_start":[0.42872,-0.03177,0.02499],"object_to_goal_dist_end":0.13806,"object_to_goal_dist_start":0.13806,"object_z_max":0.02499,"peak_contact_force":92.35864,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":92.35864,"subtask_id":"descend_to_contact","tcp_end":[0.45257,-0.02188,0.19621],"tcp_start":[0.45258,-0.02188,0.19625],"tcp_to_object_dist_end":0.17316,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.42872,-0.03177,0.02499],"object_pos_start":[0.42872,-0.03177,0.02499],"object_to_goal_dist_end":0.13806,"object_to_goal_dist_start":0.13806,"object_z_max":0.02499,"peak_contact_force":243.31567,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":289.66917,"subtask_id":"push_to_goal","tcp_end":[0.45251,-0.02175,0.19624],"tcp_start":[0.45255,-0.02182,0.19622],"tcp_to_object_dist_end":0.17319,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.08,"average_mean_iterations":22.88,"average_solve_count":25.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_speed":0.38335,"descend_to_contact.descend_force_threshold":6.22886,"push_phase.push_distance":0.15955,"push_phase.push_speed":0.16679},"optimized_scores":{"best_composite_score":0.17711,"best_fitness_score":0.07378,"best_task_score":0.05146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.62469,0.00159,-0.00027],"force_p95":1295.23792,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1670.06836,"mean_force":768.86964,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49514,0.00078,0.17173]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.66138,0.00195,-0.00022],"force_p95":1305.92989,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1306.13261,"mean_force":1304.10539,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51619,0.00152,0.14983]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.66127,0.00198,-0.0001],"force_p95":1118.97195,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1118.97195,"mean_force":1118.97195,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51619,0.00153,0.15018]},{"body_a":"push_box","body_b":"link6","contact_count":224.0,"contact_point_centroid":[0.55329,0.00085,0.04763],"force_p95":328.89782,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":466.82722,"mean_force":205.50839,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.46274,-7e-05,0.16715]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.53072,0.00103,-0.00019],"force_p95":93.68274,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.18412,"mean_force":24.98863,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.488,0.00035,0.17699]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.53151,0.00452,0.0481],"force_p95":62.04795,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.75887,"mean_force":12.62717,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.44314,-0.0001,0.10254]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.51921,0.00095,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51627,0.00154,0.15059]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.51921,0.00095,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51619,0.00152,0.14983]}],"total_contact_groups":8},"final_pose_error":0.33593,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51921,0.00095,0.02499],"final_tcp_position":[0.51639,0.0015,0.14973],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":1670.06836,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.51921,0.00095,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.15217,"object_to_goal_dist_start":0.16043,"object_z_max":0.02553,"peak_contact_force":0.24525,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2225.0,"raw_peak_contact_force":1670.06836,"subtask_id":"approach_object","tcp_end":[0.51632,0.00155,0.15103],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":810.0,"object_pos_end":[0.51921,0.00095,0.02499],"object_pos_start":[0.51921,0.00095,0.02499],"object_to_goal_dist_end":0.15217,"object_to_goal_dist_start":0.15217,"object_z_max":0.02499,"peak_contact_force":1118.97195,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":1118.97195,"subtask_id":"descend_to_contact","tcp_end":[0.51616,0.00153,0.14991],"tcp_start":[0.51632,0.00155,0.15103],"tcp_to_object_dist_end":0.12495,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.51921,0.00095,0.02499],"object_pos_start":[0.51921,0.00095,0.02499],"object_to_goal_dist_end":0.15217,"object_to_goal_dist_start":0.15217,"object_z_max":0.02499,"peak_contact_force":1302.07818,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":1306.13261,"subtask_id":"push_to_goal","tcp_end":[0.51639,0.0015,0.14973],"tcp_start":[0.51623,0.00151,0.14976],"tcp_to_object_dist_end":0.12477,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```