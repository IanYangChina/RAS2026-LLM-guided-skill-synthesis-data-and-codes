## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.0109 | 0.45 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1970 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5886 | 0.74 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5887 | 0.74 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0782 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.011) — your mutation base

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

- **Composite score**: 0.011
- **task_score** (E): 0.450
- **fitness_score**: 0.271  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1226 |
| contact_1 | 1.00 | 1.00 | 0.1308 |
| push_1 | 1.00 | 1.00 | 0.1603 |
| retract_1 | 1.00 | 1.00 | 0.0685 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.014, 0.186) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, -0.014, 0.186)→(0.487, -0.018, 0.055) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 50610.888 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.487, -0.018, 0.055)→(0.501, -0.170, 0.050) | (0.492, -0.018, 0.025)→(0.494, -0.079, 0.025) | 0.139→0.077 | 1.00 / 4.000 | 0.245 | 109.925 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.170, 0.050)→(0.497, -0.145, 0.112) | (0.494, -0.079, 0.025)→(0.494, -0.079, 0.025) | 0.077→0.077 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.459
- lateral_force_integral: None
- approach_alignment: 0.792
- goal_progress: 0.456
- terminal_score: 0.456
- phase_score: 0.167
- phase_breakdown.reach_goal_score: 0.199
- phase_breakdown.reach_pre_contact_score: 0.092

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.283
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.490
- **Median Q (composite search score)**: 0.015
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: retract_1.retract_height
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19905,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19098,"approach_1.approach_speed":0.07636,"contact_1.contact_force_threshold":9.77037,"contact_1.contact_z_offset":0.02173,"push_1.push_distance":0.17786,"push_1.push_speed":0.02536,"retract_1.arc_height":0.09795,"retract_1.retract_height":0.1,"retract_1.retract_speed":0.06228},"optimized_scores":{"best_composite_score":0.02256,"best_fitness_score":0.28256,"best_task_score":0.45624},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":216.0,"contact_point_centroid":[0.48319,-0.05063,0.05176],"force_p95":111.09218,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.32928,"mean_force":70.83597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47563,-0.05691,0.05513]},{"body_a":"world","body_b":"push_box","contact_count":1223.0,"contact_point_centroid":[0.47842,-0.07058,-0.00016],"force_p95":97.20682,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.68847,"mean_force":12.9135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48642,-0.11499,0.05221]},{"body_a":"world","body_b":"push_box","contact_count":572.0,"contact_point_centroid":[0.47139,-0.02418,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48897,-0.00821,0.26874]},{"body_a":"world","body_b":"push_box","contact_count":3532.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47136,-0.02071,0.14243]},{"body_a":"world","body_b":"push_box","contact_count":872.0,"contact_point_centroid":[0.47945,-0.08291,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49705,-0.15717,0.07403]}],"total_contact_groups":5},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47945,-0.08291,0.02499],"final_tcp_position":[0.49677,-0.14722,0.10566],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":143.0,"n_steps_budget":780.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":572.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.47707,-0.01776,0.234],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3532.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.46791,-0.02364,0.05577],"tcp_start":[0.47707,-0.01776,0.234],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.47945,-0.08291,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.07016,"object_to_goal_dist_start":0.12903,"object_z_max":0.03522,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1439.0,"raw_peak_contact_force":114.32928,"subtask_id":"reach_goal","tcp_end":[0.49989,-0.1796,0.05037],"tcp_start":[0.46791,-0.02364,0.05577],"tcp_to_object_dist_end":0.10203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":810.0,"object_pos_end":[0.47945,-0.08291,0.02499],"object_pos_start":[0.47945,-0.08291,0.02499],"object_to_goal_dist_end":0.07016,"object_to_goal_dist_start":0.07016,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":872.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_goal","tcp_end":[0.49677,-0.14722,0.10566],"tcp_start":[0.49989,-0.1796,0.05037],"tcp_to_object_dist_end":0.10461,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10952,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15768,"approach_1.approach_speed":0.05352,"contact_1.contact_force_threshold":11.48203,"contact_1.contact_z_offset":0.02489,"push_1.push_distance":0.18863,"push_1.push_speed":0.04424,"retract_1.arc_height":0.14871,"retract_1.retract_height":0.11498,"retract_1.retract_speed":0.05119},"optimized_scores":{"best_composite_score":0.01517,"best_fitness_score":0.27517,"best_task_score":0.49038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1161.0,"contact_point_centroid":[0.46736,-0.08396,-0.00022],"force_p95":108.46767,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":124.78725,"mean_force":14.85349,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48686,-0.13144,0.0522]},{"body_a":"attachment","body_b":"push_box","contact_count":212.0,"contact_point_centroid":[0.46842,-0.05617,0.05202],"force_p95":117.37595,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.76,"mean_force":79.09677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4607,-0.06207,0.05573]},{"body_a":"world","body_b":"push_box","contact_count":908.0,"contact_point_centroid":[0.45028,-0.03158,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47929,-0.0121,0.25181]},{"body_a":"world","body_b":"push_box","contact_count":2932.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45094,-0.02833,0.12651]},{"body_a":"world","body_b":"push_box","contact_count":1100.0,"contact_point_centroid":[0.46773,-0.09306,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50306,-0.16164,0.08094]}],"total_contact_groups":5},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46773,-0.09306,0.02499],"final_tcp_position":[0.49848,-0.14844,0.12038],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":124.78725,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":908.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.45728,-0.02567,0.20024],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":733.0,"n_steps_budget":960.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":45.59157,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2932.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.44705,-0.03104,0.05619],"tcp_start":[0.45728,-0.02567,0.20024],"tcp_to_object_dist_end":0.03137,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.46773,-0.09306,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.06545,"object_to_goal_dist_start":0.12843,"object_z_max":0.04016,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1373.0,"raw_peak_contact_force":124.78725,"subtask_id":"reach_goal","tcp_end":[0.50995,-0.18867,0.05058],"tcp_start":[0.44705,-0.03104,0.05619],"tcp_to_object_dist_end":0.1076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.46773,-0.09306,0.02499],"object_pos_start":[0.46773,-0.09306,0.02499],"object_to_goal_dist_end":0.06545,"object_to_goal_dist_start":0.06545,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_goal","tcp_end":[0.49848,-0.14844,0.12038],"tcp_start":[0.50995,-0.18867,0.05058],"tcp_to_object_dist_end":0.11451,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32065,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08035,"approach_1.approach_speed":0.06651,"contact_1.contact_force_threshold":14.44559,"contact_1.contact_z_offset":0.01128,"push_1.push_distance":0.1705,"push_1.push_speed":0.04227,"retract_1.arc_height":0.08581,"retract_1.retract_height":0.10013,"retract_1.retract_speed":0.07065},"optimized_scores":{"best_composite_score":-0.00489,"best_fitness_score":0.25511,"best_task_score":0.40349},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":221.0,"contact_point_centroid":[0.54443,-0.02502,0.05231],"force_p95":90.23124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.65795,"mean_force":60.59747,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53596,-0.03181,0.05444]},{"body_a":"world","body_b":"push_box","contact_count":1021.0,"contact_point_centroid":[0.54051,-0.04464,-0.00018],"force_p95":67.55665,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.47333,"mean_force":13.51829,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51712,-0.0776,0.05112]},{"body_a":"world","body_b":"push_box","contact_count":1508.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52064,0.00054,0.21304]},{"body_a":"world","body_b":"push_box","contact_count":1476.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54381,0.00112,0.08565]},{"body_a":"world","body_b":"push_box","contact_count":840.0,"contact_point_centroid":[0.53564,-0.06119,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49303,-0.13353,0.07772]}],"total_contact_groups":5},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53564,-0.06119,0.02499],"final_tcp_position":[0.49578,-0.14015,0.10858],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54391,0.00112,0.12286],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":369.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.54653,0.00119,0.0537],"tcp_start":[0.54391,0.00112,0.12286],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.53564,-0.06119,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.0957,"object_to_goal_dist_start":0.16043,"object_z_max":0.03522,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1242.0,"raw_peak_contact_force":90.65795,"subtask_id":"reach_goal","tcp_end":[0.49272,-0.14072,0.04859],"tcp_start":[0.54653,0.00119,0.0537],"tcp_to_object_dist_end":0.0934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":690.0,"object_pos_end":[0.53564,-0.06119,0.02499],"object_pos_start":[0.53564,-0.06119,0.02499],"object_to_goal_dist_end":0.0957,"object_to_goal_dist_start":0.0957,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":840.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_goal","tcp_end":[0.49578,-0.14015,0.10858],"tcp_start":[0.49272,-0.14072,0.04859],"tcp_to_object_dist_end":0.1217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```