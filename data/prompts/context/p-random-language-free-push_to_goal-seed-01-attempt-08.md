## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3158 | 0.66 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2338 | 0.00 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4923 | 0.61 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3225 | 0.63 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1238 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

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
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.316) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.1
  - 0.025
  weight: 0.3
- id: goal_reach
  target_entity: object
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.1
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.1
    - 0.025
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: impedance_motion
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
      distance: 0.95
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.8
      - 1.2
      default: 1.0
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: goal_reach
- id: retract_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.1, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.1, 0.025], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.95, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.316
- **task_score** (E): 0.658
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1568 |
| descend_1 | 0.00 | 1.00 | 0.1273 |
| push_1 | 0.00 | 1.00 | 0.2655 |
| retract_1 | 1.00 | 1.00 | 0.1379 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, 0.091, 0.181) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 0.00 / step_budget | (0.474, 0.091, 0.181)→(0.471, 0.098, 0.054) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 0.00 / step_budget | (0.471, 0.098, 0.054)→(0.516, -0.160, 0.049) | (0.474, -0.001, 0.025)→(0.511, -0.105, 0.026) | 0.154→0.047 | 1.00 / 3.667 | 0.163 | 85.537 |
| retract_1 | retract | 1.00 / step_budget | (0.516, -0.160, 0.049)→(0.513, -0.159, 0.187) | (0.511, -0.105, 0.026)→(0.510, -0.104, 0.025) | 0.047→0.048 | 1.00 / 4.000 | 0.245 | 14.629 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.867
- lateral_force_integral: None
- approach_alignment: 0.908
- goal_progress: 0.859
- terminal_score: 0.859
- phase_score: 0.676
- phase_breakdown.goal_reach_score: 0.577
- phase_breakdown.pre_contact_score: 0.905

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.859
- **Median Q (composite search score)**: 0.278
- **K-run variance**: 0.0079
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33333,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.32236,"descend_1.contact_force_threshold":6.08575,"descend_1.descend_speed":0.07496,"push_1.push_distance":1.12509,"push_1.push_speed":0.08722},"optimized_scores":{"best_composite_score":0.43882,"best_fitness_score":0.74882,"best_task_score":0.8585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1914.0,"contact_point_centroid":[0.50672,-0.00856,-0.00021],"force_p95":86.98369,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.03084,"mean_force":22.28659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49517,0.03313,0.05]},{"body_a":"attachment","body_b":"push_box","contact_count":705.0,"contact_point_centroid":[0.50348,-0.04446,0.05002],"force_p95":99.30837,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.00347,"mean_force":59.19081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49596,-0.04281,0.05123]},{"body_a":"world","body_b":"push_box","contact_count":3272.0,"contact_point_centroid":[0.50911,-0.12293,-3e-05],"force_p95":0.24537,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.39715,"mean_force":0.2958,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49077,-0.15832,0.12045]},{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.50326,-0.15364,0.04915],"force_p95":36.82047,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.69238,"mean_force":8.19565,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49333,-0.15988,0.05101]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49853,0.07021,0.23864]},{"body_a":"world","body_b":"push_box","contact_count":2656.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49681,0.14736,0.11348]}],"total_contact_groups":6},"final_pose_error":0.01211,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50925,-0.12265,0.02499],"final_tcp_position":[0.49119,-0.15838,0.18842],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":114.03084,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49861,0.14307,0.1783],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2656.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.49746,0.15228,0.05241],"tcp_start":[0.49861,0.14307,0.1783],"tcp_to_object_dist_end":0.10206,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51231,-0.12612,0.02859],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.02711,"object_to_goal_dist_start":0.20406,"object_z_max":0.03456,"peak_contact_force":4e-05,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2619.0,"raw_peak_contact_force":114.03084,"subtask_id":"goal_reach","tcp_end":[0.49394,-0.15915,0.05019],"tcp_start":[0.49746,0.15228,0.05241],"tcp_to_object_dist_end":0.04353,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50925,-0.12265,0.02499],"object_pos_start":[0.51231,-0.12612,0.02859],"object_to_goal_dist_end":0.02887,"object_to_goal_dist_start":0.02711,"object_z_max":0.02926,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3288.0,"raw_peak_contact_force":43.39715,"tcp_end":[0.49119,-0.15838,0.18842],"tcp_start":[0.49394,-0.15915,0.05019],"tcp_to_object_dist_end":0.16827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37383,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.43161,"descend_1.contact_force_threshold":3.76793,"descend_1.descend_speed":0.19017,"push_1.push_distance":0.94859,"push_1.push_speed":0.1496},"optimized_scores":{"best_composite_score":0.27779,"best_fitness_score":0.58779,"best_task_score":0.64971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2381.0,"contact_point_centroid":[0.48847,-0.05691,-0.00013],"force_p95":45.31056,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.33754,"mean_force":8.6246,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48926,-0.02983,0.0516]},{"body_a":"attachment","body_b":"push_box","contact_count":626.0,"contact_point_centroid":[0.50977,-0.06637,0.05025],"force_p95":53.55268,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.61093,"mean_force":31.25264,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49909,-0.06819,0.05232]},{"body_a":"world","body_b":"push_box","contact_count":1656.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48527,0.03349,0.24081]},{"body_a":"world","body_b":"push_box","contact_count":2204.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46848,0.07152,0.11857]},{"body_a":"world","body_b":"push_box","contact_count":3396.0,"contact_point_centroid":[0.51611,-0.10777,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24522,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51917,-0.18017,0.11653]}],"total_contact_groups":5},"final_pose_error":0.01277,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51611,-0.10777,0.02499],"final_tcp_position":[0.51962,-0.18023,0.18699],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":101.33754,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47129,0.06872,0.18175],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.4678,0.07475,0.05506],"tcp_start":[0.47129,0.06872,0.18175],"tcp_to_object_dist_end":0.10346,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51611,-0.10776,0.02493],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.04521,"object_to_goal_dist_start":0.12903,"object_z_max":0.03105,"peak_contact_force":0.24405,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3007.0,"raw_peak_contact_force":101.33754,"subtask_id":"goal_reach","tcp_end":[0.52245,-0.18109,0.04941],"tcp_start":[0.4678,0.07475,0.05506],"tcp_to_object_dist_end":0.07757,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":849.0,"n_steps_budget":930.0,"object_pos_end":[0.51611,-0.10777,0.02499],"object_pos_start":[0.51611,-0.10776,0.02493],"object_to_goal_dist_end":0.0452,"object_to_goal_dist_start":0.04521,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3396.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51962,-0.18023,0.18699],"tcp_start":[0.52245,-0.18109,0.04941],"tcp_to_object_dist_end":0.1775,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05983,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.38004,"descend_1.contact_force_threshold":7.42053,"descend_1.descend_speed":0.09238,"push_1.push_distance":0.80773,"push_1.push_speed":0.0648},"optimized_scores":{"best_composite_score":0.2308,"best_fitness_score":0.5408,"best_task_score":0.46545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2558.0,"contact_point_centroid":[0.46668,-0.05171,-5e-05],"force_p95":27.91137,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.24342,"mean_force":3.95869,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4825,-0.02401,0.04962]},{"body_a":"attachment","body_b":"push_box","contact_count":471.0,"contact_point_centroid":[0.48696,-0.05044,0.05158],"force_p95":33.71808,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.54826,"mean_force":19.51584,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49298,-0.04636,0.05014]},{"body_a":"world","body_b":"push_box","contact_count":1640.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47597,0.03018,0.24105]},{"body_a":"world","body_b":"push_box","contact_count":3392.0,"contact_point_centroid":[0.50559,-0.08157,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52688,-0.13892,0.11509]},{"body_a":"world","body_b":"push_box","contact_count":2756.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44838,0.06464,0.1164]}],"total_contact_groups":5},"final_pose_error":0.01269,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50559,-0.08157,0.02499],"final_tcp_position":[0.52733,-0.13896,0.18547],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":41.24342,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.45216,0.062,0.18211],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":689.0,"n_steps_budget":900.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2756.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.44686,0.06754,0.05344],"tcp_start":[0.45216,0.062,0.18211],"tcp_to_object_dist_end":0.10318,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50559,-0.08158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.06865,"object_to_goal_dist_start":0.12843,"object_z_max":0.03537,"peak_contact_force":0.24526,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3029.0,"raw_peak_contact_force":41.24342,"subtask_id":"goal_reach","tcp_end":[0.53022,-0.13962,0.04781],"tcp_start":[0.44686,0.06754,0.05344],"tcp_to_object_dist_end":0.06705,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":930.0,"object_pos_end":[0.50559,-0.08157,0.02499],"object_pos_start":[0.50559,-0.08158,0.02499],"object_to_goal_dist_end":0.06865,"object_to_goal_dist_start":0.06865,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3392.0,"raw_peak_contact_force":0.24526,"tcp_end":[0.52733,-0.13896,0.18547],"tcp_start":[0.53022,-0.13962,0.04781],"tcp_to_object_dist_end":0.17182,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```