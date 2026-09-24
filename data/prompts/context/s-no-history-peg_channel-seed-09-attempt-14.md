## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.271) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - -0.005
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
    entity: peg
    offset:
    - 0.0
    - 0.08
    - -0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: side_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - -0.005
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_guard
    when: after_phase
    predicate: force_below
    threshold: 10.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - -0.005
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: after_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - -0.05
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, -0.005], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **side_contact** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, -0.005], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=after_phase, predicate=force_below, on_failure=retry, threshold=10.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, -0.005], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=after_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, -0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.271
- **task_score** (E): 0.137
- **fitness_score**: 0.211  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1725 |
| descend_to_contact | 1.00 | 1.00 | 0.0016 |
| lateral_center | 1.00 | 1.00 | 0.0029 |
| channel_push | 1.00 | 1.00 | 0.0200 |
| retract_after_push | 1.00 | 1.00 | 0.1014 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.536, 0.150, 0.142) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.547 | 4.034 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.530, 0.105, 0.058)→(0.530, 0.104, 0.057) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 49.577 | 65.223 |
| lateral_center | push | 1.00 / force_exceeded | (0.525, 0.103, 0.054)→(0.523, 0.102, 0.052) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.146 | 1.00 / 2.333 | 57.666 | 57.666 |
| channel_push | push | 1.00 / time_limit | (0.530, 0.017, 0.054)→(0.534, 0.000, 0.062) | (0.502, 0.065, 0.034)→(0.506, 0.012, 0.035) | 0.146→0.096 | 1.00 / 3.000 | 269.821 | 584.372 |
| retract_after_push | retract | 1.00 / step_budget | (0.534, 0.000, 0.062)→(0.531, -0.045, 0.153) | (0.500, 0.015, 0.044)→(0.503, 0.025, 0.031) | 0.102→0.106 | 1.00 / 1.000 | 0.572 | 136.425 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.410
- phase_score: 0.604
- phase_breakdown.contact_peg_side_score: 0.669
- phase_breakdown.center_peg_score: 0.000
- phase_breakdown.push_channel_score: 0.941

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.527
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.410
- **Median Q (composite search score)**: 0.114
- **K-run variance**: 0.0499
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.325


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10204,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.17836,"channel_push.push_distance":0.14212,"channel_push.push_speed":0.0733,"descend_to_contact.contact_force_threshold":7.74475,"lateral_center.lateral_distance":0.03279,"lateral_center.lateral_force_threshold":28.33672,"lateral_center.lateral_speed":0.07029},"optimized_scores":{"best_composite_score":0.1141,"best_fitness_score":0.0541,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2870.0,"contact_point_centroid":[0.54328,0.05658,0.05995],"force_p95":441.30721,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":490.31776,"mean_force":247.6593,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.53793,0.06526,0.06178]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.54565,0.03177,0.05999],"force_p95":109.25573,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.94068,"mean_force":76.14758,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.54541,0.04326,0.0634]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.54952,0.10318,0.05986],"force_p95":63.2059,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.47321,"mean_force":54.12254,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53766,0.10375,0.0615]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.54947,0.10301,0.05974],"force_p95":46.93551,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.28701,"mean_force":43.80863,"phase_index":2.0,"phase_name":"lateral_center","phase_type":"push","tcp_position_centroid":[0.53761,0.10358,0.06125]},{"body_a":"peg","body_b":"channel_base_body","contact_count":488.0,"contact_point_centroid":[0.50571,0.06304,0.00935],"force_p95":0.57657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57428,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.52646,0.17156,0.21526]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50087,0.19842,0.29557]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2902.0,"contact_point_centroid":[0.50601,0.06297,0.00939],"force_p95":0.55122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55544,"mean_force":0.54634,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.53792,0.06539,0.06178]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50599,0.06284,0.00938],"force_p95":0.5519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54385,0.12498,0.09959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.50584,0.06299,0.00939],"force_p95":0.55117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55489,"mean_force":0.54622,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.54264,0.02601,0.11089]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49724,0.07579,0.00939],"force_p95":0.54845,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5486,"mean_force":0.54569,"phase_index":2.0,"phase_name":"lateral_center","phase_type":"push","tcp_position_centroid":[0.53761,0.10358,0.06125]}],"total_contact_groups":10},"final_pose_error":0.0105,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50604,0.06307,0.03387],"final_tcp_position":[0.54272,-0.00194,0.15444],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":490.31776,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":516.0,"n_steps_budget":660.0,"object_pos_end":[0.50603,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54538,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":522.0,"raw_peak_contact_force":3.88411,"subtask_id":"contact_peg_side","tcp_end":[0.55222,0.1461,0.14081],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":405.0,"n_steps_budget":810.0,"object_pos_end":[0.50596,0.06295,0.03381],"object_pos_start":[0.50603,0.06297,0.0338],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":46.09434,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":408.0,"raw_peak_contact_force":64.47321,"subtask_id":"contact_peg_side","tcp_end":[0.53762,0.10362,0.06131],"tcp_start":[0.53764,0.10368,0.06138],"tcp_to_object_dist_end":0.05842,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.06303,0.03381],"object_pos_start":[0.50594,0.063,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":47.28701,"phase_name":"lateral_center","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":47.28701,"subtask_id":"center_peg","tcp_end":[0.5376,0.10351,0.06117],"tcp_start":[0.53761,0.10354,0.0612],"tcp_to_object_dist_end":0.05821,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.06292,0.03385],"object_pos_start":[0.50601,0.06302,0.03381],"object_to_goal_dist_end":0.14318,"object_to_goal_dist_start":0.14328,"object_z_max":0.03388,"peak_contact_force":285.13024,"phase_name":"channel_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5772.0,"raw_peak_contact_force":490.31776,"subtask_id":"push_channel","tcp_end":[0.5454,0.04324,0.06338],"tcp_start":[0.542,0.05727,0.0621],"tcp_to_object_dist_end":0.0531,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50604,0.06307,0.03387],"object_pos_start":[0.50596,0.06285,0.03387],"object_to_goal_dist_end":0.14333,"object_to_goal_dist_start":0.14311,"object_z_max":0.03388,"peak_contact_force":0.55079,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":636.0,"raw_peak_contact_force":114.94068,"tcp_end":[0.54272,-0.00194,0.15444],"tcp_start":[0.5454,0.04324,0.06338],"tcp_to_object_dist_end":0.14181,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.08617,"channel_push.push_distance":0.12304,"channel_push.push_speed":0.09804,"descend_to_contact.contact_force_threshold":8.24892,"lateral_center.lateral_distance":0.04855,"lateral_center.lateral_force_threshold":45.97684,"lateral_center.lateral_speed":0.01955},"optimized_scores":{"best_composite_score":0.11134,"best_fitness_score":0.05134,"best_task_score":8e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2875.0,"contact_point_centroid":[0.54156,0.05546,0.05995],"force_p95":425.93063,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.3772,"mean_force":244.79349,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.53888,0.06525,0.06201]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.54352,0.03207,0.05997],"force_p95":117.56344,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.77741,"mean_force":76.188,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.54467,0.04339,0.06377]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.55185,0.09689,0.0597],"force_p95":106.82354,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.68956,"mean_force":59.48252,"phase_index":2.0,"phase_name":"lateral_center","phase_type":"push","tcp_position_centroid":[0.54,0.09749,0.06118]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.55195,0.09716,0.05989],"force_p95":70.45716,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.66075,"mean_force":57.09622,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5401,0.09776,0.06156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.50584,0.05662,0.00935],"force_p95":0.60579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57359,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.52959,0.16854,0.21527]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50075,0.19846,0.29606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2902.0,"contact_point_centroid":[0.50616,0.05661,0.00939],"force_p95":0.55054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55661,"mean_force":0.54631,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.53888,0.06532,0.06201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":396.0,"contact_point_centroid":[0.50626,0.05667,0.00938],"force_p95":0.55274,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55568,"mean_force":0.54655,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54839,0.11907,0.09944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49829,0.05062,0.00939],"force_p95":0.55365,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55564,"mean_force":0.54667,"phase_index":2.0,"phase_name":"lateral_center","phase_type":"push","tcp_position_centroid":[0.54,0.09749,0.06118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.50609,0.05653,0.00939],"force_p95":0.54943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55352,"mean_force":0.54626,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.54202,0.02613,0.11144]}],"total_contact_groups":10},"final_pose_error":0.01025,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50602,0.05657,0.03386],"final_tcp_position":[0.54211,-0.00185,0.15505],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":475.3772,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05665,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5483,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":623.0,"raw_peak_contact_force":4.44541,"subtask_id":"contact_peg_side","tcp_end":[0.55876,0.14004,0.14013],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":396.0,"n_steps_budget":840.0,"object_pos_end":[0.5062,0.05663,0.03383],"object_pos_start":[0.50615,0.05665,0.0338],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13693,"object_z_max":0.03383,"peak_contact_force":50.62485,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":399.0,"raw_peak_contact_force":72.66075,"subtask_id":"contact_peg_side","tcp_end":[0.54004,0.09761,0.06133],"tcp_start":[0.54006,0.09768,0.06142],"tcp_to_object_dist_end":0.05985,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.05664,0.03383],"object_pos_start":[0.50617,0.05656,0.03383],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13683,"object_z_max":0.03383,"peak_contact_force":113.68956,"phase_name":"lateral_center","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":113.68956,"subtask_id":"center_peg","tcp_end":[0.53994,0.09737,0.06106],"tcp_start":[0.53995,0.09739,0.06107],"tcp_to_object_dist_end":0.05957,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.05653,0.03385],"object_pos_start":[0.50612,0.05668,0.03383],"object_to_goal_dist_end":0.1368,"object_to_goal_dist_start":0.13696,"object_z_max":0.03386,"peak_contact_force":253.61895,"phase_name":"channel_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5777.0,"raw_peak_contact_force":475.3772,"subtask_id":"push_channel","tcp_end":[0.54466,0.04337,0.06375],"tcp_start":[0.54171,0.06066,0.06252],"tcp_to_object_dist_end":0.05057,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50602,0.05657,0.03386],"object_pos_start":[0.50611,0.05649,0.03386],"object_to_goal_dist_end":0.13684,"object_to_goal_dist_start":0.13677,"object_z_max":0.03386,"peak_contact_force":0.54529,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":636.0,"raw_peak_contact_force":124.77741,"tcp_end":[0.54211,-0.00185,0.15505],"tcp_start":[0.54466,0.04337,0.06375],"tcp_to_object_dist_end":0.13929,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85165,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.10744,"channel_push.push_distance":0.16232,"channel_push.push_speed":0.13846,"descend_to_contact.contact_force_threshold":8.06986,"lateral_center.lateral_distance":0.05091,"lateral_center.lateral_force_threshold":18.53838,"lateral_center.lateral_speed":0.06617},"optimized_scores":{"best_composite_score":0.58672,"best_fitness_score":0.52672,"best_task_score":0.41035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":76.0,"contact_point_centroid":[0.51618,-0.10019,0.06495],"force_p95":770.84147,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":787.42025,"mean_force":447.88321,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.51066,-0.08603,0.05807]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1310.0,"contact_point_centroid":[0.52513,-0.07485,0.05996],"force_p95":583.42801,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":763.64625,"mean_force":355.8946,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.5079,-0.07207,0.04172]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1383.0,"contact_point_centroid":[0.56919,-0.11123,0.06492],"force_p95":538.79794,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":625.49146,"mean_force":346.60639,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.50408,-0.06747,0.03657]},{"body_a":"attachment","body_b":"peg","contact_count":2375.0,"contact_point_centroid":[0.50032,-0.05046,0.04863],"force_p95":162.01342,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.14303,"mean_force":89.74296,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.50004,-0.04328,0.03573]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1448.0,"contact_point_centroid":[0.49367,-0.10201,0.04392],"force_p95":147.97873,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.68105,"mean_force":66.63468,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.50465,-0.06789,0.03666]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1286.0,"contact_point_centroid":[0.47233,-0.08157,0.04438],"force_p95":164.24394,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.99908,"mean_force":93.52063,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.50757,-0.06919,0.0422]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52509,-0.08767,0.05995],"force_p95":121.92382,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.55683,"mean_force":33.11242,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51108,-0.08579,0.05936]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51624,-0.10003,0.06499],"force_p95":103.46131,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.20136,"mean_force":73.00175,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51095,-0.08583,0.05905]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":991.0,"contact_point_centroid":[0.52545,-0.04079,0.05618],"force_p95":47.69422,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.15961,"mean_force":31.54354,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.49066,-0.01619,0.0279]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":120.0,"contact_point_centroid":[0.47441,-0.07231,0.05658],"force_p95":66.02853,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.04671,"mean_force":18.20764,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.5099,-0.08929,0.07279]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.50318,-0.08103,0.07332],"force_p95":70.94869,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.96774,"mean_force":22.71755,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51043,-0.08715,0.06668]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.57999,-0.12,0.06497],"force_p95":69.73229,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.03715,"mean_force":45.1524,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.51095,-0.08583,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":957.0,"contact_point_centroid":[0.50759,-0.03534,0.00984],"force_p95":40.53936,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.86733,"mean_force":19.95407,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.48971,0.00267,0.02816]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52501,0.11512,0.06],"force_p95":56.90508,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.53582,"mean_force":29.20113,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51188,0.11515,0.05348]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.475,0.06459,0.03084],"force_p95":40.50218,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.40257,"mean_force":27.91696,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.4868,0.06458,0.02864]},{"body_a":"peg","body_b":"link7","contact_count":993.0,"contact_point_centroid":[0.51481,-0.03942,0.06784],"force_p95":27.55555,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.87304,"mean_force":18.97237,"phase_index":3.0,"phase_name":"channel_push","phase_type":"push","tcp_position_centroid":[0.49524,-0.02059,0.03121]}],"total_contact_groups":26},"final_pose_error":0.01161,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49761,-0.04462,0.02421],"final_tcp_position":[0.50784,-0.13037,0.14925],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":788.55644,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":481.0,"n_steps_budget":990.0,"object_pos_end":[0.49383,0.07996,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54635,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":488.0,"raw_peak_contact_force":3.77147,"subtask_id":"contact_peg_side","tcp_end":[0.49735,0.16241,0.14417],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":642.0,"n_steps_budget":840.0,"object_pos_end":[0.49383,0.07996,0.03378],"object_pos_start":[0.49383,0.07996,0.03377],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":52.01286,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":648.0,"raw_peak_contact_force":58.53582,"subtask_id":"contact_peg_side","tcp_end":[0.51087,0.11166,0.04739],"tcp_start":[0.51155,0.11398,0.05143],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.49304,0.07824,0.0344],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.15849,"object_to_goal_dist_start":0.16017,"object_z_max":0.03518,"peak_contact_force":12.02233,"phase_name":"lateral_center","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":193.0,"raw_peak_contact_force":12.02233,"subtask_id":"center_peg","tcp_end":[0.49002,0.10636,0.03375],"tcp_start":[0.49732,0.10774,0.03832],"tcp_to_object_dist_end":0.02829,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2475.0,"n_steps_budget":870.0,"object_pos_end":[0.5073,-0.08305,0.03663],"object_pos_start":[0.49293,0.07657,0.03462],"object_to_goal_dist_end":0.0086,"object_to_goal_dist_start":0.15682,"object_z_max":0.06543,"peak_contact_force":270.71232,"phase_name":"channel_push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10825.0,"raw_peak_contact_force":787.42025,"subtask_id":"push_channel","tcp_end":[0.5109,-0.08586,0.05902],"tcp_start":[0.50733,-0.06777,0.03818],"tcp_to_object_dist_end":0.02285,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":628.0,"n_steps_budget":720.0,"object_pos_end":[0.49761,-0.04462,0.02421],"object_pos_start":[0.48925,-0.07332,0.06379],"object_to_goal_dist_end":0.03882,"object_to_goal_dist_start":0.02695,"object_z_max":0.0695,"peak_contact_force":0.6196,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":767.0,"raw_peak_contact_force":169.55683,"tcp_end":[0.50784,-0.13037,0.14925],"tcp_start":[0.5109,-0.08586,0.05902],"tcp_to_object_dist_end":0.15197,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```