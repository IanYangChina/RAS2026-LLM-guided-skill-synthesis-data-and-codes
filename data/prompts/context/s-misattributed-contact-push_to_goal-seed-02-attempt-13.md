## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5917 | 0.75 | ❌ rejected |
| 12 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.6404 | 0.82 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0982 | 0.03 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.6483 | 0.86 | ✅ accepted |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5117 | 0.66 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.857, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.592) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object_high
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: descend_to_table
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object_high
- id: align_behind_object
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_side_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: push_along_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_stroke_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_to_table** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **align_behind_object** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_side_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_along_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_stroke_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.592
- **task_score** (E): 0.752
- **fitness_score**: 0.772  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_table | 1.00 | 1.00 | 0.1995 |
| align_behind_object | 1.00 | 1.00 | 0.0890 |
| push_along_goal | 1.00 | 1.00 | 0.3100 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_table | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.016, 0.106) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind_object | align | 1.00 / step_budget | (0.490, -0.016, 0.106)→(0.487, 0.052, 0.057) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 158.166 |
| push_along_goal | push | 1.00 / step_budget | (0.487, 0.052, 0.057)→(0.500, -0.240, 0.021) | (0.492, -0.018, 0.025)→(0.510, -0.127, 0.025) | 0.139→0.033 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.960
- lateral_force_integral: None
- approach_alignment: 0.838
- goal_progress: 0.857
- terminal_score: 0.857
- phase_score: 0.851
- phase_breakdown.push_to_goal_score: 0.857
- phase_breakdown.reach_object_high_score: 0.835

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.853
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.857
- **Median Q (composite search score)**: 0.565
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.578


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.928,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.07708,"descend_to_table.approach_height":0.05761,"push_along_goal.push_stroke_distance":0.09742},"optimized_scores":{"best_composite_score":0.53654,"best_fitness_score":0.71654,"best_task_score":0.67063},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2513.0,"contact_point_centroid":[0.48323,-0.07165,-0.00029],"force_p95":149.96388,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.21993,"mean_force":30.00528,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.48497,-0.08638,0.04291]},{"body_a":"attachment","body_b":"push_box","contact_count":506.0,"contact_point_centroid":[0.48964,-0.05095,0.0473],"force_p95":191.03523,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.06291,"mean_force":146.98139,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.48048,-0.05193,0.05044]},{"body_a":"world","body_b":"push_box","contact_count":1544.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.48559,-0.01041,0.20258]},{"body_a":"world","body_b":"push_box","contact_count":604.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.46298,0.00439,0.08]}],"total_contact_groups":4},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48649,-0.10971,0.02499],"final_tcp_position":[0.51375,-0.22732,0.0209],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":204.21993,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":604.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.47158,-0.02146,0.10227],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3019.0,"raw_peak_contact_force":204.21993,"tcp_end":[0.45539,0.03318,0.05853],"tcp_start":[0.47158,-0.02146,0.10227],"tcp_to_object_dist_end":0.06835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.48649,-0.10971,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.0425,"object_to_goal_dist_start":0.12903,"object_z_max":0.03474,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.51375,-0.22732,0.0209],"tcp_start":[0.45539,0.03318,0.05853],"tcp_to_object_dist_end":0.1208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92913,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.08027,"descend_to_table.approach_height":0.06889,"push_along_goal.push_stroke_distance":0.10565},"optimized_scores":{"best_composite_score":0.56516,"best_fitness_score":0.74516,"best_task_score":0.72721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":451.0,"contact_point_centroid":[0.47379,-0.05579,0.04724],"force_p95":191.53222,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.40955,"mean_force":144.39257,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.46455,-0.05773,0.05115]},{"body_a":"world","body_b":"push_box","contact_count":2190.0,"contact_point_centroid":[0.48672,-0.07833,-0.00031],"force_p95":163.36113,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.60886,"mean_force":30.75091,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.47556,-0.09344,0.04287]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.53622,-0.11831,0.0647],"force_p95":48.32447,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.35048,"mean_force":23.78843,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.49634,-0.14445,0.0372]},{"body_a":"world","body_b":"push_box","contact_count":1488.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.47665,-0.01352,0.20803]},{"body_a":"world","body_b":"push_box","contact_count":656.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.43832,-0.00217,0.08679]}],"total_contact_groups":5},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52161,-0.12242,0.02499],"final_tcp_position":[0.53045,-0.23119,0.02047],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":201.40955,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.45312,-0.02789,0.11328],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":164.0,"n_steps_budget":660.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2695.0,"raw_peak_contact_force":201.40955,"tcp_end":[0.42396,0.02626,0.06069],"tcp_start":[0.45312,-0.02789,0.11328],"tcp_to_object_dist_end":0.07289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.52161,-0.12242,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.03504,"object_to_goal_dist_start":0.12843,"object_z_max":0.03922,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.53045,-0.23119,0.02047],"tcp_start":[0.42396,0.02626,0.06069],"tcp_to_object_dist_end":0.10923,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94194,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.11732,"descend_to_table.approach_height":0.06099,"push_along_goal.push_stroke_distance":0.13793},"optimized_scores":{"best_composite_score":0.67344,"best_fitness_score":0.85344,"best_task_score":0.85743},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":308.0,"contact_point_centroid":[0.53385,-0.07266,0.05023],"force_p95":45.88019,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.86842,"mean_force":9.93911,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.52337,-0.06439,0.03473]},{"body_a":"world","body_b":"push_box","contact_count":2102.0,"contact_point_centroid":[0.5402,-0.09272,-7e-05],"force_p95":13.65663,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.75209,"mean_force":1.85712,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.514,-0.09251,0.03303]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53929,-0.10693,0.06077],"force_p95":17.00162,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.59539,"mean_force":8.82199,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.50299,-0.12446,0.03074]},{"body_a":"world","body_b":"push_box","contact_count":1596.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.52093,0.00055,0.20333]},{"body_a":"world","body_b":"push_box","contact_count":1100.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.56138,0.0476,0.07574]}],"total_contact_groups":5},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52287,-0.14956,0.02499],"final_tcp_position":[0.45663,-0.2609,0.021],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":68.86842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.54424,0.00112,0.10388],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":840.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2421.0,"raw_peak_contact_force":68.86842,"tcp_end":[0.58136,0.09554,0.05113],"tcp_start":[0.54424,0.00112,0.10388],"tcp_to_object_dist_end":0.10173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.52287,-0.14956,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02287,"object_to_goal_dist_start":0.16043,"object_z_max":0.0308,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.45663,-0.2609,0.021],"tcp_start":[0.58136,0.09554,0.05113],"tcp_to_object_dist_end":0.12961,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```