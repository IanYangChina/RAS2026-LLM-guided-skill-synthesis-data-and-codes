## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

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

## Current Skill (Q=0.273) — your mutation base

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

- **Composite score**: 0.273
- **task_score** (E): 0.236
- **fitness_score**: 0.533  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.2124 |
| descend_to_peg | 1.00 | 1.00 | 0.0690 |
| push_along_channel | 1.00 | 1.00 | 0.0075 |
| retract | 1.00 | 1.00 | 0.1019 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.116, 0.107) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.546 | 4.034 |
| descend_to_peg | descend | 1.00 / step_budget | (0.508, 0.116, 0.107)→(0.498, 0.096, 0.045) | (0.502, 0.067, 0.034)→(0.501, 0.065, 0.034) | 0.147→0.145 | 1.00 / 1.667 | 133.980 | 260.994 |
| push_along_channel | push | 1.00 / time_limit | (0.522, 0.089, 0.063)→(0.525, 0.088, 0.061) | (0.501, 0.065, 0.034)→(0.499, -0.057, 0.024) | 0.145→0.029 | 1.00 / 3.667 | 421.173 | 1434.968 |
| retract | retract | 1.00 / step_budget | (0.525, 0.088, 0.061)→(0.524, 0.042, 0.152) | (0.496, -0.057, 0.024)→(0.496, -0.057, 0.024) | 0.029→0.029 | 1.00 / 1.000 | 0.546 | 596.455 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.935
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.384
- phase_score: 0.796
- phase_breakdown.reach_peg_score: 0.608
- phase_breakdown.push_to_goal_score: 0.877

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.631
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.384
- **Median Q (composite search score)**: 0.247
- **K-run variance**: 0.0053
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.41497,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.1904,"descend_to_peg.descend_speed":0.11981,"push_along_channel.push_distance":0.16681,"push_along_channel.push_speed":0.02894},"optimized_scores":{"best_composite_score":0.24732,"best_fitness_score":0.50732,"best_task_score":0.21959},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2256.0,"contact_point_centroid":[0.52511,0.08408,0.05171],"force_p95":584.46263,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1439.14673,"mean_force":385.98737,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51323,0.08254,0.05141]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1469.0,"contact_point_centroid":[0.47493,0.11986,0.05912],"force_p95":791.22521,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":847.64107,"mean_force":676.26233,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51337,0.08285,0.05171]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":174.0,"contact_point_centroid":[0.53022,0.11938,0.05995],"force_p95":581.00646,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":714.54009,"mean_force":274.58894,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5113,0.07935,0.05184]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":71.0,"contact_point_centroid":[0.47472,0.11999,0.06],"force_p95":193.68213,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":660.20582,"mean_force":62.78411,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51231,0.08651,0.06156]},{"body_a":"world","body_b":"link7","contact_count":2238.0,"contact_point_centroid":[0.51014,0.14538,-8e-05],"force_p95":363.93095,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":499.00228,"mean_force":271.58267,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51262,0.08287,0.05127]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52505,0.08944,0.05382],"force_p95":405.93109,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":448.48759,"mean_force":205.04009,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51336,0.08697,0.05369]},{"body_a":"world","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.35935,0.2167,-2e-05],"force_p95":297.3427,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.19915,"mean_force":142.81793,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51337,0.08689,0.05364]},{"body_a":"world","body_b":"link5","contact_count":344.0,"contact_point_centroid":[0.37784,0.20963,-2e-05],"force_p95":272.14333,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.61197,"mean_force":144.62918,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51333,0.08424,0.05347]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2858.0,"contact_point_centroid":[0.49916,-0.04635,0.0081],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.20978,"mean_force":0.64523,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5126,0.08296,0.05162]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50513,0.07681,0.03765],"force_p95":26.85671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.05449,"mean_force":23.37896,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50557,0.08876,0.03663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.50611,0.06178,0.00941],"force_p95":0.62009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.97809,"mean_force":0.67788,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51364,0.10171,0.0719]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50565,0.07987,0.0452],"force_p95":11.72345,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.67589,"mean_force":4.03444,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50555,0.09187,0.04242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52513,-0.00168,0.02776],"force_p95":8.14535,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.21649,"mean_force":1.29594,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50776,0.08131,0.043]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47492,-0.05734,0.03764],"force_p95":8.03208,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.11931,"mean_force":1.69749,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5112,0.08306,0.05289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":571.0,"contact_point_centroid":[0.5058,0.06296,0.00936],"force_p95":0.56471,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57025,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51195,0.15442,0.198]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50009,0.19791,0.29545]}],"total_contact_groups":17},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50164,-0.0479,0.02413],"final_tcp_position":[0.51221,0.04172,0.14496],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1439.14673,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":750.0,"object_pos_end":[0.50595,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54678,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":605.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.5245,0.11274,0.10683],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":600.0,"object_pos_end":[0.50418,0.06021,0.03455],"object_pos_start":[0.50595,0.06295,0.03381],"object_to_goal_dist_end":0.14038,"object_to_goal_dist_start":0.14321,"object_z_max":0.03452,"peak_contact_force":0.50917,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":14.97809,"subtask_id":"reach_peg","tcp_end":[0.50431,0.0903,0.03776],"tcp_start":[0.5245,0.11274,0.10683],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.4996,-0.04737,0.02413],"object_pos_start":[0.50418,0.06021,0.03455],"object_to_goal_dist_end":0.03629,"object_to_goal_dist_start":0.14038,"object_z_max":0.0433,"peak_contact_force":277.61197,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9390.0,"raw_peak_contact_force":1439.14673,"subtask_id":"push_to_goal","tcp_end":[0.51337,0.08689,0.05361],"tcp_start":[0.51342,0.08688,0.05249],"tcp_to_object_dist_end":0.13814,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":616.0,"n_steps_budget":720.0,"object_pos_end":[0.50164,-0.0479,0.02413],"object_pos_start":[0.4982,-0.04769,0.02413],"object_to_goal_dist_end":0.03585,"object_to_goal_dist_start":0.03604,"object_z_max":0.02413,"peak_contact_force":0.53262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":696.0,"raw_peak_contact_force":660.20582,"tcp_end":[0.51221,0.04172,0.14496],"tcp_start":[0.51337,0.08689,0.05361],"tcp_to_object_dist_end":0.15082,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.43226,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12304,"descend_to_peg.descend_speed":0.12231,"push_along_channel.push_distance":0.15186,"push_along_channel.push_speed":0.11683},"optimized_scores":{"best_composite_score":0.19916,"best_fitness_score":0.45916,"best_task_score":0.10271},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1862.0,"contact_point_centroid":[0.52885,0.10219,0.05985],"force_p95":431.18679,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1463.67627,"mean_force":313.1649,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53544,0.08171,0.07169]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":298.0,"contact_point_centroid":[0.47496,0.11999,0.05999],"force_p95":356.94664,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1197.38631,"mean_force":259.42804,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53507,0.08141,0.07245]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2138.0,"contact_point_centroid":[0.52518,0.11989,0.05435],"force_p95":378.54885,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1179.80326,"mean_force":271.83871,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52903,0.0793,0.07825]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52526,0.09197,0.05994],"force_p95":308.08888,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.35517,"mean_force":223.51501,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51339,0.09208,0.06076]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53086,0.11999,0.05993],"force_p95":140.3525,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.41898,"mean_force":118.04232,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54874,0.08986,0.07462]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.52501,0.11999,0.05207],"force_p95":75.7888,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.35957,"mean_force":46.13211,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54716,0.08908,0.08467]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50637,0.07032,0.03839],"force_p95":30.52085,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.18729,"mean_force":18.70462,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50711,0.08214,0.03655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2755.0,"contact_point_centroid":[0.49438,-0.05265,0.00812],"force_p95":0.80648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.11191,"mean_force":0.80912,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53023,0.07976,0.07676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":329.0,"contact_point_centroid":[0.50593,0.05575,0.00939],"force_p95":0.62429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.48823,"mean_force":0.69456,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51737,0.09557,0.0714]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50647,0.07341,0.04439],"force_p95":13.17143,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.99095,"mean_force":4.39335,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50658,0.08536,0.04121]},{"body_a":"peg","body_b":"channel_base_body","contact_count":630.0,"contact_point_centroid":[0.49328,-0.05427,0.0081],"force_p95":0.73739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.8899,"mean_force":0.79528,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54727,0.07295,0.12175]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":125.0,"contact_point_centroid":[0.47498,-0.05604,0.02475],"force_p95":9.25087,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.78484,"mean_force":4.24201,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53156,0.08031,0.07288]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47498,-0.05418,0.02474],"force_p95":9.31531,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.4047,"mean_force":4.30924,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54716,0.0796,0.11266]},{"body_a":"peg","body_b":"channel_base_body","contact_count":654.0,"contact_point_centroid":[0.50589,0.05664,0.00936],"force_p95":0.60081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57091,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51513,0.15146,0.19817]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50005,0.19801,0.29585]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52503,0.00713,0.04795],"force_p95":1.40506,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4916,"mean_force":0.84274,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50836,0.06848,0.04385]}],"total_contact_groups":16},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49333,-0.05408,0.02413],"final_tcp_position":[0.54754,0.0445,0.1659],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1463.67627,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05662,0.03379],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.5465,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":691.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.53096,0.10665,0.10635],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":329.0,"n_steps_budget":600.0,"object_pos_end":[0.5051,0.05437,0.03414],"object_pos_start":[0.50616,0.05662,0.03379],"object_to_goal_dist_end":0.13459,"object_to_goal_dist_start":0.1369,"object_z_max":0.03427,"peak_contact_force":6.33052,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":357.0,"raw_peak_contact_force":308.35517,"subtask_id":"reach_peg","tcp_end":[0.50541,0.08422,0.03796],"tcp_start":[0.53096,0.10665,0.10635],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2796.0,"n_steps_budget":990.0,"object_pos_end":[0.49305,-0.0537,0.02413],"object_pos_start":[0.5051,0.05437,0.03414],"object_to_goal_dist_end":0.03149,"object_to_goal_dist_start":0.13459,"object_z_max":0.04065,"peak_contact_force":337.63319,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7189.0,"raw_peak_contact_force":1463.67627,"subtask_id":"push_to_goal","tcp_end":[0.5487,0.08982,0.07456],"tcp_start":[0.53873,0.08526,0.0754],"tcp_to_object_dist_end":0.16198,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":720.0,"object_pos_end":[0.49333,-0.05408,0.02413],"object_pos_start":[0.49332,-0.05427,0.02415],"object_to_goal_dist_end":0.03112,"object_to_goal_dist_start":0.03095,"object_z_max":0.02551,"peak_contact_force":0.57752,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":753.0,"raw_peak_contact_force":143.41898,"tcp_end":[0.54754,0.0445,0.1659],"tcp_start":[0.5487,0.08982,0.07456],"tcp_to_object_dist_end":0.18097,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.67832,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.19704,"descend_to_peg.descend_speed":0.11779,"push_along_channel.push_distance":0.14209,"push_along_channel.push_speed":0.09763},"optimized_scores":{"best_composite_score":0.37129,"best_fitness_score":0.63129,"best_task_score":0.3843},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.52909,0.11981,0.05111],"force_p95":1120.40798,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1402.08006,"mean_force":337.95088,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50823,0.08594,0.04603]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.47472,0.11997,0.05966],"force_p95":334.11832,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":985.7392,"mean_force":90.68037,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51208,0.08485,0.06978]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2209.0,"contact_point_centroid":[0.46971,0.1199,0.05695],"force_p95":784.28326,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":840.1635,"mean_force":452.8005,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50678,0.08412,0.05175]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52514,0.08851,0.05386],"force_p95":641.10092,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":712.72976,"mean_force":314.66474,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51352,0.08616,0.05387]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1260.0,"contact_point_centroid":[0.52512,0.08836,0.05233],"force_p95":585.90626,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":647.21352,"mean_force":421.82526,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51345,0.08592,0.05211]},{"body_a":"world","body_b":"link7","contact_count":2408.0,"contact_point_centroid":[0.49466,0.14777,-8e-05],"force_p95":508.34955,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":621.59738,"mean_force":281.73981,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50524,0.08515,0.05202]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":49.0,"contact_point_centroid":[0.47475,0.09691,0.0354],"force_p95":221.64718,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":615.20126,"mean_force":160.08572,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48638,0.09552,0.03485]},{"body_a":"world","body_b":"link6","contact_count":56.0,"contact_point_centroid":[0.45129,0.26553,-0.00011],"force_p95":526.01838,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":602.77716,"mean_force":398.31158,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51398,0.09431,0.05976]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":188.0,"contact_point_centroid":[0.47499,0.11445,0.05993],"force_p95":434.07977,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.64813,"mean_force":395.1068,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48276,0.11366,0.05853]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.50988,0.14849,-1e-05],"force_p95":229.97214,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.63535,"mean_force":197.00328,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51347,0.08596,0.05359]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49392,0.09533,0.05602],"force_p95":50.20308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.34503,"mean_force":34.26706,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4938,0.10652,0.05525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2840.0,"contact_point_centroid":[0.50187,-0.06799,0.00808],"force_p95":0.68339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.16698,"mean_force":0.72083,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50571,0.08543,0.05179]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47492,-0.0166,0.02857],"force_p95":10.04676,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.31862,"mean_force":2.30119,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49077,0.09484,0.04639]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.52501,-0.09098,0.02463],"force_p95":8.72221,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.82086,"mean_force":3.93939,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49553,0.08416,0.05181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":516.0,"contact_point_centroid":[0.49412,0.07992,0.00937],"force_p95":0.59437,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.57132,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48336,0.16285,0.19898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49738,-0.10129,0.03972],"force_p95":3.72488,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.73602,"mean_force":1.3694,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48688,0.09298,0.03899]}],"total_contact_groups":20},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49307,-0.06969,0.02418],"final_tcp_position":[0.51216,0.04084,0.145],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":1402.08006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":690.0,"object_pos_end":[0.49383,0.07994,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54348,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":551.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.46925,0.12906,0.10881],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":530.0,"n_steps_budget":600.0,"object_pos_end":[0.49385,0.07995,0.03377],"object_pos_start":[0.49383,0.07994,0.03377],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.0338,"peak_contact_force":395.1016,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":718.0,"raw_peak_contact_force":459.64813,"subtask_id":"reach_peg","tcp_end":[0.48511,0.1137,0.058],"tcp_start":[0.46925,0.12906,0.10881],"tcp_to_object_dist_end":0.04246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2902.0,"n_steps_budget":1000.0,"object_pos_end":[0.50563,-0.06966,0.02413],"object_pos_start":[0.49385,0.07995,0.03377],"object_to_goal_dist_end":0.01976,"object_to_goal_dist_start":0.16019,"object_z_max":0.04907,"peak_contact_force":648.27528,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8979.0,"raw_peak_contact_force":1402.08006,"subtask_id":"push_to_goal","tcp_end":[0.51346,0.08595,0.05357],"tcp_start":[0.51389,0.09424,0.05975],"tcp_to_object_dist_end":0.15857,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":619.0,"n_steps_budget":720.0,"object_pos_end":[0.49307,-0.06969,0.02418],"object_pos_start":[0.4965,-0.06967,0.02413],"object_to_goal_dist_end":0.02011,"object_to_goal_dist_start":0.01926,"object_z_max":0.02423,"peak_contact_force":0.52721,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":798.0,"raw_peak_contact_force":985.7392,"tcp_end":[0.51216,0.04084,0.145],"tcp_start":[0.51346,0.08595,0.05357],"tcp_to_object_dist_end":0.16485,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```