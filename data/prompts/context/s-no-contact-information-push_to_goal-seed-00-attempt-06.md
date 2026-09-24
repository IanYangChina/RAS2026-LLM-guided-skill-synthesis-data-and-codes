## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5823 | 0.95 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.3045 | 0.47 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.7646 | 0.96 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.6241 | 0.80 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.7787 | 0.95 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.961, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.582) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
  weight: 0.3
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: body
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.015
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: body
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=body, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=replace_offset_projection, sign=negative}, tolerance=0.015
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=body, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.582
- **task_score** (E): 0.948
- **fitness_score**: 0.812  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| descend_to_pre_contact | 1.00 | 0.1858 |
| move_behind_object | 1.00 | 0.0950 |
| push_to_goal | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| descend_to_pre_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.119) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 |
| move_behind_object | approach | 1.00 / step_budget | (0.494, 0.001, 0.119)→(0.495, 0.048, 0.037) | (0.496, 0.001, 0.025)→(0.497, 0.005, 0.028) | 0.152→0.157 |
| push_to_goal | push | 1.00 / step_budget | (0.495, 0.048, 0.037)→(0.497, -0.115, 0.023) | (0.497, 0.005, 0.028)→(0.504, -0.152, 0.028) | 0.157→0.008 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.985
- approach_alignment: 0.679
- goal_progress: 0.963
- terminal_score: 0.963
- phase_score: 0.735
- phase_breakdown.reach_goal_score: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.826
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.963
- **Median Q (composite search score)**: 0.579
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.452


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38217,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_pre_contact.approach_speed":0.09373,"move_behind_object.lateral_speed":0.0915,"push_to_goal.push_distance":0.11158,"push_to_goal.push_speed":0.03568},"optimized_scores":{"best_composite_score":0.57211,"best_fitness_score":0.80211,"best_task_score":0.93402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":27.0,"contact_point_centroid":[0.52257,-0.00214,0.04876],"force_p95":162.27007,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":209.36538,"mean_force":111.49477,"phase_index":1.0,"phase_name":"move_behind_object","phase_type":"approach","tcp_position_centroid":[0.51691,0.0073,0.05047]},{"body_a":"world","body_b":"push_box","contact_count":879.0,"contact_point_centroid":[0.51651,-0.02726,-4e-05],"force_p95":20.20157,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.87168,"mean_force":3.70776,"phase_index":1.0,"phase_name":"move_behind_object","phase_type":"approach","tcp_position_centroid":[0.51348,-0.00708,0.07905]},{"body_a":"attachment","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.51222,-0.06782,0.03744],"force_p95":37.03909,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.21067,"mean_force":6.63286,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5072,-0.05598,0.02678]},{"body_a":"world","body_b":"push_box","contact_count":487.0,"contact_point_centroid":[0.51189,-0.08315,-8e-05],"force_p95":16.15655,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.02435,"mean_force":3.79934,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5098,-0.03732,0.0289]},{"body_a":"world","body_b":"push_box","contact_count":1776.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_pre_contact","phase_type":"approach","tcp_position_centroid":[0.50495,-0.0121,0.21044]}],"total_contact_groups":5},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50459,-0.15665,0.02604],"final_tcp_position":[0.49974,-0.11967,0.02135],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"phases":[{"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"phase_name":"descend_to_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.51165,-0.0249,0.11881],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09398,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":236.0,"n_steps_budget":750.0,"object_pos_end":[0.51648,-0.02842,0.02473],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12269,"object_to_goal_dist_start":0.12347,"object_z_max":0.02508,"phase_name":"move_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.51878,0.01436,0.03704],"tcp_start":[0.51165,-0.0249,0.11881],"tcp_to_object_dist_end":0.04457,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.50459,-0.15665,0.02604],"object_pos_start":[0.51648,-0.02842,0.02473],"object_to_goal_dist_end":0.00815,"object_to_goal_dist_start":0.12269,"object_z_max":0.02627,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49974,-0.11967,0.02135],"tcp_start":[0.51878,0.01436,0.03704],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21505,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_pre_contact.approach_speed":0.13777,"move_behind_object.lateral_speed":0.06499,"push_to_goal.push_distance":0.20455,"push_to_goal.push_speed":0.02844},"optimized_scores":{"best_composite_score":0.57874,"best_fitness_score":0.80874,"best_task_score":0.94731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":128.0,"contact_point_centroid":[0.51075,0.09059,0.04367],"force_p95":207.31758,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":229.27962,"mean_force":170.29392,"phase_index":1.0,"phase_name":"move_behind_object","phase_type":"approach","tcp_position_centroid":[0.50321,0.09813,0.0455]},{"body_a":"world","body_b":"push_box","contact_count":1026.0,"contact_point_centroid":[0.50174,0.05963,-0.00018],"force_p95":137.5628,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.22398,"mean_force":21.58315,"phase_index":1.0,"phase_name":"move_behind_object","phase_type":"approach","tcp_position_centroid":[0.49825,0.0733,0.07609]},{"body_a":"world","body_b":"push_box","contact_count":558.0,"contact_point_centroid":[0.50936,-0.06686,-0.00014],"force_p95":61.21313,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.21086,"mean_force":15.75035,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5001,-0.01363,0.0272]},{"body_a":"attachment","body_b":"push_box","contact_count":446.0,"contact_point_centroid":[0.5075,-0.02052,0.04018],"force_p95":65.03366,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.20664,"mean_force":14.70777,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50019,-0.00916,0.0274]},{"body_a":"push_box","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.52901,-0.08188,0.05676],"force_p95":62.0049,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.76092,"mean_force":19.52643,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49953,-0.05666,0.0255]},{"body_a":"world","body_b":"push_box","contact_count":1768.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_pre_contact","phase_type":"approach","tcp_position_centroid":[0.49842,0.02376,0.20983]}],"total_contact_groups":6},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50981,-0.15071,0.02935],"final_tcp_position":[0.5002,-0.11497,0.02419],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"phases":[{"n_steps":442.0,"n_steps_budget":930.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"phase_name":"descend_to_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.49816,0.04871,0.11828],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0935,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50291,0.06957,0.03448],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.2198,"object_to_goal_dist_start":0.20406,"object_z_max":0.03444,"phase_name":"move_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.50635,0.11156,0.03726],"tcp_start":[0.49816,0.04871,0.11828],"tcp_to_object_dist_end":0.04222,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.50981,-0.15071,0.02935],"object_pos_start":[0.50291,0.06957,0.03448],"object_to_goal_dist_end":0.01075,"object_to_goal_dist_start":0.2198,"object_z_max":0.03586,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.5002,-0.11497,0.02419],"tcp_start":[0.50635,0.11156,0.03726],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28333,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_pre_contact.approach_speed":0.14967,"move_behind_object.lateral_speed":0.05573,"push_to_goal.push_distance":0.10914,"push_to_goal.push_speed":0.05913},"optimized_scores":{"best_composite_score":0.59617,"best_fitness_score":0.82617,"best_task_score":0.96295},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":30.0,"contact_point_centroid":[0.46673,0.00109,0.04872],"force_p95":170.11205,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":190.00968,"mean_force":121.25609,"phase_index":1.0,"phase_name":"move_behind_object","phase_type":"approach","tcp_position_centroid":[0.46128,0.01029,0.05129]},{"body_a":"world","body_b":"push_box","contact_count":961.0,"contact_point_centroid":[0.47186,-0.02344,-5e-05],"force_p95":30.76553,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.69265,"mean_force":4.0432,"phase_index":1.0,"phase_name":"move_behind_object","phase_type":"approach","tcp_position_centroid":[0.46438,-0.00341,0.07883]},{"body_a":"attachment","body_b":"push_box","contact_count":270.0,"contact_point_centroid":[0.49183,-0.07263,0.0486],"force_p95":74.01285,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.14027,"mean_force":30.37274,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4772,-0.06172,0.02751]},{"body_a":"world","body_b":"push_box","contact_count":558.0,"contact_point_centroid":[0.49093,-0.09578,-0.00012],"force_p95":57.03214,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.70414,"mean_force":18.71428,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47308,-0.04485,0.02927]},{"body_a":"push_box","body_b":"link7","contact_count":142.0,"contact_point_centroid":[0.51351,-0.10814,0.05576],"force_p95":61.06715,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.54459,"mean_force":25.64307,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48455,-0.08874,0.02533]},{"body_a":"world","body_b":"push_box","contact_count":1648.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_pre_contact","phase_type":"approach","tcp_position_centroid":[0.48525,-0.01061,0.21061]}],"total_contact_groups":6},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49885,-0.14826,0.0293],"final_tcp_position":[0.4917,-0.11169,0.02399],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"phases":[{"n_steps":412.0,"n_steps_budget":840.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"phase_name":"descend_to_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.47112,-0.02178,0.11955],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09459,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.47181,-0.0247,0.0249],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12844,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"phase_name":"move_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.45996,0.01733,0.03803],"tcp_start":[0.47112,-0.02178,0.11955],"tcp_to_object_dist_end":0.0456,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.49885,-0.14826,0.0293],"object_pos_start":[0.47181,-0.0247,0.0249],"object_to_goal_dist_end":0.00478,"object_to_goal_dist_start":0.12844,"object_z_max":0.02965,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.4917,-0.11169,0.02399],"tcp_start":[0.45996,0.01733,0.03803],"tcp_to_object_dist_end":0.03763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```