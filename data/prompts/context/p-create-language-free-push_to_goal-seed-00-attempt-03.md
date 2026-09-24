## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1488 | 0.38 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.2139 | 0.38 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | -0.2350 | 0.00 | ❌ rejected |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.2121 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.149) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
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
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: retract_1
  type: retract
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.149
- **task_score** (E): 0.383
- **fitness_score**: 0.359  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0968 |
| descend_1 | 1.00 | 1.00 | 0.1949 |
| push_1 | 0.33 | 1.00 | 0.1443 |
| retract_1 | 1.00 | 1.00 | 0.0946 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.023, 0.237) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.023, 0.237)→(0.511, 0.027, 0.044) | (0.496, 0.001, 0.025)→(0.501, 0.001, 0.024) | 0.152→0.153 | 1.00 / 4.000 | 214.938 | 226.960 |
| push_1 | push | 0.33 / step_budget | (0.511, 0.027, 0.044)→(0.506, -0.115, 0.040) | (0.501, 0.001, 0.024)→(0.504, -0.058, 0.027) | 0.153→0.092 | 1.00 / 3.000 | 0.386 | 144.311 |
| retract_1 | retract | 1.00 / step_budget | (0.506, -0.115, 0.040)→(0.501, -0.061, 0.117) | (0.504, -0.058, 0.027)→(0.503, -0.055, 0.025) | 0.092→0.095 | 1.00 / 4.000 | 0.245 | 2.051 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.611
- lateral_force_integral: None
- approach_alignment: 0.741
- goal_progress: 0.610
- terminal_score: 0.610
- phase_score: 0.483
- phase_breakdown.pre_contact_score: 0.183
- phase_breakdown.push_to_goal_score: 0.611

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.534
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.610
- **Median Q (composite search score)**: 0.115
- **K-run variance**: 0.0172
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98039,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07195,"descend_1.descend_speed":0.01682,"push_1.push_speed":0.07205},"optimized_scores":{"best_composite_score":0.32357,"best_fitness_score":0.53357,"best_task_score":0.6098},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":499.0,"contact_point_centroid":[0.53745,-0.00778,0.04579],"force_p95":198.89378,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":205.90525,"mean_force":186.46391,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52783,-0.00181,0.0455]},{"body_a":"world","body_b":"push_box","contact_count":2234.0,"contact_point_centroid":[0.52431,-0.02385,-0.00044],"force_p95":167.29174,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.09933,"mean_force":42.04829,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52124,-0.00208,0.05782]},{"body_a":"attachment","body_b":"push_box","contact_count":893.0,"contact_point_centroid":[0.54145,-0.04882,0.04782],"force_p95":107.29462,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.90864,"mean_force":91.83299,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53453,-0.05578,0.04716]},{"body_a":"world","body_b":"push_box","contact_count":2261.0,"contact_point_centroid":[0.52497,-0.05839,-0.00038],"force_p95":93.47109,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.02477,"mean_force":36.79791,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53281,-0.06244,0.04659]},{"body_a":"world","body_b":"push_box","contact_count":1752.0,"contact_point_centroid":[0.5046,-0.09871,-5e-05],"force_p95":0.47989,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.38283,"mean_force":0.29476,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50463,-0.12119,0.07952]},{"body_a":"attachment","body_b":"push_box","contact_count":80.0,"contact_point_centroid":[0.51076,-0.12489,0.05],"force_p95":1.30249,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.2173,"mean_force":0.66007,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50755,-0.13646,0.0492]},{"body_a":"world","body_b":"push_box","contact_count":2472.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50502,-0.00123,0.20291]}],"total_contact_groups":7},"final_pose_error":0.01139,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50392,-0.10198,0.02499],"final_tcp_position":[0.50175,-0.10447,0.11349],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":205.90525,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2472.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.51197,-0.0025,0.1058],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.52202,-0.02852,0.02453],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12346,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":189.00038,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2733.0,"raw_peak_contact_force":205.90525,"subtask_id":"pre_contact","tcp_end":[0.54109,-0.00205,0.04384],"tcp_start":[0.51197,-0.0025,0.1058],"tcp_to_object_dist_end":0.03791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50453,-0.1022,0.0243],"object_pos_start":[0.52202,-0.02852,0.02453],"object_to_goal_dist_end":0.04802,"object_to_goal_dist_start":0.12346,"object_z_max":0.03531,"peak_contact_force":0.49583,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3154.0,"raw_peak_contact_force":124.90864,"subtask_id":"push_to_goal","tcp_end":[0.51161,-0.1435,0.03941],"tcp_start":[0.54109,-0.00205,0.04384],"tcp_to_object_dist_end":0.04454,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":600.0,"object_pos_end":[0.50392,-0.10198,0.02499],"object_pos_start":[0.50453,-0.1022,0.0243],"object_to_goal_dist_end":0.04818,"object_to_goal_dist_start":0.04802,"object_z_max":0.02875,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1832.0,"raw_peak_contact_force":3.38283,"tcp_end":[0.50175,-0.10447,0.11349],"tcp_start":[0.51161,-0.1435,0.03941],"tcp_to_object_dist_end":0.08857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36275,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27579,"descend_1.descend_speed":0.02131,"push_1.push_speed":0.0841},"optimized_scores":{"best_composite_score":0.1153,"best_fitness_score":0.3253,"best_task_score":0.3519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":165.0,"contact_point_centroid":[0.51702,0.0759,0.04614],"force_p95":234.82456,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":238.01572,"mean_force":195.41778,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50605,0.07993,0.04639]},{"body_a":"world","body_b":"push_box","contact_count":3836.0,"contact_point_centroid":[0.50267,0.05509,-8e-05],"force_p95":28.69989,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":205.66774,"mean_force":8.69594,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49864,0.07476,0.15694]},{"body_a":"attachment","body_b":"push_box","contact_count":783.0,"contact_point_centroid":[0.52616,0.03183,0.04754],"force_p95":124.94393,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.41142,"mean_force":103.21723,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51612,0.02845,0.04773]},{"body_a":"world","body_b":"push_box","contact_count":2274.0,"contact_point_centroid":[0.5105,0.01701,-0.00038],"force_p95":108.44333,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.54435,"mean_force":36.07566,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51346,0.00576,0.04554]},{"body_a":"world","body_b":"push_box","contact_count":1448.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49883,0.03585,0.29645]},{"body_a":"world","body_b":"push_box","contact_count":2412.0,"contact_point_centroid":[0.49799,-0.01776,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49859,-0.04998,0.0763]}],"total_contact_groups":6},"final_pose_error":0.01085,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49799,-0.01776,0.02499],"final_tcp_position":[0.49512,-0.02141,0.11518],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":238.01572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49928,0.07076,0.29577],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50556,0.05542,0.02435],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20549,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":230.93611,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4001.0,"raw_peak_contact_force":238.01572,"subtask_id":"pre_contact","tcp_end":[0.51384,0.08166,0.04388],"tcp_start":[0.49928,0.07076,0.29577],"tcp_to_object_dist_end":0.03375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49799,-0.01776,0.02499],"object_pos_start":[0.50556,0.05542,0.02435],"object_to_goal_dist_end":0.13225,"object_to_goal_dist_start":0.20549,"object_z_max":0.03535,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3057.0,"raw_peak_contact_force":148.41142,"subtask_id":"push_to_goal","tcp_end":[0.50556,-0.08022,0.03952],"tcp_start":[0.51384,0.08166,0.04388],"tcp_to_object_dist_end":0.06457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49799,-0.01776,0.02499],"object_pos_start":[0.49799,-0.01776,0.02499],"object_to_goal_dist_end":0.13225,"object_to_goal_dist_start":0.13225,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49512,-0.02141,0.11518],"tcp_start":[0.50556,-0.08022,0.03952],"tcp_to_object_dist_end":0.09031,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06699,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29164,"descend_1.descend_speed":0.04555,"push_1.push_speed":0.05859},"optimized_scores":{"best_composite_score":0.0076,"best_fitness_score":0.2176,"best_task_score":0.18614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":104.0,"contact_point_centroid":[0.4853,-0.00146,0.04662],"force_p95":225.31305,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":236.95817,"mean_force":185.86608,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47395,0.0015,0.04721]},{"body_a":"world","body_b":"push_box","contact_count":3898.0,"contact_point_centroid":[0.47211,-0.02356,-5e-05],"force_p95":22.50363,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.64948,"mean_force":5.23207,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47201,0.00073,0.16891]},{"body_a":"attachment","body_b":"push_box","contact_count":927.0,"contact_point_centroid":[0.49994,-0.03955,0.04768],"force_p95":131.08578,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.61353,"mean_force":95.72878,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49356,-0.04663,0.04775]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.49858,-0.04412,-0.0005],"force_p95":88.17092,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.3904,"mean_force":49.1893,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49336,-0.04788,0.04736]},{"body_a":"world","body_b":"push_box","contact_count":2454.0,"contact_point_centroid":[0.50787,-0.04523,-5e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.52624,"mean_force":0.25857,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50203,-0.08827,0.08123]},{"body_a":"world","body_b":"push_box","contact_count":548.0,"contact_point_centroid":[0.47139,-0.02418,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48798,0.00028,0.30342]}],"total_contact_groups":6},"final_pose_error":0.01144,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50788,-0.04528,0.02499],"final_tcp_position":[0.50591,-0.05814,0.12126],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":236.95817,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":137.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":548.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.4768,0.00059,0.30828],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.28442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4743,-0.02343,0.0243],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12916,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":224.87856,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4002.0,"raw_peak_contact_force":236.95817,"subtask_id":"pre_contact","tcp_end":[0.47931,0.0019,0.04475],"tcp_start":[0.4768,0.00059,0.30828],"tcp_to_object_dist_end":0.03294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50975,-0.05454,0.03142],"object_pos_start":[0.4743,-0.02343,0.0243],"object_to_goal_dist_end":0.09617,"object_to_goal_dist_start":0.12916,"object_z_max":0.03464,"peak_contact_force":0.4162,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2755.0,"raw_peak_contact_force":159.61353,"subtask_id":"push_to_goal","tcp_end":[0.5013,-0.12242,0.04099],"tcp_start":[0.47931,0.0019,0.04475],"tcp_to_object_dist_end":0.06907,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":720.0,"object_pos_end":[0.50788,-0.04528,0.02499],"object_pos_start":[0.50975,-0.05454,0.03142],"object_to_goal_dist_end":0.10501,"object_to_goal_dist_start":0.09617,"object_z_max":0.03142,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2454.0,"raw_peak_contact_force":2.52624,"tcp_end":[0.50591,-0.05814,0.12126],"tcp_start":[0.5013,-0.12242,0.04099],"tcp_to_object_dist_end":0.09715,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```