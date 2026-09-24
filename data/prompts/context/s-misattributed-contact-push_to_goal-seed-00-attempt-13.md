## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4765 | 0.98 | ❌ rejected |
| 12 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4629 | 0.96 | ❌ rejected |
| 11 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4763 | 0.98 | ✅ accepted |
| 10 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4662 | 0.96 | ❌ rejected |
| 9 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4678 | 0.98 | ✅ accepted |

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

## Current Skill (Q=0.476) — your mutation base

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

- **Composite score**: 0.476
- **task_score** (E): 0.976
- **fitness_score**: 0.856  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_object | 1.00 | 1.00 | 0.2786 |
| push_object_to_goal | 1.00 | 1.00 | 0.1746 |
| retract_from_object | 1.00 | 1.00 | 0.0708 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, 0.060, 0.032) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 2.000 | 1.158 | 105.271 |
| push_object_to_goal | push | 1.00 / step_budget | (0.492, 0.060, 0.032)→(0.496, -0.113, 0.021) | (0.496, 0.001, 0.025)→(0.501, -0.150, 0.025) | 0.152→0.002 | 1.00 / 4.000 | 0.245 | 15.846 |
| retract_from_object | retract | 1.00 / step_budget | (0.496, -0.113, 0.021)→(0.493, -0.113, 0.092) | (0.501, -0.150, 0.025)→(0.501, -0.153, 0.025) | 0.002→0.004 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.733
- goal_progress: 0.982
- terminal_score: 0.982
- phase_score: 0.779
- phase_breakdown.pre_push_approach_score: 0.296
- phase_breakdown.push_to_goal_score: 0.986

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.860
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.982
- **Median Q (composite search score)**: 0.477
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82482,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.11582,"approach_behind_object.approach_tolerance":0.01636,"approach_behind_object.arc_height":0.12389,"push_object_to_goal.push_speed":0.05745,"push_object_to_goal.push_tolerance":0.03772,"retract_from_object.retract_speed":0.09039,"retract_from_object.retract_tolerance":0.03668},"optimized_scores":{"best_composite_score":0.47716,"best_fitness_score":0.85716,"best_task_score":0.97347},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":127.0,"contact_point_centroid":[0.51435,-0.06557,0.03761],"force_p95":21.91299,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.67892,"mean_force":5.03734,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50661,-0.05421,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":252.0,"contact_point_centroid":[0.51382,-0.05901,-5e-05],"force_p95":16.81295,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.6493,"mean_force":3.0258,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.51154,-0.01213,0.0219]},{"body_a":"push_box","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53752,-0.0596,0.05166],"force_p95":8.23444,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.67705,"mean_force":2.58547,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50766,-0.04425,0.02046]},{"body_a":"world","body_b":"push_box","contact_count":353.0,"contact_point_centroid":[0.49924,-0.1568,-0.00013],"force_p95":0.82167,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.30426,"mean_force":0.33519,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.4978,-0.11357,0.05298]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52804,-0.13222,0.05168],"force_p95":1.81057,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.83861,"mean_force":1.18768,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49907,-0.11505,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":3440.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.50723,0.08359,0.17061]}],"total_contact_groups":6},"final_pose_error":0.03663,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49945,-0.15323,0.02498],"final_tcp_position":[0.49778,-0.11284,0.08329],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":82.67892,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":2.52389,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":403.0,"raw_peak_contact_force":82.67892,"subtask_id":"pre_push_approach","tcp_end":[0.51718,0.02761,0.02461],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.50158,-0.15037,0.02473],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.00164,"object_to_goal_dist_start":0.12347,"object_z_max":0.02703,"peak_contact_force":0.24534,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":357.0,"raw_peak_contact_force":2.30426,"subtask_id":"push_to_goal","tcp_end":[0.50054,-0.11296,0.01982],"tcp_start":[0.51718,0.02761,0.02461],"tcp_to_object_dist_end":0.03774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":105.0,"n_steps_budget":720.0,"object_pos_end":[0.49945,-0.15323,0.02498],"object_pos_start":[0.50158,-0.15037,0.02473],"object_to_goal_dist_end":0.00328,"object_to_goal_dist_start":0.00164,"object_z_max":0.02629,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3440.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49778,-0.11284,0.08329],"tcp_start":[0.50054,-0.11296,0.01982],"tcp_to_object_dist_end":0.07096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54737,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.09702,"approach_behind_object.approach_tolerance":0.01905,"approach_behind_object.arc_height":0.1424,"push_object_to_goal.push_speed":0.04934,"push_object_to_goal.push_tolerance":0.03863,"retract_from_object.retract_speed":0.10558,"retract_from_object.retract_tolerance":0.03243},"optimized_scores":{"best_composite_score":0.48033,"best_fitness_score":0.86033,"best_task_score":0.98203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":195.0,"contact_point_centroid":[0.50515,-0.02269,0.04025],"force_p95":82.05257,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.10075,"mean_force":10.47449,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49638,-0.01155,0.02355]},{"body_a":"push_box","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.53015,-0.03234,0.05257],"force_p95":36.09365,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.99869,"mean_force":6.52957,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49647,-0.01492,0.02345]},{"body_a":"world","body_b":"push_box","contact_count":355.0,"contact_point_centroid":[0.50457,-0.00481,-0.00013],"force_p95":46.08171,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.30279,"mean_force":7.01055,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49639,0.0421,0.02571]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52823,-0.12965,0.05012],"force_p95":14.01744,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.65461,"mean_force":8.28293,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49539,-0.11375,0.02101]},{"body_a":"world","body_b":"push_box","contact_count":448.0,"contact_point_centroid":[0.50213,-0.15474,-0.00016],"force_p95":0.54894,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.67897,"mean_force":0.33337,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49383,-0.11225,0.05531]},{"body_a":"world","body_b":"push_box","contact_count":3504.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.49828,0.12703,0.20219]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49627,-0.12371,0.02119],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.4969,-0.11178,0.02072]}],"total_contact_groups":7},"final_pose_error":0.03222,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50238,-0.15279,0.02499],"final_tcp_position":[0.49399,-0.11152,0.08863],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":119.10075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.0,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":616.0,"raw_peak_contact_force":119.10075,"subtask_id":"pre_push_approach","tcp_end":[0.49775,0.11156,0.03029],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.5024,-0.14891,0.0259],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.00278,"object_to_goal_dist_start":0.20406,"object_z_max":0.02918,"peak_contact_force":0.24522,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":451.0,"raw_peak_contact_force":14.65461,"subtask_id":"push_to_goal","tcp_end":[0.4969,-0.11178,0.02072],"tcp_start":[0.49775,0.11156,0.03029],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":600.0,"object_pos_end":[0.50238,-0.15279,0.02499],"object_pos_start":[0.5024,-0.14891,0.0259],"object_to_goal_dist_end":0.00367,"object_to_goal_dist_start":0.00278,"object_z_max":0.0259,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3504.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49399,-0.11152,0.08863],"tcp_start":[0.4969,-0.11178,0.02072],"tcp_to_object_dist_end":0.07632,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4837,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_speed":0.07743,"approach_behind_object.approach_tolerance":0.03127,"approach_behind_object.arc_height":0.09401,"push_object_to_goal.push_speed":0.04544,"push_object_to_goal.push_tolerance":0.03731,"retract_from_object.retract_speed":0.0909,"retract_from_object.retract_tolerance":0.01958},"optimized_scores":{"best_composite_score":0.47186,"best_fitness_score":0.85186,"best_task_score":0.97119},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.48672,-0.0662,0.04049],"force_p95":107.01641,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.03468,"mean_force":18.05642,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.47919,-0.05491,0.02881]},{"body_a":"world","body_b":"push_box","contact_count":377.0,"contact_point_centroid":[0.47834,-0.05763,-9e-05],"force_p95":42.80236,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.44148,"mean_force":5.67154,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.47001,-0.00821,0.03375]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.52337,-0.13949,0.05085],"force_p95":27.10497,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.57777,"mean_force":12.15981,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.4904,-0.11529,0.02324]},{"body_a":"world","body_b":"push_box","contact_count":990.0,"contact_point_centroid":[0.50047,-0.15367,-5e-05],"force_p95":0.29086,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.01834,"mean_force":0.3393,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.48748,-0.11412,0.0647]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50735,-0.12671,0.0503],"force_p95":0.56168,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.7346,"mean_force":0.14634,"phase_index":2.0,"phase_name":"retract_from_object","phase_type":"retract","tcp_position_centroid":[0.49032,-0.11538,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":1760.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.48239,0.06709,0.17985]}],"total_contact_groups":6},"final_pose_error":0.01957,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5012,-0.15352,0.02499],"final_tcp_position":[0.48733,-0.1137,0.10387],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":114.03468,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.94905,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":487.0,"raw_peak_contact_force":114.03468,"subtask_id":"pre_push_approach","tcp_end":[0.46231,0.04086,0.04116],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.49936,-0.15089,0.02582],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00137,"object_to_goal_dist_start":0.12903,"object_z_max":0.02822,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":30.57777,"subtask_id":"push_to_goal","tcp_end":[0.49077,-0.11427,0.02312],"tcp_start":[0.46231,0.04086,0.04116],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":720.0,"object_pos_end":[0.5012,-0.15352,0.02499],"object_pos_start":[0.49936,-0.15089,0.02582],"object_to_goal_dist_end":0.00372,"object_to_goal_dist_start":0.00137,"object_z_max":0.02582,"peak_contact_force":0.24525,"phase_name":"retract_from_object","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.48733,-0.1137,0.10387],"tcp_start":[0.49077,-0.11427,0.02312],"tcp_to_object_dist_end":0.08944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```