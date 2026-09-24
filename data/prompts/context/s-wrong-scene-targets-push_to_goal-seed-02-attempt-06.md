## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1571 | 0.09 | ❌ rejected |
| 5 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 4 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 3 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 2 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is 0.09 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.47139345610991795, -0.0241810627903052, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.47139345610991795, -0.0241810627903052, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.157) — your mutation base

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

- **Composite score**: 0.157
- **task_score** (E): 0.093
- **fitness_score**: 0.154  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2683 |
| establish_contact | 1.00 | 1.00 | 0.0139 |
| push_to_goal | 0.00 | 1.00 | 0.0118 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.484, 0.028, 0.041) | (0.492, -0.018, 0.025)→(0.492, -0.019, 0.025) | 0.139→0.139 | 1.00 / 3.000 | 0.164 | 77.368 |
| establish_contact | contact | 1.00 / force_exceeded | (0.484, 0.028, 0.041)→(0.482, 0.017, 0.033) | (0.492, -0.019, 0.025)→(0.491, -0.020, 0.025) | 0.139→0.137 | 1.00 / 4.667 | 17.389 | 0.891 |
| push_to_goal | push | 0.00 / guard_failure | (0.482, 0.017, 0.033)→(0.485, 0.006, 0.031) | (0.491, -0.020, 0.025)→(0.492, -0.031, 0.025) | 0.137→0.127 | 1.00 / 4.000 | 39.778 | 48.419 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.206
- lateral_force_integral: None
- approach_alignment: 0.493
- goal_progress: 0.194
- terminal_score: 0.194
- phase_score: 0.265
- phase_breakdown.approach_and_contact_score: 0.431
- phase_breakdown.push_to_goal_score: 0.194

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.237
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.194
- **Median Q (composite search score)**: 0.117
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.319


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47139,-0.02418,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15625,"average_solve_count":32.0,"average_success_count":32.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.39426,"approach_behind.behind_offset":0.05637,"establish_contact.contact_force_threshold":7.46848,"establish_contact.contact_speed":0.30931,"push_to_goal.push_distance":0.12629,"push_to_goal.push_speed":0.39186},"optimized_scores":{"best_composite_score":0.11665,"best_fitness_score":0.11331,"best_task_score":0.0391},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.46668,-0.00062,0.04422],"force_p95":31.32291,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.82785,"mean_force":9.05243,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45811,0.01125,0.03025]},{"body_a":"world","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.47622,-0.02802,-6e-05],"force_p95":18.46319,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.85226,"mean_force":3.5846,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4582,0.01076,0.03015]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47907,0.0137,0.17269]},{"body_a":"world","body_b":"push_box","contact_count":740.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.45655,0.021,0.03358]}],"total_contact_groups":4},"final_pose_error":0.28899,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4734,-0.0289,0.02529],"final_tcp_position":[0.45869,0.00738,0.02955],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":40.82785,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_and_contact","tcp_end":[0.45786,0.02847,0.03891],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":20.12279,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":740.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_and_contact","tcp_end":[0.45786,0.01279,0.03063],"tcp_start":[0.45786,0.02847,0.03891],"tcp_to_object_dist_end":0.03977,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.4734,-0.0289,0.02529],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12399,"object_to_goal_dist_start":0.12903,"object_z_max":0.0252,"peak_contact_force":40.82785,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":36.0,"raw_peak_contact_force":40.82785,"subtask_id":"push_to_goal","tcp_end":[0.45869,0.00738,0.02955],"tcp_start":[0.45786,0.01279,0.03063],"tcp_to_object_dist_end":0.03938,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45028,-0.03158,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42857,"average_solve_count":35.0,"average_success_count":35.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.54264,"approach_behind.behind_offset":0.0546,"establish_contact.contact_force_threshold":8.03195,"establish_contact.contact_speed":0.27128,"push_to_goal.push_distance":0.19156,"push_to_goal.push_speed":0.1897},"optimized_scores":{"best_composite_score":0.2402,"best_fitness_score":0.23687,"best_task_score":0.19433},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.44238,-0.01834,0.04053],"force_p95":10.14651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.50673,"mean_force":4.05043,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43516,-0.00641,0.0301]},{"body_a":"world","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.45325,-0.05356,-0.0001],"force_p95":10.12221,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.21218,"mean_force":2.93243,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43581,-0.00822,0.02994]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.47604,-0.01835,0.05028],"force_p95":14.62901,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.63507,"mean_force":4.01701,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4332,-0.00056,0.03081]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46574,0.00835,0.17268]},{"body_a":"world","body_b":"push_box","contact_count":620.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.42959,0.01165,0.03469]}],"total_contact_groups":5},"final_pose_error":0.33411,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45283,-0.05791,0.0246],"final_tcp_position":[0.44007,-0.02061,0.0285],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":62.50673,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_and_contact","tcp_end":[0.43025,0.01732,0.03925],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":155.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":16.04505,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":620.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_and_contact","tcp_end":[0.43132,0.00536,0.03208],"tcp_start":[0.43025,0.01732,0.03925],"tcp_to_object_dist_end":0.04213,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.45283,-0.05791,0.0246],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.10347,"object_to_goal_dist_start":0.12843,"object_z_max":0.02563,"peak_contact_force":62.50673,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":122.0,"raw_peak_contact_force":62.50673,"subtask_id":"push_to_goal","tcp_end":[0.44007,-0.02061,0.0285],"tcp_start":[0.43132,0.00536,0.03208],"tcp_to_object_dist_end":0.03961,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55317,0.00136,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55172,"average_solve_count":29.0,"average_success_count":29.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.64096,"approach_behind.behind_offset":0.03961,"establish_contact.contact_force_threshold":11.33444,"establish_contact.contact_speed":0.21139,"push_to_goal.push_distance":0.20005,"push_to_goal.push_speed":0.26584},"optimized_scores":{"best_composite_score":0.11441,"best_fitness_score":0.11108,"best_task_score":0.04675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":30.0,"contact_point_centroid":[0.56594,0.02703,0.04766],"force_p95":230.81137,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":231.61347,"mean_force":173.92121,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.55904,0.03558,0.04851]},{"body_a":"world","body_b":"push_box","contact_count":2202.0,"contact_point_centroid":[0.55354,0.00158,-2e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":206.96085,"mean_force":2.64728,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52705,0.01698,0.17442]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56068,0.01933,0.04904],"force_p95":41.9237,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.9237,"mean_force":41.9237,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55726,0.03136,0.03597]},{"body_a":"world","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.55036,-0.00594,-0.0003],"force_p95":10.24755,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.64556,"mean_force":1.72785,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55787,0.03215,0.03629]},{"body_a":"world","body_b":"push_box","contact_count":82.0,"contact_point_centroid":[0.55031,-0.00994,-0.0005],"force_p95":1.70964,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18153,"mean_force":0.72741,"phase_index":1.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55949,0.03457,0.0384]}],"total_contact_groups":5},"final_pose_error":0.38993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55043,-0.00563,0.02456],"final_tcp_position":[0.55706,0.03102,0.03587],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":231.61347,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":559.0,"n_steps_budget":600.0,"object_pos_end":[0.55297,-0.00031,0.02516],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.15878,"object_to_goal_dist_start":0.16043,"object_z_max":0.02505,"peak_contact_force":0.0,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2232.0,"raw_peak_contact_force":231.61347,"subtask_id":"approach_and_contact","tcp_end":[0.56316,0.03772,0.04368],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.55053,-0.00538,0.02429],"object_pos_start":[0.55297,-0.00031,0.02516],"object_to_goal_dist_end":0.1532,"object_to_goal_dist_start":0.15878,"object_z_max":0.02923,"peak_contact_force":16.0,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":82.0,"raw_peak_contact_force":2.18153,"subtask_id":"approach_and_contact","tcp_end":[0.55831,0.03266,0.03657],"tcp_start":[0.56316,0.03772,0.04368],"tcp_to_object_dist_end":0.04072,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":7.0,"n_steps_budget":930.0,"object_pos_end":[0.55043,-0.00563,0.02456],"object_pos_start":[0.55053,-0.00538,0.02429],"object_to_goal_dist_end":0.15292,"object_to_goal_dist_start":0.1532,"object_z_max":0.02448,"peak_contact_force":16.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":29.0,"raw_peak_contact_force":41.9237,"subtask_id":"push_to_goal","tcp_end":[0.55706,0.03102,0.03587],"tcp_start":[0.55831,0.03266,0.03657],"tcp_to_object_dist_end":0.03893,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```