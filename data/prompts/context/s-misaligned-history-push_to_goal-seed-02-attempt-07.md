## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4  | 0.6074 | 0.96 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4  | 0.6556 | 0.85 | ❌ rejected |
| 5 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.9115 | 0.83 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5  | 1.0065 | 0.94 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5  | 0.6145 | 0.97 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.97). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.971, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.614) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: behind_above
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: behind_at_height
  anchor: object
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_behind
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
    - 0.1
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: behind_above
- id: descend_to_pushing_height
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: behind_at_height
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_pushing_height** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.614
- **task_score** (E): 0.971
- **fitness_score**: 0.844  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1670 |
| descend_to_pushing_height | 1.00 | 1.00 | 0.1093 |
| push_to_goal | 1.00 | 1.00 | 0.1363 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.487, 0.017, 0.143) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_pushing_height | descend | 1.00 / step_budget | (0.487, 0.017, 0.143)→(0.484, 0.019, 0.034) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.246 | 58.832 |
| push_to_goal | push | 1.00 / step_budget | (0.484, 0.019, 0.034)→(0.489, -0.110, 0.029) | (0.492, -0.018, 0.025)→(0.502, -0.146, 0.025) | 0.139→0.004 | 1.00 / 3.000 | 2.284 | 63.025 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.991
- lateral_force_integral: None
- approach_alignment: 0.680
- goal_progress: 0.991
- terminal_score: 0.991
- phase_score: 0.768
- phase_breakdown.push_to_goal_score: 0.991
- phase_breakdown.behind_at_height_score: 0.435
- phase_breakdown.behind_above_score: 0.431

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.857
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.991
- **Median Q (composite search score)**: 0.609
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.230


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42647,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.18709,"descend_to_pushing_height.descend_speed":0.09258,"push_to_goal.push_distance":0.14767,"push_to_goal.push_speed":0.19087},"optimized_scores":{"best_composite_score":0.6272,"best_fitness_score":0.8572,"best_task_score":0.99116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":198.0,"contact_point_centroid":[0.4784,-0.06347,0.04202],"force_p95":48.7071,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.56806,"mean_force":8.09336,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47107,-0.0517,0.03033]},{"body_a":"world","body_b":"push_box","contact_count":318.0,"contact_point_centroid":[0.48026,-0.08692,-0.0001],"force_p95":29.87685,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.10793,"mean_force":5.5967,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46761,-0.03462,0.03093]},{"body_a":"world","body_b":"push_box","contact_count":1136.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48264,0.00614,0.2235]},{"body_a":"world","body_b":"push_box","contact_count":1436.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_pushing_height","phase_type":"descend","tcp_position_centroid":[0.46091,0.0135,0.08895]}],"total_contact_groups":4},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49977,-0.14889,0.02493],"final_tcp_position":[0.48411,-0.112,0.02939],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":82.56806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":630.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_above","tcp_end":[0.46507,0.01272,0.14432],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":810.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_pushing_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.24525,"subtask_id":"behind_at_height","tcp_end":[0.45895,0.0144,0.03425],"tcp_start":[0.46507,0.01272,0.14432],"tcp_to_object_dist_end":0.04158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":315.0,"n_steps_budget":600.0,"object_pos_end":[0.49977,-0.14889,0.02493],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00114,"object_to_goal_dist_start":0.12903,"object_z_max":0.027,"peak_contact_force":4.31237,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":516.0,"raw_peak_contact_force":82.56806,"subtask_id":"push_to_goal","tcp_end":[0.48411,-0.112,0.02939],"tcp_start":[0.45895,0.0144,0.03425],"tcp_to_object_dist_end":0.04032,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13889,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.19832,"descend_to_pushing_height.descend_speed":0.11735,"push_to_goal.push_distance":0.14297,"push_to_goal.push_speed":0.1021},"optimized_scores":{"best_composite_score":0.60923,"best_fitness_score":0.83923,"best_task_score":0.96807},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.43432,-0.0067,0.04997],"force_p95":77.27261,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.55314,"mean_force":48.46219,"phase_index":1.0,"phase_name":"descend_to_pushing_height","phase_type":"descend","tcp_position_centroid":[0.4328,0.00507,0.05093]},{"body_a":"attachment","body_b":"push_box","contact_count":199.0,"contact_point_centroid":[0.4634,-0.06448,0.04631],"force_p95":39.58014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.18554,"mean_force":9.73207,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45343,-0.05247,0.03087]},{"body_a":"world","body_b":"push_box","contact_count":349.0,"contact_point_centroid":[0.47517,-0.10294,-6e-05],"force_p95":22.26212,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.16574,"mean_force":6.16152,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45291,-0.05089,0.03104]},{"body_a":"world","body_b":"push_box","contact_count":1405.0,"contact_point_centroid":[0.45005,-0.03189,-1e-05],"force_p95":0.24618,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.32659,"mean_force":0.45472,"phase_index":1.0,"phase_name":"descend_to_pushing_height","phase_type":"descend","tcp_position_centroid":[0.43533,0.00482,0.08914]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.49664,-0.06422,0.05092],"force_p95":4.00204,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.19235,"mean_force":0.95499,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45228,-0.05024,0.03068]},{"body_a":"world","body_b":"push_box","contact_count":1164.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47083,0.0022,0.22299]}],"total_contact_groups":6},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49965,-0.14592,0.02528],"final_tcp_position":[0.47743,-0.10977,0.03004],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":84.55314,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_above","tcp_end":[0.44088,0.00454,0.14386],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":660.0,"object_pos_end":[0.45028,-0.03189,0.02498],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12815,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24521,"phase_name":"descend_to_pushing_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1411.0,"raw_peak_contact_force":84.55314,"subtask_id":"behind_at_height","tcp_end":[0.43184,0.00523,0.03453],"tcp_start":[0.44088,0.00454,0.14386],"tcp_to_object_dist_end":0.04254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":335.0,"n_steps_budget":900.0,"object_pos_end":[0.49965,-0.14592,0.02528],"object_pos_start":[0.45028,-0.03189,0.02498],"object_to_goal_dist_end":0.0041,"object_to_goal_dist_start":0.12815,"object_z_max":0.02591,"peak_contact_force":1.18997,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":554.0,"raw_peak_contact_force":52.18554,"subtask_id":"push_to_goal","tcp_end":[0.47743,-0.10977,0.03004],"tcp_start":[0.43184,0.00523,0.03453],"tcp_to_object_dist_end":0.0427,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11364,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.20837,"descend_to_pushing_height.descend_speed":0.09127,"push_to_goal.push_distance":0.17447,"push_to_goal.push_speed":0.08748},"optimized_scores":{"best_composite_score":0.60695,"best_fitness_score":0.83695,"best_task_score":0.95234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.56157,0.02612,0.04969],"force_p95":88.15813,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.69866,"mean_force":55.02697,"phase_index":1.0,"phase_name":"descend_to_pushing_height","phase_type":"descend","tcp_position_centroid":[0.55962,0.03757,0.05008]},{"body_a":"world","body_b":"push_box","contact_count":1292.0,"contact_point_centroid":[0.55273,0.00066,-1e-05],"force_p95":0.48753,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.11196,"mean_force":0.67966,"phase_index":1.0,"phase_name":"descend_to_pushing_height","phase_type":"descend","tcp_position_centroid":[0.55683,0.03599,0.08754]},{"body_a":"attachment","body_b":"push_box","contact_count":210.0,"contact_point_centroid":[0.53469,-0.04913,0.03819],"force_p95":35.96417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.32142,"mean_force":6.63232,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53051,-0.03733,0.02837]},{"body_a":"world","body_b":"push_box","contact_count":382.0,"contact_point_centroid":[0.52921,-0.07941,-9e-05],"force_p95":17.32137,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.17655,"mean_force":4.185,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53283,-0.03137,0.02862]},{"body_a":"world","body_b":"push_box","contact_count":1264.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52677,0.0166,0.22124]}],"total_contact_groups":5},"final_pose_error":0.01963,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50519,-0.1444,0.02467],"final_tcp_position":[0.50536,-0.10729,0.02809],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":91.69866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_above","tcp_end":[0.5556,0.03408,0.14087],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":810.0,"object_pos_end":[0.55346,0.00097,0.02497],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16016,"object_to_goal_dist_start":0.16043,"object_z_max":0.02501,"peak_contact_force":0.24633,"phase_name":"descend_to_pushing_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1302.0,"raw_peak_contact_force":91.69866,"subtask_id":"behind_at_height","tcp_end":[0.56101,0.03839,0.03319],"tcp_start":[0.5556,0.03408,0.14087],"tcp_to_object_dist_end":0.03905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50519,-0.1444,0.02467],"object_pos_start":[0.55346,0.00097,0.02497],"object_to_goal_dist_end":0.00765,"object_to_goal_dist_start":0.16016,"object_z_max":0.02605,"peak_contact_force":1.3497,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":592.0,"raw_peak_contact_force":54.32142,"subtask_id":"push_to_goal","tcp_end":[0.50536,-0.10729,0.02809],"tcp_start":[0.56101,0.03839,0.03319],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```