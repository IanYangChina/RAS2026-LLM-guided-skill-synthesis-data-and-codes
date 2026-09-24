## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.7461 | 0.95 | ✅ accepted |
| 12 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.2000 | 0.00 | ❌ rejected |
| 11 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.7272 | 0.93 | ✅ accepted |
| 10 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 9 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.946, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.746) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: push_to_goal
  target_entity: object
  metric: goal_progress
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: push_object
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
      distance: 0.2
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
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_object** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.746
- **task_score** (E): 0.946
- **fitness_score**: 0.946  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_behind | 1.00 | 0.2770 |
| push_object | 1.00 | 0.1753 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.483, 0.049, 0.037) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 |
| push_object | push | 1.00 / step_budget | (0.483, 0.049, 0.037)→(0.489, -0.116, 0.032) | (0.492, -0.018, 0.025)→(0.507, -0.151, 0.027) | 0.139→0.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- approach_alignment: 0.671
- goal_progress: 0.986
- terminal_score: 0.986
- phase_score: 0.986
- phase_breakdown.push_to_goal_score: 0.986

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.986
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.778
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.81395,"average_solve_count":43.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.05761,"approach_behind.approach_speed":0.26511,"push_object.push_distance":0.16461,"push_object.push_speed":0.17438},"optimized_scores":{"best_composite_score":0.77763,"best_fitness_score":0.97763,"best_task_score":0.97763},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.48028,-0.06159,0.04424],"force_p95":53.64064,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.01649,"mean_force":9.84808,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.47218,-0.04983,0.03223]},{"body_a":"world","body_b":"push_box","contact_count":453.0,"contact_point_centroid":[0.48008,-0.06972,-8e-05],"force_p95":26.58958,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.43516,"mean_force":4.73681,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.46574,-0.01899,0.03312]},{"body_a":"world","body_b":"push_box","contact_count":2568.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47835,0.01456,0.1698]}],"total_contact_groups":3},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49944,-0.14829,0.02726],"final_tcp_position":[0.48616,-0.11293,0.03156],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"phases":[{"n_steps":642.0,"n_steps_budget":690.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"push_to_goal","tcp_end":[0.45709,0.02987,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05706,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":348.0,"n_steps_budget":600.0,"object_pos_end":[0.49944,-0.14829,0.02726],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00289,"object_to_goal_dist_start":0.12903,"object_z_max":0.02766,"phase_name":"push_object","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48616,-0.11293,0.03156],"tcp_start":[0.45709,0.02987,0.03637],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.025,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.08321,"approach_behind.approach_speed":0.39843,"push_object.push_distance":0.18763,"push_object.push_speed":0.21204},"optimized_scores":{"best_composite_score":0.78617,"best_fitness_score":0.98617,"best_task_score":0.98617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":170.0,"contact_point_centroid":[0.46259,-0.06322,0.04424],"force_p95":41.79663,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.72646,"mean_force":7.20298,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.45607,-0.05146,0.03503]},{"body_a":"world","body_b":"push_box","contact_count":653.0,"contact_point_centroid":[0.46246,-0.06719,-6e-05],"force_p95":14.08995,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.25981,"mean_force":2.29434,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.44007,-0.01208,0.03591]},{"body_a":"world","body_b":"push_box","contact_count":2236.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46083,0.02013,0.17285]}],"total_contact_groups":3},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50133,-0.15118,0.02502],"final_tcp_position":[0.48253,-0.11481,0.03441],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"phases":[{"n_steps":559.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"push_to_goal","tcp_end":[0.41996,0.04184,0.03919],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0807,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":399.0,"n_steps_budget":600.0,"object_pos_end":[0.50133,-0.15118,0.02502],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00178,"object_to_goal_dist_start":0.12843,"object_z_max":0.02775,"phase_name":"push_object","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.48253,-0.11481,0.03441],"tcp_start":[0.41996,0.04184,0.03919],"tcp_to_object_dist_end":0.042,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.86,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.08596,"approach_behind.approach_speed":0.30879,"push_object.push_distance":0.23037,"push_object.push_speed":0.16683},"optimized_scores":{"best_composite_score":0.67464,"best_fitness_score":0.87464,"best_task_score":0.87464},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":214.0,"contact_point_centroid":[0.53872,-0.04511,0.04424],"force_p95":58.04029,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.62918,"mean_force":10.2979,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.52998,-0.03412,0.0308]},{"body_a":"world","body_b":"push_box","contact_count":733.0,"contact_point_centroid":[0.54936,-0.04968,-0.00012],"force_p95":24.03283,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.97159,"mean_force":4.24579,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.54384,0.00404,0.0315]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.54924,-0.09162,0.05945],"force_p95":62.79248,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.08038,"mean_force":16.90533,"phase_index":1.0,"phase_name":"push_object","phase_type":"push","tcp_position_centroid":[0.51206,-0.08531,0.0312]},{"body_a":"world","body_b":"push_box","contact_count":2356.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53442,0.03685,0.17169]}],"total_contact_groups":4},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51963,-0.15369,0.02732],"final_tcp_position":[0.49942,-0.12156,0.03151],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":589.0,"n_steps_budget":630.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"push_to_goal","tcp_end":[0.57276,0.07673,0.03611],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07866,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":461.0,"n_steps_budget":870.0,"object_pos_end":[0.51963,-0.15369,0.02732],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02011,"object_to_goal_dist_start":0.16043,"object_z_max":0.03306,"phase_name":"push_object","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49942,-0.12156,0.03151],"tcp_start":[0.57276,0.07673,0.03611],"tcp_to_object_dist_end":0.03819,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```