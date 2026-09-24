## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1621 | 0.00 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2219 | 0.55 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.1885 | 0.00 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4456 | 0.49 | ✅ accepted |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3593 | 0.49 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.162) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
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
    - 0.03
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
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
    anchor: current_tcp
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
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.162
- **task_score** (E): 0.001
- **fitness_score**: 0.148  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0668 |
| descend_1 | 1.00 | 1.00 | 0.2031 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.0887 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.023, 0.247) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.023, 0.247)→(0.504, 0.027, 0.044) | (0.496, 0.001, 0.025)→(0.500, 0.002, 0.024) | 0.152→0.153 | 1.00 / 4.000 | 258.501 | 262.982 |
| push_1 | push | 0.00 / guard_failure | (0.504, 0.027, 0.044)→(0.504, 0.027, 0.044) | (0.500, 0.002, 0.024)→(0.500, 0.002, 0.024) | 0.153→0.153 | 1.00 / 4.000 | 128.834 | 128.834 |
| retract_1 | retract | 1.00 / step_budget | (0.504, 0.027, 0.044)→(0.501, 0.027, 0.133) | (0.500, 0.002, 0.024)→(0.498, 0.001, 0.025) | 0.153→0.152 | 1.00 / 4.000 | 0.245 | 138.983 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.015
- lateral_force_integral: None
- approach_alignment: 0.495
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.248
- phase_breakdown.pre_contact_score: 0.827
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.149
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.162
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.382


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60494,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26392,"approach_1.approach_speed":0.42601,"descend_1.descend_speed":0.14898,"push_1.push_distance":0.20553,"push_1.push_speed":0.01074},"optimized_scores":{"best_composite_score":-0.1611,"best_fitness_score":0.1489,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.52848,-0.00478,0.04669],"force_p95":256.45728,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":256.71866,"mean_force":204.58592,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51719,-0.00173,0.04721]},{"body_a":"world","body_b":"push_box","contact_count":3031.0,"contact_point_centroid":[0.5171,-0.02705,-4e-05],"force_p95":25.82364,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.96531,"mean_force":5.34991,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50907,-0.00191,0.16196]},{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.53501,-0.00487,0.04729],"force_p95":65.93409,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.8642,"mean_force":30.69989,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52373,-0.00134,0.04799]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53427,-0.00708,0.04483],"force_p95":122.85124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.57737,"mean_force":108.8946,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52392,-0.00116,0.04422]},{"body_a":"world","body_b":"push_box","contact_count":2067.0,"contact_point_centroid":[0.51846,-0.02688,-4e-05],"force_p95":0.27331,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.22834,"mean_force":0.87934,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52082,-0.00125,0.08967]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.52677,-0.02002,-0.00085],"force_p95":82.58054,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.54079,"mean_force":36.74375,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52392,-0.00116,0.04422]},{"body_a":"world","body_b":"push_box","contact_count":236.0,"contact_point_centroid":[0.51644,-0.02763,-0.0],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50274,-0.00054,0.29634]}],"total_contact_groups":7},"final_pose_error":0.01223,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51823,-0.02782,0.02499],"final_tcp_position":[0.5208,-0.00123,0.13252],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":256.71866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":59.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24526,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":236.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.50685,-0.00131,0.29141],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.26789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.51989,-0.02655,0.02425],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12504,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":252.12472,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3106.0,"raw_peak_contact_force":256.71866,"subtask_id":"pre_contact","tcp_end":[0.52381,-0.00115,0.0442],"tcp_start":[0.50685,-0.00131,0.29141],"tcp_to_object_dist_end":0.03253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51987,-0.02656,0.02425],"object_pos_start":[0.51989,-0.02655,0.02425],"object_to_goal_dist_end":0.12503,"object_to_goal_dist_start":0.12504,"object_z_max":0.02426,"peak_contact_force":124.57737,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":124.57737,"subtask_id":"push_to_goal","tcp_end":[0.52409,-0.00117,0.0443],"tcp_start":[0.52402,-0.00116,0.04424],"tcp_to_object_dist_end":0.03263,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":630.0,"object_pos_end":[0.51823,-0.02782,0.02499],"object_pos_start":[0.5198,-0.0266,0.02427],"object_to_goal_dist_end":0.12353,"object_to_goal_dist_start":0.12498,"object_z_max":0.02533,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2109.0,"raw_peak_contact_force":132.8642,"tcp_end":[0.5208,-0.00123,0.13252],"tcp_start":[0.52409,-0.00117,0.0443],"tcp_to_object_dist_end":0.1108,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2133,"approach_1.approach_speed":0.10518,"descend_1.descend_speed":0.14963,"push_1.push_distance":0.23104,"push_1.push_speed":0.06843},"optimized_scores":{"best_composite_score":-0.16153,"best_fitness_score":0.14847,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":76.0,"contact_point_centroid":[0.5139,0.07587,0.04671],"force_p95":259.01513,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":259.45643,"mean_force":204.46111,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50265,0.07891,0.04727]},{"body_a":"world","body_b":"push_box","contact_count":2450.0,"contact_point_centroid":[0.50225,0.0548,-5e-05],"force_p95":26.52416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":227.42122,"mean_force":6.63252,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49776,0.07378,0.137]},{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.52003,0.07687,0.04728],"force_p95":65.28258,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.7738,"mean_force":31.46201,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5088,0.08048,0.04802]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51917,0.07452,0.04475],"force_p95":127.64829,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.42991,"mean_force":111.9225,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50897,0.08068,0.04412]},{"body_a":"world","body_b":"push_box","contact_count":2063.0,"contact_point_centroid":[0.50335,0.05542,-4e-05],"force_p95":0.26526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.7214,"mean_force":0.91205,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50596,0.08014,0.08982]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.51165,0.06222,-0.00086],"force_p95":84.95414,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.40817,"mean_force":37.80331,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50897,0.08068,0.04412]},{"body_a":"world","body_b":"push_box","contact_count":1364.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49866,0.03423,0.26934]}],"total_contact_groups":7},"final_pose_error":0.01205,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50307,0.05453,0.02499],"final_tcp_position":[0.50593,0.08017,0.1326],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":259.45643,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":630.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49883,0.06972,0.24046],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.21606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":900.0,"object_pos_end":[0.50484,0.05574,0.02426],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.2058,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":254.08404,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2526.0,"raw_peak_contact_force":259.45643,"subtask_id":"pre_contact","tcp_end":[0.50886,0.08066,0.0441],"tcp_start":[0.49883,0.06972,0.24046],"tcp_to_object_dist_end":0.0321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50482,0.05573,0.02426],"object_pos_start":[0.50484,0.05574,0.02426],"object_to_goal_dist_end":0.20579,"object_to_goal_dist_start":0.2058,"object_z_max":0.02426,"peak_contact_force":129.42991,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":129.42991,"subtask_id":"push_to_goal","tcp_end":[0.50914,0.08069,0.0442],"tcp_start":[0.50906,0.08069,0.04414],"tcp_to_object_dist_end":0.03223,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":630.0,"object_pos_end":[0.50307,0.05453,0.02499],"object_pos_start":[0.50476,0.0557,0.02427],"object_to_goal_dist_end":0.20455,"object_to_goal_dist_start":0.20575,"object_z_max":0.02536,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2106.0,"raw_peak_contact_force":136.7738,"tcp_end":[0.50593,0.08017,0.1326],"tcp_start":[0.50914,0.08069,0.0442],"tcp_to_object_dist_end":0.11066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91549,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17339,"approach_1.approach_speed":0.29707,"descend_1.descend_speed":0.14979,"push_1.push_distance":0.28968,"push_1.push_speed":0.05678},"optimized_scores":{"best_composite_score":-0.16361,"best_fitness_score":0.14639,"best_task_score":0.00282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.48465,-0.0016,0.04649],"force_p95":272.6013,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":272.77133,"mean_force":216.59085,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47343,0.00157,0.04693]},{"body_a":"world","body_b":"push_box","contact_count":2119.0,"contact_point_centroid":[0.47234,-0.02336,-6e-05],"force_p95":33.69741,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":229.24493,"mean_force":7.96924,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47007,0.00079,0.12112]},{"body_a":"attachment","body_b":"push_box","contact_count":45.0,"contact_point_centroid":[0.49109,-0.00172,0.04714],"force_p95":65.08405,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.31122,"mean_force":31.46211,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47989,0.00203,0.04776]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49003,-0.00426,0.04445],"force_p95":130.2554,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.49355,"mean_force":109.33127,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48,0.00222,0.04359]},{"body_a":"world","body_b":"push_box","contact_count":2158.0,"contact_point_centroid":[0.47313,-0.02335,-4e-05],"force_p95":0.26439,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.54491,"mean_force":0.91133,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47714,0.00212,0.09028]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.48148,-0.01664,-0.00089],"force_p95":93.23145,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.3378,"mean_force":36.92494,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48,0.00222,0.04359]},{"body_a":"world","body_b":"push_box","contact_count":1152.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48647,0.00032,0.25494]}],"total_contact_groups":7},"final_pose_error":0.0111,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47281,-0.02424,0.02499],"final_tcp_position":[0.4771,0.00215,0.133],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":272.77133,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47291,0.00068,0.20799],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":780.0,"object_pos_end":[0.47477,-0.02308,0.02422],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12941,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":269.29275,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2194.0,"raw_peak_contact_force":272.77133,"subtask_id":"pre_contact","tcp_end":[0.47988,0.00222,0.04358],"tcp_start":[0.47291,0.00068,0.20799],"tcp_to_object_dist_end":0.03226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47476,-0.02309,0.02423],"object_pos_start":[0.47477,-0.02308,0.02422],"object_to_goal_dist_end":0.1294,"object_to_goal_dist_start":0.12941,"object_z_max":0.02424,"peak_contact_force":132.49355,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":132.49355,"subtask_id":"push_to_goal","tcp_end":[0.4802,0.00221,0.04367],"tcp_start":[0.48011,0.00221,0.04361],"tcp_to_object_dist_end":0.03236,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":660.0,"object_pos_end":[0.47281,-0.02424,0.02499],"object_pos_start":[0.4747,-0.02313,0.02425],"object_to_goal_dist_end":0.12867,"object_to_goal_dist_start":0.12937,"object_z_max":0.02529,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2203.0,"raw_peak_contact_force":147.31122,"tcp_end":[0.4771,0.00215,0.133],"tcp_start":[0.4802,0.00221,0.04367],"tcp_to_object_dist_end":0.11128,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```