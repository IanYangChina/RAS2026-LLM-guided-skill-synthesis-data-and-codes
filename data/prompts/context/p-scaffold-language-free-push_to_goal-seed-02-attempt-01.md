## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0581 | 0.01 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5898 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.058) — your mutation base

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

- **Composite score**: -0.058
- **task_score** (E): 0.010
- **fitness_score**: 0.269  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2276 |
| contact_1 | 0.33 | 1.00 | 0.0284 |
| push_1 | 0.00 | 1.00 | 0.0643 |
| retract_1 | 1.00 | 1.00 | 0.0886 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, 0.011, 0.078) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.33 / step_budget | (0.489, 0.011, 0.078)→(0.486, -0.010, 0.059) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.333 | 25298.009 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.486, -0.010, 0.058)→(0.466, -0.070, 0.049) | (0.492, -0.018, 0.025)→(0.494, -0.021, 0.025) | 0.139→0.138 | 1.00 / 4.000 | 8.481 | 28.749 |
| retract_1 | retract | 1.00 / step_budget | (0.466, -0.070, 0.049)→(0.462, -0.070, 0.138) | (0.494, -0.021, 0.025)→(0.494, -0.021, 0.025) | 0.138→0.138 | 1.00 / 4.000 | 0.245 | 15.758 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.001
- lateral_force_integral: None
- approach_alignment: 0.503
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.339
- phase_breakdown.reach_pre_contact_score: 0.988
- phase_breakdown.push_to_goal_score: 0.061

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.403
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.031
- **Median Q (composite search score)**: -0.007
- **K-run variance**: 0.0121
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.775,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04034,"approach_1.approach_speed":0.03021,"contact_1.contact_force_threshold":16.38281,"contact_1.contact_speed":0.01075,"push_1.push_distance":0.11093,"push_1.push_speed":0.04819,"retract_1.retract_speed":0.1338},"optimized_scores":{"best_composite_score":-0.21108,"best_fitness_score":0.19892,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.47689,-0.018,0.04994],"force_p95":30.90457,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.13308,"mean_force":28.84799,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46643,-0.01789,0.05578]},{"body_a":"world","body_b":"push_box","contact_count":52.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":8.91788,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.6924,"mean_force":1.35021,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46652,-0.01714,0.05628]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.47635,-0.01852,0.05012],"force_p95":23.90728,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.01525,"mean_force":5.86191,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4659,-0.01839,0.05584]},{"body_a":"world","body_b":"push_box","contact_count":2044.0,"contact_point_centroid":[0.47075,-0.0241,-1e-05],"force_p95":0.24571,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.58111,"mean_force":0.28408,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46317,-0.01811,0.09974]},{"body_a":"world","body_b":"push_box","contact_count":3064.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48408,0.00263,0.18777]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46647,-0.00871,0.06201]}],"total_contact_groups":6},"final_pose_error":0.0118,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47124,-0.0241,0.02499],"final_tcp_position":[0.46328,-0.01807,0.14428],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":31.13308,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":766.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3064.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.46951,0.00536,0.07513],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.46665,-0.01669,0.05671],"tcp_start":[0.46951,0.00536,0.07513],"tcp_to_object_dist_end":0.03294,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02419,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":54.0,"raw_peak_contact_force":31.13308,"subtask_id":"push_to_goal","tcp_end":[0.46639,-0.01811,0.05566],"tcp_start":[0.46642,-0.01797,0.05573],"tcp_to_object_dist_end":0.03167,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.47124,-0.0241,0.02499],"object_pos_start":[0.47136,-0.02419,0.025],"object_to_goal_dist_end":0.12914,"object_to_goal_dist_start":0.12903,"object_z_max":0.02537,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2056.0,"raw_peak_contact_force":24.01525,"tcp_end":[0.46328,-0.01807,0.14428],"tcp_start":[0.46639,-0.01811,0.05566],"tcp_to_object_dist_end":0.11971,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50459,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04025,"approach_1.approach_speed":0.08283,"contact_1.contact_force_threshold":7.52457,"contact_1.contact_speed":0.02454,"push_1.push_distance":0.24428,"push_1.push_speed":0.0611,"retract_1.retract_speed":0.13642},"optimized_scores":{"best_composite_score":0.04357,"best_fitness_score":0.20357,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.45639,-0.02514,0.04997],"force_p95":29.52793,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.11902,"mean_force":25.84179,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44621,-0.02488,0.0563]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.45608,-0.0252,0.05005],"force_p95":22.17808,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.01465,"mean_force":6.96531,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44591,-0.02497,0.05633]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.45027,-0.03158,-1e-05],"force_p95":12.94768,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.33925,"mean_force":6.6995,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44621,-0.02488,0.0563]},{"body_a":"world","body_b":"push_box","contact_count":2056.0,"contact_point_centroid":[0.44989,-0.03157,-1e-05],"force_p95":0.24543,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.20417,"mean_force":0.27523,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44307,-0.02486,0.10036]},{"body_a":"world","body_b":"push_box","contact_count":2876.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47433,-0.00077,0.18756]},{"body_a":"world","body_b":"push_box","contact_count":2036.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44643,-0.01525,0.06272]}],"total_contact_groups":6},"final_pose_error":0.01148,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45018,-0.03156,0.02499],"final_tcp_position":[0.44314,-0.02485,0.14516],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2876.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.44968,-0.00155,0.07503],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.44622,-0.02485,0.05634],"tcp_start":[0.44968,-0.00155,0.07503],"tcp_to_object_dist_end":0.03232,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.45027,-0.03158,0.02498],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12844,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":23.19815,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":30.11902,"subtask_id":"push_to_goal","tcp_end":[0.44618,-0.02494,0.05623],"tcp_start":[0.4462,-0.02491,0.05627],"tcp_to_object_dist_end":0.03221,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.45018,-0.03156,0.02499],"object_pos_start":[0.45026,-0.03158,0.02498],"object_to_goal_dist_end":0.12849,"object_to_goal_dist_start":0.12844,"object_z_max":0.02521,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2064.0,"raw_peak_contact_force":23.01465,"tcp_end":[0.44314,-0.02485,0.14516],"tcp_start":[0.44618,-0.02494,0.05623],"tcp_to_object_dist_end":0.12057,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03756,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05165,"approach_1.approach_speed":0.07241,"contact_1.contact_force_threshold":10.72977,"contact_1.contact_speed":0.00894,"push_1.push_distance":0.16235,"push_1.push_speed":0.03032,"retract_1.retract_speed":0.11103},"optimized_scores":{"best_composite_score":-0.00664,"best_fitness_score":0.40336,"best_task_score":0.03074},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":169.0,"contact_point_centroid":[0.537,-0.02884,0.04976],"force_p95":24.69205,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.9943,"mean_force":14.83515,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52739,-0.03414,0.05332]},{"body_a":"world","body_b":"push_box","contact_count":3341.0,"contact_point_centroid":[0.55646,-0.00771,-5e-05],"force_p95":6.046,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.85652,"mean_force":1.047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50985,-0.08751,0.04626]},{"body_a":"world","body_b":"push_box","contact_count":3052.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52202,0.01447,0.19146]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54431,0.01857,0.06881]},{"body_a":"world","body_b":"push_box","contact_count":2092.0,"contact_point_centroid":[0.55909,-0.00617,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48078,-0.16725,0.07866]}],"total_contact_groups":5},"final_pose_error":0.01249,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55909,-0.00617,0.02499],"final_tcp_position":[0.48087,-0.1672,0.12414],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":24.9943,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":763.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3052.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54636,0.02932,0.08362],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.54514,0.01266,0.06329],"tcp_start":[0.54636,0.02932,0.08362],"tcp_to_object_dist_end":0.04074,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55909,-0.00617,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15549,"object_to_goal_dist_start":0.16043,"object_z_max":0.03487,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3510.0,"raw_peak_contact_force":24.9943,"subtask_id":"push_to_goal","tcp_end":[0.48414,-0.16809,0.03616],"tcp_start":[0.54514,0.01266,0.06329],"tcp_to_object_dist_end":0.17878,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.55909,-0.00617,0.02499],"object_pos_start":[0.55909,-0.00617,0.02499],"object_to_goal_dist_end":0.15549,"object_to_goal_dist_start":0.15549,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48087,-0.1672,0.12414],"tcp_start":[0.48414,-0.16809,0.03616],"tcp_to_object_dist_end":0.20464,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```