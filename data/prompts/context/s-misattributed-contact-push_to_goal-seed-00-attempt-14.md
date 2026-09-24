## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | time_limit | time_limit | 7 | -0.1971 | 0.15 | ❌ rejected |
| 13 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4765 | 0.98 | ❌ rejected |
| 12 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4629 | 0.96 | ❌ rejected |
| 11 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4763 | 0.98 | ✅ accepted |
| 10 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4662 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.979, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.197) — your mutation base

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

- **Composite score**: -0.197
- **task_score** (E): 0.149
- **fitness_score**: 0.183  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_object | 1.00 | 1.00 | 0.2515 |
| push_object_to_goal | 1.00 | 1.00 | 0.0870 |
| retract_from_object | 1.00 | 1.00 | 0.0868 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_object | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.492, 0.071, 0.064) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 2.667 | 25.041 | 47.914 |
| push_object_to_goal | push | 1.00 / time_limit | (0.492, 0.071, 0.064)→(0.493, -0.014, 0.046) | (0.496, 0.001, 0.025)→(0.500, -0.026, 0.030) | 0.152→0.125 | 1.00 / 4.000 | 0.245 | 22.107 |
| retract_from_object | retract | 1.00 / time_limit | (0.493, -0.014, 0.046)→(0.490, -0.014, 0.133) | (0.500, -0.026, 0.030)→(0.499, -0.019, 0.025) | 0.125→0.133 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.233
- lateral_force_integral: None
- approach_alignment: 0.550
- goal_progress: 0.230
- terminal_score: 0.230
- phase_score: 0.260
- phase_breakdown.pre_push_approach_score: 0.247
- phase_breakdown.push_to_goal_score: 0.266

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.248
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.230
- **Median Q (composite search score)**: -0.169
- **K-run variance**: 0.0046
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.505


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55046,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_max_time":1.48723,"approach_behind_object.approach_speed":0.14711,"approach_behind_object.arc_height":0.05159,"push_object_to_goal.push_max_time":2.04109,"push_object_to_goal.push_speed":0.02015,"retract_from_object.retract_max_time":1.2064,"retract_from_object.retract_speed":0.05457},"optimized_scores":{"best_composite_score":-0.16869,"best_fitness_score":0.21131,"best_task_score":0.18955},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":541.0,"contact_point_centroid":[0.50946,-0.01672,0.04671],"force_p95":8.69345,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.73016,"mean_force":5.12769,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50761,-0.00485,0.0453]},{"body_a":"world","body_b":"push_box","contact_count":2670.0,"contact_point_centroid":[0.51813,-0.04026,-2e-05],"force_p95":4.93483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.23716,"mean_force":1.33685,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50916,0.0118,0.04845]},{"body_a":"world","body_b":"push_box","contact_count":3579.0,"contact_point_centroid":[0.51867,-0.05423,-1e-05],"force_p95":0.41612,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.72194,"mean_force":0.27604,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.50272,-0.01949,0.08567]},{"body_a":"attachment","body_b":"push_box","contact_count":142.0,"contact_point_centroid":[0.50912,-0.03111,0.05266],"force_p95":1.53121,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.03048,"mean_force":0.60734,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.5033,-0.01949,0.04635]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.506,0.04109,0.18356]}],"total_contact_groups":5},"final_pose_error":0.0168,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51816,-0.05159,0.02499],"final_tcp_position":[0.50293,-0.01949,0.12633],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":10.73016,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":1.64769,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3211.0,"raw_peak_contact_force":10.73016,"subtask_id":"pre_push_approach","tcp_end":[0.51484,0.03501,0.05717],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07044,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51956,-0.05334,0.02681],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.09863,"object_to_goal_dist_start":0.12347,"object_z_max":0.0268,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3721.0,"raw_peak_contact_force":2.72194,"subtask_id":"push_to_goal","tcp_end":[0.50642,-0.01953,0.04276],"tcp_start":[0.51484,0.03501,0.05717],"tcp_to_object_dist_end":0.03962,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51816,-0.05159,0.02499],"object_pos_start":[0.51956,-0.05334,0.02681],"object_to_goal_dist_end":0.10007,"object_to_goal_dist_start":0.09863,"object_z_max":0.02698,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50293,-0.01949,0.12633],"tcp_start":[0.50642,-0.01953,0.04276],"tcp_to_object_dist_end":0.10739,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26374,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_max_time":3.9962,"approach_behind_object.approach_speed":0.14997,"approach_behind_object.arc_height":0.09922,"push_object_to_goal.push_max_time":3.67236,"push_object_to_goal.push_speed":0.07988,"retract_from_object.retract_max_time":1.59516,"retract_from_object.retract_speed":0.1427},"optimized_scores":{"best_composite_score":-0.29046,"best_fitness_score":0.08954,"best_task_score":0.0282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":410.0,"contact_point_centroid":[0.50758,0.03604,0.05058],"force_p95":89.33061,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.48323,"mean_force":65.72427,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49796,0.03126,0.05419]},{"body_a":"world","body_b":"push_box","contact_count":3184.0,"contact_point_centroid":[0.50169,0.04661,-0.0001],"force_p95":53.0677,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.09077,"mean_force":8.76739,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49534,0.07798,0.05964]},{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.50563,0.01049,0.04935],"force_p95":39.63735,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.39568,"mean_force":17.19097,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49912,0.00107,0.05188]},{"body_a":"world","body_b":"push_box","contact_count":2008.0,"contact_point_centroid":[0.5056,0.04687,-6e-05],"force_p95":0.49127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.63055,"mean_force":0.54902,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.4964,0.00158,0.09562]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.49797,0.10156,0.21089]}],"total_contact_groups":5},"final_pose_error":0.01231,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50584,0.04822,0.02499],"final_tcp_position":[0.49658,0.00164,0.13943],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":93.48323,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":62.88333,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3594.0,"raw_peak_contact_force":93.48323,"subtask_id":"pre_push_approach","tcp_end":[0.49776,0.13264,0.07249],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0919,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50427,0.03282,0.03334],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.18306,"object_to_goal_dist_start":0.20406,"object_z_max":0.03331,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2040.0,"raw_peak_contact_force":52.39568,"subtask_id":"push_to_goal","tcp_end":[0.49982,0.00172,0.05131],"tcp_start":[0.49776,0.13264,0.07249],"tcp_to_object_dist_end":0.0362,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.04822,0.02499],"object_pos_start":[0.50427,0.03282,0.03334],"object_to_goal_dist_end":0.19831,"object_to_goal_dist_start":0.18306,"object_z_max":0.03384,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49658,0.00164,0.13943],"tcp_start":[0.49982,0.00172,0.05131],"tcp_to_object_dist_end":0.12391,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86957,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_max_time":4.94722,"approach_behind_object.approach_speed":0.14506,"approach_behind_object.arc_height":0.05933,"push_object_to_goal.push_max_time":2.58888,"push_object_to_goal.push_speed":0.04212,"retract_from_object.retract_max_time":2.07755,"retract_from_object.retract_speed":0.11807},"optimized_scores":{"best_composite_score":-0.13205,"best_fitness_score":0.24795,"best_task_score":0.2296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":528.0,"contact_point_centroid":[0.47221,-0.01631,0.04865],"force_p95":29.411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.52853,"mean_force":16.27528,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.47037,-0.00482,0.04939]},{"body_a":"world","body_b":"push_box","contact_count":2944.0,"contact_point_centroid":[0.4723,-0.03706,-2e-05],"force_p95":12.38128,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.92485,"mean_force":3.2037,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.46644,0.01526,0.05345]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.47156,-0.03623,0.04864],"force_p95":2.09243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.20454,"mean_force":0.9998,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.47098,-0.0243,0.04875]},{"body_a":"world","body_b":"push_box","contact_count":1970.0,"contact_point_centroid":[0.47362,-0.05766,-3e-05],"force_p95":0.4559,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.35932,"mean_force":0.30438,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.47004,-0.02426,0.09036]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.48247,0.04773,0.18774]}],"total_contact_groups":5},"final_pose_error":0.01195,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47373,-0.05413,0.02499],"final_tcp_position":[0.47026,-0.02426,0.13377],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":39.52853,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":10.59071,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3472.0,"raw_peak_contact_force":39.52853,"subtask_id":"pre_push_approach","tcp_end":[0.46454,0.04425,0.06307],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07861,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47555,-0.0586,0.02915],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.0947,"object_to_goal_dist_start":0.12903,"object_z_max":0.02913,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2051.0,"raw_peak_contact_force":11.20454,"subtask_id":"push_to_goal","tcp_end":[0.47348,-0.02432,0.04528],"tcp_start":[0.46454,0.04425,0.06307],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.47373,-0.05413,0.02499],"object_pos_start":[0.47555,-0.0586,0.02915],"object_to_goal_dist_end":0.09941,"object_to_goal_dist_start":0.0947,"object_z_max":0.02927,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47026,-0.02426,0.13377],"tcp_start":[0.47348,-0.02432,0.04528],"tcp_to_object_dist_end":0.11286,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```