## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.160) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
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
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_behind_distance:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_contact
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
    - 0.0
    - 0.012
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    descend_behind_distance:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_height:
      type: scalar
      range:
      - 0.005
      - 0.025
      default: 0.012
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: contact_object
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    contact_distance:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_low
    when: after_phase
    predicate: force_below
    threshold: 2.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.015
    - 0.0
  subtask_id: approach_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    max_time:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.012], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=negative}, tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - descend_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact_object** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - contact_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_low, when=after_phase, predicate=force_below, on_failure=retry, threshold=2.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.015, 0.0]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.160
- **task_score** (E): 0.692
- **fitness_score**: 0.598  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1824 |
| descend_to_contact | 1.00 | 1.00 | 0.1021 |
| contact_object | 0.67 | 1.00 | 0.0118 |
| push_to_goal | 1.00 | 1.00 | 0.1190 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.541, 0.082, 0.155) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.541, 0.082, 0.155)→(0.540, 0.068, 0.054) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 0.67 / force_exceeded | (0.534, 0.050, 0.050)→(0.528, 0.040, 0.048) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.667 | 13.001 | 13.906 |
| push_to_goal | push | 1.00 / time_limit | (0.528, 0.040, 0.048)→(0.497, -0.071, 0.044) | (0.526, -0.001, 0.025)→(0.513, -0.101, 0.031) | 0.156→0.054 | 1.00 / 3.333 | 18.397 | 25.944 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.751
- lateral_force_integral: None
- approach_alignment: 0.653
- goal_progress: 0.724
- terminal_score: 0.724
- phase_score: 0.564
- phase_breakdown.approach_object_score: 0.189
- phase_breakdown.reach_goal_score: 0.724

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.737
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.862
- **Median Q (composite search score)**: 0.103
- **K-run variance**: 0.0100
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.337


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10345,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_behind_distance":0.0898,"approach_behind.approach_height":0.093,"approach_behind.approach_speed":0.04848,"contact_object.contact_distance":0.05742,"contact_object.contact_force_threshold":4.56563,"contact_object.contact_speed":0.04,"descend_to_contact.descend_behind_distance":0.05714,"descend_to_contact.descend_height":0.00832,"descend_to_contact.descend_speed":0.04267,"push_to_goal.max_time":2.06901,"push_to_goal.push_distance":0.28196,"push_to_goal.push_speed":0.07322},"optimized_scores":{"best_composite_score":0.10318,"best_fitness_score":0.42984,"best_task_score":0.48898},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1439.0,"contact_point_centroid":[0.49685,-0.00519,-5e-05],"force_p95":17.14188,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.59023,"mean_force":5.94944,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46932,0.04083,0.03865]},{"body_a":"attachment","body_b":"push_box","contact_count":882.0,"contact_point_centroid":[0.48029,0.02458,0.0454],"force_p95":15.262,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.89767,"mean_force":6.86085,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46988,0.03415,0.03852]},{"body_a":"push_box","body_b":"link7","contact_count":275.0,"contact_point_centroid":[0.51746,-0.00865,0.0606],"force_p95":13.88035,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.72509,"mean_force":8.70448,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47403,-0.00578,0.03855]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.46772,0.08334,0.04298],"force_p95":16.6933,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.88055,"mean_force":8.92523,"phase_index":2.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.46753,0.09528,0.04271]},{"body_a":"world","body_b":"push_box","contact_count":1249.0,"contact_point_centroid":[0.47926,0.05849,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.41815,"mean_force":0.29411,"phase_index":2.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.46709,0.10569,0.04335]},{"body_a":"world","body_b":"push_box","contact_count":1864.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4848,0.06492,0.21581]},{"body_a":"world","body_b":"push_box","contact_count":888.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.46894,0.12574,0.08979]}],"total_contact_groups":7},"final_pose_error":0.16496,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50629,-0.04341,0.0328],"final_tcp_position":[0.47595,-0.02173,0.03877],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":24.59023,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.47038,0.13289,0.13086],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":888.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.46942,0.11786,0.04737],"tcp_start":[0.47038,0.13289,0.13086],"tcp_to_object_dist_end":0.06422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":314.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02501,"peak_contact_force":17.88055,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1256.0,"raw_peak_contact_force":17.88055,"subtask_id":"approach_object","tcp_end":[0.46735,0.09507,0.04247],"tcp_start":[0.46758,0.09531,0.04277],"tcp_to_object_dist_end":0.04226,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50629,-0.04341,0.0328],"object_pos_start":[0.47917,0.05822,0.02492],"object_to_goal_dist_end":0.10706,"object_to_goal_dist_start":0.20926,"object_z_max":0.03287,"peak_contact_force":22.89767,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2596.0,"raw_peak_contact_force":24.59023,"subtask_id":"reach_goal","tcp_end":[0.47595,-0.02173,0.03877],"tcp_start":[0.46735,0.09507,0.04247],"tcp_to_object_dist_end":0.03776,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95631,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_behind_distance":0.09041,"approach_behind.approach_height":0.13962,"approach_behind.approach_speed":0.08336,"contact_object.contact_distance":0.03855,"contact_object.contact_force_threshold":3.69324,"contact_object.contact_speed":0.02296,"descend_to_contact.descend_behind_distance":0.07269,"descend_to_contact.descend_height":0.01734,"descend_to_contact.descend_speed":0.02947,"push_to_goal.max_time":3.41792,"push_to_goal.push_distance":0.18214,"push_to_goal.push_speed":0.06727},"optimized_scores":{"best_composite_score":0.30116,"best_fitness_score":0.62782,"best_task_score":0.72406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":905.0,"contact_point_centroid":[0.52797,-0.0527,0.04488],"force_p95":18.42282,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.08628,"mean_force":9.38132,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52539,-0.04125,0.04575]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54986,-0.00059,0.04998],"force_p95":23.45506,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.59077,"mean_force":22.23368,"phase_index":2.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.54814,0.01126,0.05055]},{"body_a":"world","body_b":"push_box","contact_count":1635.0,"contact_point_centroid":[0.53481,-0.08955,-5e-05],"force_p95":12.80404,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.06098,"mean_force":5.60997,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52663,-0.03809,0.04588]},{"body_a":"world","body_b":"push_box","contact_count":3336.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17428,"mean_force":0.25856,"phase_index":2.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.55368,0.02614,0.05072]},{"body_a":"world","body_b":"push_box","contact_count":1248.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52967,0.0248,0.23927]},{"body_a":"world","body_b":"push_box","contact_count":1208.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.56201,0.04766,0.11741]}],"total_contact_groups":6},"final_pose_error":0.07278,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52173,-0.12189,0.03315],"final_tcp_position":[0.50763,-0.0907,0.0458],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.56226,0.05126,0.17712],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.56399,0.04375,0.05636],"tcp_start":[0.56226,0.05126,0.17712],"tcp_to_object_dist_end":0.07857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":20.8766,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3338.0,"raw_peak_contact_force":23.59077,"subtask_id":"approach_object","tcp_end":[0.54811,0.01124,0.0505],"tcp_start":[0.54814,0.01125,0.05054],"tcp_to_object_dist_end":0.04495,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52173,-0.12189,0.03315],"object_pos_start":[0.54443,-0.02559,0.02498],"object_to_goal_dist_end":0.03646,"object_to_goal_dist_start":0.13211,"object_z_max":0.03321,"peak_contact_force":13.13516,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2540.0,"raw_peak_contact_force":34.08628,"subtask_id":"reach_goal","tcp_end":[0.50763,-0.0907,0.0458],"tcp_start":[0.54811,0.01124,0.0505],"tcp_to_object_dist_end":0.03649,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84483,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_behind_distance":0.11614,"approach_behind.approach_height":0.11971,"approach_behind.approach_speed":0.06254,"contact_object.contact_distance":0.03442,"contact_object.contact_force_threshold":6.20209,"contact_object.contact_speed":0.02749,"descend_to_contact.descend_behind_distance":0.08218,"descend_to_contact.descend_height":0.01839,"descend_to_contact.descend_speed":0.02259,"push_to_goal.max_time":5.71221,"push_to_goal.push_distance":0.2239,"push_to_goal.push_speed":0.07858},"optimized_scores":{"best_composite_score":0.07702,"best_fitness_score":0.73702,"best_task_score":0.86228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":736.0,"contact_point_centroid":[0.53337,-0.06295,0.04548],"force_p95":13.52377,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.1569,"mean_force":5.99505,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53284,-0.05104,0.04556]},{"body_a":"world","body_b":"push_box","contact_count":1732.0,"contact_point_centroid":[0.53805,-0.08616,-3e-05],"force_p95":7.34602,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.47066,"mean_force":2.92307,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54149,-0.03382,0.046]},{"body_a":"world","body_b":"push_box","contact_count":1608.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54343,0.03004,0.22831]},{"body_a":"world","body_b":"push_box","contact_count":992.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.58729,0.05293,0.10744]},{"body_a":"world","body_b":"push_box","contact_count":2660.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.5746,0.02696,0.05113]}],"total_contact_groups":5},"final_pose_error":0.09419,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5107,-0.13657,0.02853],"final_tcp_position":[0.50861,-0.10197,0.04603],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":19.1569,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.59035,0.06174,0.15555],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":992.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.58613,0.04281,0.05707],"tcp_start":[0.59035,0.06174,0.15555],"tcp_to_object_dist_end":0.0899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":665.0,"n_steps_budget":810.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.56799,0.01365,0.05089],"tcp_start":[0.58613,0.04281,0.05707],"tcp_to_object_dist_end":0.05676,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5107,-0.13657,0.02853],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.01753,"object_to_goal_dist_start":0.12728,"object_z_max":0.02864,"peak_contact_force":19.1569,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2468.0,"raw_peak_contact_force":19.1569,"subtask_id":"reach_goal","tcp_end":[0.50861,-0.10197,0.04603],"tcp_start":[0.56799,0.01365,0.05089],"tcp_to_object_dist_end":0.03883,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```