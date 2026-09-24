## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=0.212) — your mutation base

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

- **Composite score**: 0.212
- **task_score** (E): 0.383
- **fitness_score**: 0.372  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0967 |
| descend_1 | 1.00 | 1.00 | 0.1724 |
| push_1 | 1.00 | 1.00 | 0.1364 |
| retract_1 | 1.00 | 1.00 | 0.0918 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.023, 0.215) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.023, 0.215)→(0.507, 0.027, 0.044) | (0.496, 0.001, 0.025)→(0.500, 0.002, 0.024) | 0.152→0.153 | 1.00 / 4.000 | 251.333 | 256.182 |
| push_1 | push | 1.00 / step_budget | (0.507, 0.027, 0.044)→(0.503, -0.109, 0.039) | (0.500, 0.002, 0.024)→(0.510, -0.063, 0.028) | 0.153→0.089 | 1.00 / 3.333 | 0.326 | 162.327 |
| retract_1 | retract | 1.00 / step_budget | (0.503, -0.109, 0.039)→(0.506, -0.065, 0.118) | (0.510, -0.063, 0.028)→(0.511, -0.056, 0.025) | 0.089→0.095 | 1.00 / 4.000 | 0.245 | 2.911 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.571
- lateral_force_integral: None
- approach_alignment: 0.731
- goal_progress: 0.564
- terminal_score: 0.564
- phase_score: 0.456
- phase_breakdown.pre_contact_score: 0.195
- phase_breakdown.push_to_goal_score: 0.568

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.499
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.160
- **K-run variance**: 0.0082
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.261


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78906,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19715,"push_1.push_speed":0.07052},"optimized_scores":{"best_composite_score":0.33926,"best_fitness_score":0.49926,"best_task_score":0.56413},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":107.0,"contact_point_centroid":[0.53015,-0.00522,0.04634],"force_p95":249.38606,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":249.88269,"mean_force":204.18627,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.519,-0.0017,0.04671]},{"body_a":"world","body_b":"push_box","contact_count":2551.0,"contact_point_centroid":[0.51761,-0.02665,-8e-05],"force_p95":30.3846,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.36952,"mean_force":8.87296,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51164,-0.00233,0.129]},{"body_a":"attachment","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.54104,-0.04979,0.04728],"force_p95":130.72329,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.09103,"mean_force":105.62729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53081,-0.05326,0.04769]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.52777,-0.05558,-0.00044],"force_p95":108.80811,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.52386,"mean_force":41.53099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52985,-0.05878,0.04662]},{"body_a":"world","body_b":"push_box","contact_count":2064.0,"contact_point_centroid":[0.51444,-0.09693,-2e-05],"force_p95":0.363,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.55993,"mean_force":0.25779,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51524,-0.12039,0.07638]},{"body_a":"attachment","body_b":"push_box","contact_count":30.0,"contact_point_centroid":[0.51883,-0.12208,0.05096],"force_p95":0.60242,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.30323,"mean_force":0.50282,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51756,-0.13394,0.05063]},{"body_a":"world","body_b":"push_box","contact_count":940.0,"contact_point_centroid":[0.51644,-0.02763,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50477,-0.00105,0.26584]}],"total_contact_groups":7},"final_pose_error":0.01152,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51431,-0.09812,0.02499],"final_tcp_position":[0.51176,-0.10042,0.11402],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":249.88269,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.51126,-0.00221,0.23043],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.52037,-0.02664,0.02428],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12504,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":243.62308,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2658.0,"raw_peak_contact_force":249.88269,"subtask_id":"pre_contact","tcp_end":[0.52646,-0.00121,0.04391],"tcp_start":[0.51126,-0.00221,0.23043],"tcp_to_object_dist_end":0.0327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51465,-0.09799,0.0249],"object_pos_start":[0.52037,-0.02664,0.02428],"object_to_goal_dist_end":0.05403,"object_to_goal_dist_start":0.12504,"object_z_max":0.03575,"peak_contact_force":0.2454,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3080.0,"raw_peak_contact_force":156.09103,"subtask_id":"push_to_goal","tcp_end":[0.52246,-0.14335,0.03854],"tcp_start":[0.52646,-0.00121,0.04391],"tcp_to_object_dist_end":0.04801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.51431,-0.09812,0.02499],"object_pos_start":[0.51465,-0.09799,0.0249],"object_to_goal_dist_end":0.05382,"object_to_goal_dist_start":0.05403,"object_z_max":0.02635,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2094.0,"raw_peak_contact_force":3.55993,"tcp_end":[0.51176,-0.10042,0.11402],"tcp_start":[0.52246,-0.14335,0.03854],"tcp_to_object_dist_end":0.0891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89844,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20675,"push_1.push_speed":0.0735},"optimized_scores":{"best_composite_score":0.15986,"best_fitness_score":0.31986,"best_task_score":0.34504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.51522,0.07569,0.04634],"force_p95":252.25438,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":252.6916,"mean_force":205.60994,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50414,0.07929,0.04669]},{"body_a":"world","body_b":"push_box","contact_count":2618.0,"contact_point_centroid":[0.50252,0.05501,-8e-05],"force_p95":30.76572,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.5291,"mean_force":8.54401,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49798,0.07406,0.13137]},{"body_a":"attachment","body_b":"push_box","contact_count":840.0,"contact_point_centroid":[0.52547,0.0323,0.04714],"force_p95":129.2499,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.13106,"mean_force":105.71482,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51534,0.02893,0.04764]},{"body_a":"world","body_b":"push_box","contact_count":2181.0,"contact_point_centroid":[0.51177,0.02816,-0.00044],"force_p95":110.76896,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":124.78529,"mean_force":41.32521,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51453,0.02602,0.04679]},{"body_a":"world","body_b":"push_box","contact_count":2107.0,"contact_point_centroid":[0.49949,-0.01564,-2e-05],"force_p95":0.24645,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.62258,"mean_force":0.25311,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50038,-0.03897,0.0766]},{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.50396,-0.04086,0.05046],"force_p95":1.30007,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.26784,"mean_force":0.60689,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50287,-0.05276,0.05038]},{"body_a":"world","body_b":"push_box","contact_count":1400.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49864,0.03423,0.26646]}],"total_contact_groups":7},"final_pose_error":0.01115,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49943,-0.01635,0.02499],"final_tcp_position":[0.49691,-0.019,0.11452],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":252.6916,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":660.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49878,0.06992,0.23447],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.50527,0.05576,0.02428],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20583,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":247.08623,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2723.0,"raw_peak_contact_force":252.6916,"subtask_id":"pre_contact","tcp_end":[0.51135,0.08115,0.0438],"tcp_start":[0.49878,0.06992,0.23447],"tcp_to_object_dist_end":0.0326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.49973,-0.01612,0.02491],"object_pos_start":[0.50527,0.05576,0.02428],"object_to_goal_dist_end":0.13388,"object_to_goal_dist_start":0.20583,"object_z_max":0.03625,"peak_contact_force":0.24596,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3021.0,"raw_peak_contact_force":157.13106,"subtask_id":"push_to_goal","tcp_end":[0.50753,-0.06096,0.03906],"tcp_start":[0.51135,0.08115,0.0438],"tcp_to_object_dist_end":0.04766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49943,-0.01635,0.02499],"object_pos_start":[0.49973,-0.01612,0.02491],"object_to_goal_dist_end":0.13365,"object_to_goal_dist_start":0.13388,"object_z_max":0.02572,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2122.0,"raw_peak_contact_force":2.62258,"tcp_end":[0.49691,-0.019,0.11452],"tcp_start":[0.50753,-0.06096,0.03906],"tcp_to_object_dist_end":0.08961,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14657,"push_1.push_speed":0.06221},"optimized_scores":{"best_composite_score":0.13721,"best_fitness_score":0.29721,"best_task_score":0.23891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.4859,-0.00209,0.04609],"force_p95":265.94143,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":265.97262,"mean_force":217.95601,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47489,0.00168,0.0463]},{"body_a":"world","body_b":"push_box","contact_count":2005.0,"contact_point_centroid":[0.47283,-0.02298,-0.0001],"force_p95":56.60483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":226.09115,"mean_force":11.74048,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46987,0.00086,0.10559]},{"body_a":"attachment","body_b":"push_box","contact_count":947.0,"contact_point_centroid":[0.49781,-0.04404,0.04707],"force_p95":138.50997,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.75932,"mean_force":114.07344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48784,-0.04814,0.04738]},{"body_a":"world","body_b":"push_box","contact_count":1830.0,"contact_point_centroid":[0.49833,-0.04521,-0.00062],"force_p95":110.21462,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.20901,"mean_force":59.76206,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48743,-0.04805,0.047]},{"body_a":"world","body_b":"push_box","contact_count":2336.0,"contact_point_centroid":[0.52008,-0.05491,-6e-05],"force_p95":0.46131,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.54989,"mean_force":0.27052,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49482,-0.09713,0.08422]},{"body_a":"world","body_b":"push_box","contact_count":1484.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48569,0.00033,0.24142]}],"total_contact_groups":6},"final_pose_error":0.01208,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52031,-0.05392,0.02499],"final_tcp_position":[0.51014,-0.0768,0.12448],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":265.97262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":840.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1484.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47183,0.0007,0.18133],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":990.0,"object_pos_end":[0.47531,-0.02319,0.02428],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1292,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":263.28915,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2110.0,"raw_peak_contact_force":265.97262,"subtask_id":"pre_contact","tcp_end":[0.4826,0.00226,0.0432],"tcp_start":[0.47183,0.0007,0.18133],"tcp_to_object_dist_end":0.03254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51553,-0.07444,0.03503],"object_pos_start":[0.47531,-0.02319,0.02428],"object_to_goal_dist_end":0.07779,"object_to_goal_dist_start":0.1292,"object_z_max":0.03508,"peak_contact_force":0.48622,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2777.0,"raw_peak_contact_force":173.75932,"subtask_id":"push_to_goal","tcp_end":[0.47986,-0.12233,0.03968],"tcp_start":[0.4826,0.00226,0.0432],"tcp_to_object_dist_end":0.05989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":720.0,"object_pos_end":[0.52031,-0.05392,0.02499],"object_pos_start":[0.51553,-0.07444,0.03503],"object_to_goal_dist_end":0.0982,"object_to_goal_dist_start":0.07779,"object_z_max":0.03503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2336.0,"raw_peak_contact_force":2.54989,"tcp_end":[0.51014,-0.0768,0.12448],"tcp_start":[0.47986,-0.12233,0.03968],"tcp_to_object_dist_end":0.10259,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```