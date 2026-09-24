## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1085 | 0.00 | ❌ rejected |
| 1 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ✅ accepted |

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

## Current Skill (Q=0.109) — your mutation base

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

- **Composite score**: 0.109
- **task_score** (E): 0.001
- **fitness_score**: 0.339  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2029 |
| descend | 1.00 | 1.00 | 0.0547 |
| push | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, -0.017, 0.104) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.489, -0.017, 0.104)→(0.490, -0.018, 0.049) | (0.492, -0.018, 0.025)→(0.493, -0.018, 0.024) | 0.139→0.139 | 1.00 / 5.000 | 164.261 | 164.261 |
| push | push | 0.00 / guard_failure | (0.490, -0.018, 0.049)→(0.490, -0.018, 0.049) | (0.493, -0.018, 0.024)→(0.493, -0.018, 0.024) | 0.139→0.139 | 1.00 / 5.000 | 71.172 | 71.172 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.008
- lateral_force_integral: None
- approach_alignment: 0.518
- goal_progress: 0.003
- terminal_score: 0.003
- phase_score: 0.575
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_above_score: 0.949
- phase_breakdown.contact_object_score: 0.968

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.346
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: 0.109
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70769,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.height":0.06763,"descend.contact_z":0.01509,"push.push_distance":0.21075,"push.push_speed":0.22592},"optimized_scores":{"best_composite_score":0.10943,"best_fitness_score":0.33943,"best_task_score":0.00102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.4799,-0.02369,0.04908],"force_p95":142.40078,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.92632,"mean_force":113.25267,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.46815,-0.02372,0.05088]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48075,-0.02373,0.04833],"force_p95":66.89113,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.89113,"mean_force":66.89113,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46899,-0.02379,0.04969]},{"body_a":"world","body_b":"push_box","contact_count":756.0,"contact_point_centroid":[0.4714,-0.02418,-1e-05],"force_p95":12.43503,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.29434,"mean_force":2.50158,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.46809,-0.0231,0.07531]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47157,-0.02421,-0.00025],"force_p95":35.08397,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.66686,"mean_force":16.86195,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46899,-0.02379,0.04969]},{"body_a":"world","body_b":"push_box","contact_count":2488.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48443,-0.01105,0.20117]}],"total_contact_groups":5},"final_pose_error":0.21318,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47182,-0.02422,0.02451],"final_tcp_position":[0.46905,-0.02379,0.04966],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":144.92632,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":622.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2488.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_above","tcp_end":[0.47008,-0.0225,0.10216],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":189.0,"n_steps_budget":600.0,"object_pos_end":[0.47185,-0.02422,0.02451],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1289,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":144.92632,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":771.0,"raw_peak_contact_force":144.92632,"subtask_id":"contact_object","tcp_end":[0.46899,-0.02379,0.04969],"tcp_start":[0.47008,-0.0225,0.10216],"tcp_to_object_dist_end":0.02535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47182,-0.02422,0.02451],"object_pos_start":[0.47185,-0.02422,0.02451],"object_to_goal_dist_end":0.1289,"object_to_goal_dist_start":0.1289,"object_z_max":0.02451,"peak_contact_force":66.89113,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":66.89113,"subtask_id":"push_to_goal","tcp_end":[0.46905,-0.02379,0.04966],"tcp_start":[0.46899,-0.02379,0.04969],"tcp_to_object_dist_end":0.02531,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70769,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.height":0.06884,"descend.contact_z":0.01395,"push.push_distance":0.29191,"push.push_speed":0.18993},"optimized_scores":{"best_composite_score":0.11623,"best_fitness_score":0.34623,"best_task_score":0.00297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.45967,-0.03096,0.04875],"force_p95":173.00626,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.34241,"mean_force":138.10364,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.44791,-0.03099,0.05035]},{"body_a":"world","body_b":"push_box","contact_count":816.0,"contact_point_centroid":[0.4503,-0.03159,-2e-05],"force_p95":26.15243,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.65174,"mean_force":4.1561,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.448,-0.03017,0.07507]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.46104,-0.03106,0.04778],"force_p95":61.69792,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.69792,"mean_force":61.69792,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44926,-0.03113,0.04883]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.45068,-0.03164,-0.00035],"force_p95":32.41728,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.97819,"mean_force":15.55424,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44926,-0.03113,0.04883]},{"body_a":"world","body_b":"push_box","contact_count":2512.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47481,-0.01444,0.20176]}],"total_contact_groups":5},"final_pose_error":0.29396,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45108,-0.03166,0.02431],"final_tcp_position":[0.44933,-0.03114,0.04883],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":174.34241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2512.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_above","tcp_end":[0.45048,-0.02937,0.10359],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.45111,-0.03166,0.0243],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12804,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":174.34241,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":839.0,"raw_peak_contact_force":174.34241,"subtask_id":"contact_object","tcp_end":[0.44926,-0.03113,0.04883],"tcp_start":[0.45048,-0.02937,0.10359],"tcp_to_object_dist_end":0.02461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.45108,-0.03166,0.02431],"object_pos_start":[0.45111,-0.03166,0.0243],"object_to_goal_dist_end":0.12805,"object_to_goal_dist_start":0.12804,"object_z_max":0.0243,"peak_contact_force":61.69792,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":61.69792,"subtask_id":"push_to_goal","tcp_end":[0.44933,-0.03114,0.04883],"tcp_start":[0.44926,-0.03113,0.04883],"tcp_to_object_dist_end":0.02459,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84375,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.height":0.07274,"descend.contact_z":0.01332,"push.push_distance":0.20134,"push.push_speed":0.29544},"optimized_scores":{"best_composite_score":0.09987,"best_fitness_score":0.32987,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.5613,0.00125,0.04833],"force_p95":173.33632,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.51356,"mean_force":149.2795,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54954,0.00122,0.04968]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56408,0.00134,0.04743],"force_p95":84.928,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.928,"mean_force":84.928,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.55228,0.00123,0.04824]},{"body_a":"world","body_b":"push_box","contact_count":812.0,"contact_point_centroid":[0.55324,0.00136,-4e-05],"force_p95":72.31934,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.40115,"mean_force":6.72212,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54653,0.00119,0.07357]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.5541,0.00136,-0.00039],"force_p95":41.79879,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.25314,"mean_force":21.33977,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.55228,0.00123,0.04824]},{"body_a":"world","body_b":"push_box","contact_count":2660.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52202,0.00058,0.20205]}],"total_contact_groups":5},"final_pose_error":0.20178,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55464,0.00135,0.02421],"final_tcp_position":[0.55238,0.00123,0.04824],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":173.51356,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_above","tcp_end":[0.54628,0.00119,0.10476],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":203.0,"n_steps_budget":600.0,"object_pos_end":[0.55467,0.00136,0.0242],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16093,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":173.51356,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":847.0,"raw_peak_contact_force":173.51356,"subtask_id":"contact_object","tcp_end":[0.55228,0.00123,0.04824],"tcp_start":[0.54628,0.00119,0.10476],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.55464,0.00135,0.02421],"object_pos_start":[0.55467,0.00136,0.0242],"object_to_goal_dist_end":0.16092,"object_to_goal_dist_start":0.16093,"object_z_max":0.0242,"peak_contact_force":84.928,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":84.928,"subtask_id":"push_to_goal","tcp_end":[0.55238,0.00123,0.04824],"tcp_start":[0.55228,0.00123,0.04824],"tcp_to_object_dist_end":0.02413,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```