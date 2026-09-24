## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4678 | 0.98 | ✅ accepted |
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1453 | 0.51 | ❌ rejected |
| 7 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3607 | 0.83 | ✅ accepted |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2398 | 0.81 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1205 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.98). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.977, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.468) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_push_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_object
  type: approach
  generator: arc_cartesian
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
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: pre_push_approach
- id: push_object_to_goal
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_to_goal
- id: retract_from_object
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **push_object_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, entity=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_from_object** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.468
- **task_score** (E): 0.977
- **fitness_score**: 0.848  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_object | 1.00 | 1.00 | 0.2819 |
| push_object_to_goal | 1.00 | 1.00 | 0.1707 |
| retract_from_object | 1.00 | 1.00 | 0.0795 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, 0.059, 0.028) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 2.000 | 11.018 | 95.084 |
| push_object_to_goal | push | 1.00 / step_budget | (0.492, 0.059, 0.028)→(0.496, -0.110, 0.020) | (0.496, 0.001, 0.025)→(0.500, -0.147, 0.025) | 0.152→0.005 | 1.00 / 4.000 | 0.245 | 17.450 |
| retract_from_object | retract | 1.00 / step_budget | (0.496, -0.110, 0.020)→(0.493, -0.110, 0.100) | (0.500, -0.147, 0.025)→(0.500, -0.151, 0.025) | 0.005→0.004 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.736
- goal_progress: 0.977
- terminal_score: 0.977
- phase_score: 0.776
- phase_breakdown.pre_push_approach_score: 0.317
- phase_breakdown.push_to_goal_score: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.856
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.980
- **Median Q (composite search score)**: 0.466
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.234


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10569,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.1175,"approach_behind_object.approach_tolerance":0.01688,"approach_behind_object.arc_height":0.1344,"push_object_to_goal.push_speed":0.06969,"push_object_to_goal.push_tolerance":0.04269,"retract_from_object.retract_speed":0.10097,"retract_from_object.retract_tolerance":0.02707},"optimized_scores":{"best_composite_score":0.46646,"best_fitness_score":0.84646,"best_task_score":0.98006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.50972,-0.06161,0.02641],"force_p95":6.33029,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.93785,"mean_force":3.49192,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50738,-0.05021,0.01984]},{"body_a":"world","body_b":"push_box","contact_count":207.0,"contact_point_centroid":[0.51406,-0.05156,-4e-05],"force_p95":5.33255,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.20374,"mean_force":2.2356,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.51271,-0.0041,0.02126]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.53744,-0.05261,0.0515],"force_p95":21.86182,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.11369,"mean_force":5.01603,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50902,-0.0339,0.01979]},{"body_a":"world","body_b":"push_box","contact_count":552.0,"contact_point_centroid":[0.49913,-0.15169,-0.00018],"force_p95":0.76687,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.68026,"mean_force":0.32976,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49832,-0.10814,0.05909]},{"body_a":"world","body_b":"push_box","contact_count":3532.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.50722,0.08963,0.17086]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50063,-0.11974,0.01995],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.50144,-0.10779,0.01952]}],"total_contact_groups":6},"final_pose_error":0.02684,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49958,-0.14757,0.02499],"final_tcp_position":[0.49828,-0.1074,0.09287],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":94.93785,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":1.82296,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":326.0,"raw_peak_contact_force":94.93785,"subtask_id":"pre_push_approach","tcp_end":[0.51728,0.028,0.02338],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":168.0,"n_steps_budget":1000.0,"object_pos_end":[0.49974,-0.14472,0.02514],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.00529,"object_to_goal_dist_start":0.12347,"object_z_max":0.02726,"peak_contact_force":0.24526,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":553.0,"raw_peak_contact_force":2.68026,"subtask_id":"push_to_goal","tcp_end":[0.50144,-0.10779,0.01952],"tcp_start":[0.51728,0.028,0.02338],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":163.0,"n_steps_budget":630.0,"object_pos_end":[0.49958,-0.14757,0.02499],"object_pos_start":[0.49974,-0.14472,0.02514],"object_to_goal_dist_end":0.00246,"object_to_goal_dist_start":0.00529,"object_z_max":0.02746,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3532.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49828,-0.1074,0.09287],"tcp_start":[0.50144,-0.10779,0.01952],"tcp_to_object_dist_end":0.0789,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56425,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.08252,"approach_behind_object.approach_tolerance":0.01565,"approach_behind_object.arc_height":0.1246,"push_object_to_goal.push_speed":0.06057,"push_object_to_goal.push_tolerance":0.04179,"retract_from_object.retract_speed":0.11046,"retract_from_object.retract_tolerance":0.02302},"optimized_scores":{"best_composite_score":0.476,"best_fitness_score":0.856,"best_task_score":0.97654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":134.0,"contact_point_centroid":[0.50332,-0.02444,0.03525],"force_p95":85.23746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.10826,"mean_force":11.97817,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49648,-0.01318,0.02365]},{"body_a":"world","body_b":"push_box","contact_count":306.0,"contact_point_centroid":[0.50533,-0.00758,-7e-05],"force_p95":39.61317,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.55473,"mean_force":6.21669,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49646,0.03921,0.02589]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.53098,-0.0365,0.05193],"force_p95":30.99396,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.82133,"mean_force":7.11071,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49655,-0.02031,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":758.0,"contact_point_centroid":[0.50218,-0.15514,-2e-05],"force_p95":0.45962,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.334,"mean_force":0.27905,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.4938,-0.10896,0.0608]},{"body_a":"world","body_b":"push_box","contact_count":3936.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.49809,0.11678,0.1986]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49734,-0.12095,0.02078],"force_p95":0.2014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.212,"mean_force":0.106,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49703,-0.10911,0.02077]}],"total_contact_groups":6},"final_pose_error":0.02288,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50185,-0.15442,0.02499],"final_tcp_position":[0.49381,-0.10833,0.09816],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":108.10826,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":2.92024,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":108.10826,"subtask_id":"pre_push_approach","tcp_end":[0.49764,0.10794,0.03043],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.5032,-0.14532,0.0252],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.00567,"object_to_goal_dist_start":0.20406,"object_z_max":0.02764,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":760.0,"raw_peak_contact_force":2.334,"subtask_id":"push_to_goal","tcp_end":[0.4971,-0.10882,0.0208],"tcp_start":[0.49764,0.10794,0.03043],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":600.0,"object_pos_end":[0.50185,-0.15442,0.02499],"object_pos_start":[0.5032,-0.14532,0.0252],"object_to_goal_dist_end":0.00479,"object_to_goal_dist_start":0.00567,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3936.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49381,-0.10833,0.09816],"tcp_start":[0.4971,-0.10882,0.0208],"tcp_to_object_dist_end":0.08685,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36453,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.09085,"approach_behind_object.approach_tolerance":0.02794,"approach_behind_object.arc_height":0.12627,"push_object_to_goal.push_speed":0.01168,"push_object_to_goal.push_tolerance":0.03784,"retract_from_object.retract_speed":0.10535,"retract_from_object.retract_tolerance":0.01305},"optimized_scores":{"best_composite_score":0.46107,"best_fitness_score":0.84107,"best_task_score":0.97318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.48323,-0.06167,0.03386],"force_p95":59.28494,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.20471,"mean_force":7.04776,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.47716,-0.05028,0.02395]},{"body_a":"world","body_b":"push_box","contact_count":385.0,"contact_point_centroid":[0.47759,-0.05356,-6e-05],"force_p95":20.57962,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.17679,"mean_force":3.01766,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.46819,-0.00472,0.02674]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.51875,-0.14178,0.05209],"force_p95":44.33415,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.33575,"mean_force":11.15851,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.48935,-0.11521,0.02212]},{"body_a":"world","body_b":"push_box","contact_count":1753.0,"contact_point_centroid":[0.49721,-0.15257,-2e-05],"force_p95":0.3298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.12012,"mean_force":0.3461,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.48644,-0.11331,0.0679]},{"body_a":"push_box","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.5128,-0.08795,0.05129],"force_p95":7.07148,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.29393,"mean_force":2.54262,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.48108,-0.06982,0.02302]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.5069,-0.12579,0.05099],"force_p95":5.58686,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.3594,"mean_force":1.45433,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.48851,-0.11493,0.02505]},{"body_a":"world","body_b":"push_box","contact_count":2264.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.48183,0.08712,0.17739]}],"total_contact_groups":7},"final_pose_error":0.01299,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49723,-0.15207,0.02499],"final_tcp_position":[0.48657,-0.11318,0.10866],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":82.20471,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":28.31123,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":549.0,"raw_peak_contact_force":82.20471,"subtask_id":"pre_push_approach","tcp_end":[0.46062,0.04161,0.03119],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.49597,-0.15024,0.02548],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00407,"object_to_goal_dist_start":0.12903,"object_z_max":0.02705,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1805.0,"raw_peak_contact_force":47.33575,"subtask_id":"push_to_goal","tcp_end":[0.49005,-0.11375,0.02115],"tcp_start":[0.46062,0.04161,0.03119],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":600.0,"object_pos_end":[0.49723,-0.15207,0.02499],"object_pos_start":[0.49597,-0.15024,0.02548],"object_to_goal_dist_end":0.00346,"object_to_goal_dist_start":0.00407,"object_z_max":0.02665,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.48657,-0.11318,0.10866],"tcp_start":[0.49005,-0.11375,0.02115],"tcp_to_object_dist_end":0.09288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```