## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

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

## Current Skill (Q=0.623) — your mutation base

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

- **Composite score**: 0.623
- **task_score** (E): 0.305
- **fitness_score**: 0.550  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2637 |
| side_contact | 1.00 | 1.00 | 0.0001 |
| push_1 | 1.00 | 1.00 | 0.0754 |
| retract_1 | 1.00 | 1.00 | 0.1010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.148, 0.044) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.548 | 4.034 |
| side_contact | contact | 1.00 / force_exceeded | (0.506, 0.132, 0.035)→(0.506, 0.132, 0.035) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 46.109 | 68.025 |
| push_1 | push | 1.00 / time_limit | (0.510, 0.008, 0.032)→(0.507, -0.066, 0.033) | (0.502, 0.067, 0.034)→(0.498, -0.060, 0.036) | 0.147→0.024 | 1.00 / 4.000 | 162.060 | 411.979 |
| retract_1 | retract | 1.00 / step_budget | (0.507, -0.066, 0.033)→(0.504, -0.111, 0.124) | (0.492, -0.078, 0.035)→(0.500, -0.076, 0.028) | 0.014→0.014 | 1.00 / 1.000 | 0.576 | 125.420 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.860
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.320
- phase_score: 0.783
- phase_breakdown.reach_peg_score: 0.369
- phase_breakdown.push_to_goal_score: 0.960

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.598
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.396
- **Median Q (composite search score)**: 0.614
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14286,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15325,"push_1.push_distance":0.17838,"push_1.push_speed":0.11457,"side_contact.contact_force_threshold":6.90366},"optimized_scores":{"best_composite_score":0.67108,"best_fitness_score":0.59775,"best_task_score":0.32037},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":379.0,"contact_point_centroid":[0.52502,0.09526,0.06],"force_p95":153.63766,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.67705,"mean_force":79.98801,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50992,0.09915,0.03021]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.11997,0.06],"force_p95":82.48162,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.19959,"mean_force":55.65124,"phase_index":1.0,"phase_name":"side_contact","phase_type":"contact","tcp_position_centroid":[0.51683,0.13115,0.03541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.50493,-0.1005,0.05762],"force_p95":41.12196,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.40006,"mean_force":23.69564,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50148,-0.05584,0.06514]},{"body_a":"attachment","body_b":"peg","contact_count":321.0,"contact_point_centroid":[0.50316,-0.06535,0.05999],"force_p95":40.98157,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.31642,"mean_force":22.20466,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50152,-0.05387,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.50497,-0.08028,0.00849],"force_p95":1.25814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.07077,"mean_force":0.67594,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50189,-0.06929,0.07822]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.04984,0.02133],"force_p95":12.77608,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.82088,"mean_force":4.32482,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50155,-0.0732,0.09455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.50578,0.06295,0.00936],"force_p95":0.5587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51174,0.17121,0.16617]},{"body_a":"attachment","body_b":"peg","contact_count":556.0,"contact_point_centroid":[0.50591,0.00716,0.02772],"force_p95":1.86319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.79788,"mean_force":0.84236,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50692,0.01903,0.02708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":846.0,"contact_point_centroid":[0.50404,0.00971,0.00972],"force_p95":2.02854,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.74979,"mean_force":0.95441,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50832,0.05279,0.0286]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,0.19882,0.29563]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":93.0,"contact_point_centroid":[0.52511,0.02647,0.02896],"force_p95":1.44812,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14888,"mean_force":0.47738,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50752,0.05654,0.0275]},{"body_a":"peg","body_b":"channel_base_body","contact_count":113.0,"contact_point_centroid":[0.50599,0.06341,0.00938],"force_p95":0.55116,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55396,"mean_force":0.54659,"phase_index":1.0,"phase_name":"side_contact","phase_type":"contact","tcp_position_centroid":[0.51982,0.13774,0.03825]}],"total_contact_groups":12},"final_pose_error":0.01139,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50487,-0.07464,0.02415],"final_tcp_position":[0.50166,-0.09246,0.11629],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":171.67705,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54416,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":758.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52431,0.1448,0.04323],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.06304,0.03381],"object_pos_start":[0.50595,0.06302,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":58.01995,"phase_name":"side_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":116.0,"raw_peak_contact_force":85.19959,"subtask_id":"reach_peg","tcp_end":[0.51671,0.13107,0.0353],"tcp_start":[0.51676,0.13108,0.03536],"tcp_to_object_dist_end":0.06889,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50217,-0.0773,0.03542],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.00575,"object_to_goal_dist_start":0.14326,"object_z_max":0.03555,"peak_contact_force":0.68198,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1874.0,"raw_peak_contact_force":171.67705,"subtask_id":"push_to_goal","tcp_end":[0.50499,-0.04776,0.0258],"tcp_start":[0.51671,0.13107,0.0353],"tcp_to_object_dist_end":0.03119,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50487,-0.07464,0.02415],"object_pos_start":[0.50217,-0.0773,0.03542],"object_to_goal_dist_end":0.01743,"object_to_goal_dist_start":0.00575,"object_z_max":0.06014,"peak_contact_force":0.56822,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":957.0,"raw_peak_contact_force":42.40006,"tcp_end":[0.50166,-0.09246,0.11629],"tcp_start":[0.50499,-0.04776,0.0258],"tcp_to_object_dist_end":0.0939,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97436,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07676,"push_1.push_distance":0.12351,"push_1.push_speed":0.13172,"side_contact.contact_force_threshold":3.81337},"optimized_scores":{"best_composite_score":0.61394,"best_fitness_score":0.5406,"best_task_score":0.19973},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":833.0,"contact_point_centroid":[0.55319,-0.10012,0.06494],"force_p95":410.74288,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":544.07069,"mean_force":237.88708,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50751,-0.07289,0.0287]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1165.0,"contact_point_centroid":[0.52536,-0.00277,0.05999],"force_p95":463.15489,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":521.32876,"mean_force":246.8856,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51178,0.00167,0.03151]},{"body_a":"attachment","body_b":"peg","contact_count":288.0,"contact_point_centroid":[0.50066,-0.08328,0.06264],"force_p95":149.57685,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.98965,"mean_force":73.93346,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51093,-0.08382,0.06048]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":321.0,"contact_point_centroid":[0.4726,-0.08232,0.05566],"force_p95":149.33243,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":186.25702,"mean_force":66.35933,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5105,-0.08503,0.06327]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.52502,-0.08124,0.06],"force_p95":113.67661,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.97711,"mean_force":68.69472,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51106,-0.07996,0.04877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":876.0,"contact_point_centroid":[0.48731,-0.10362,0.02912],"force_p95":172.81692,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.33113,"mean_force":82.95954,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50752,-0.07266,0.02848]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":815.0,"contact_point_centroid":[0.47123,-0.08927,0.03015],"force_p95":164.12245,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":174.46691,"mean_force":106.00198,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50796,-0.07548,0.02901]},{"body_a":"attachment","body_b":"peg","contact_count":1215.0,"contact_point_centroid":[0.50082,-0.06253,0.03049],"force_p95":145.52745,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.79876,"mean_force":81.11476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50731,-0.05514,0.028]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.56936,-0.12,0.0649],"force_p95":83.38631,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.58087,"mean_force":42.65328,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50811,-0.07825,0.031]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52883,0.11993,0.06],"force_p95":57.72448,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.06885,"mean_force":41.28187,"phase_index":1.0,"phase_name":"side_contact","phase_type":"contact","tcp_position_centroid":[0.52556,0.13197,0.03756]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54005,-0.03937,0.06],"force_p95":53.76297,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.76297,"mean_force":53.76297,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50417,-0.04577,0.02494]},{"body_a":"peg","body_b":"link7","contact_count":240.0,"contact_point_centroid":[0.50349,-0.09109,0.06949],"force_p95":40.8236,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.46339,"mean_force":22.63922,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50812,-0.07095,0.02873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.486,-0.10015,0.05921],"force_p95":24.81073,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.06666,"mean_force":6.56744,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51028,-0.08804,0.07131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":780.0,"contact_point_centroid":[0.50175,0.01166,0.00952],"force_p95":2.35006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.21973,"mean_force":0.88223,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51289,0.06488,0.03158]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":47.0,"contact_point_centroid":[0.52515,0.02261,0.03275],"force_p95":2.45815,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.11351,"mean_force":0.81121,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50726,0.05463,0.02667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":824.0,"contact_point_centroid":[0.50593,0.05663,0.00936],"force_p95":0.61178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56587,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51492,0.16817,0.1663]}],"total_contact_groups":20},"final_pose_error":0.01156,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50273,-0.07794,0.03456],"final_tcp_position":[0.50492,-0.12273,0.12134],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":544.07069,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05665,0.03381],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54432,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":861.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.5308,0.13874,0.04274],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":54.0,"n_steps_budget":600.0,"object_pos_end":[0.50606,0.05663,0.03382],"object_pos_start":[0.50617,0.05665,0.03381],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13693,"object_z_max":0.03382,"peak_contact_force":36.6252,"phase_name":"side_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":57.0,"raw_peak_contact_force":60.06885,"subtask_id":"reach_peg","tcp_end":[0.5254,0.13186,0.03741],"tcp_start":[0.52547,0.13188,0.03749],"tcp_to_object_dist_end":0.07775,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1844.0,"n_steps_budget":960.0,"object_pos_end":[0.49814,-0.08321,0.03564],"object_pos_start":[0.50611,0.05668,0.03382],"object_to_goal_dist_end":0.00573,"object_to_goal_dist_start":0.13695,"object_z_max":0.04649,"peak_contact_force":32.21248,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5972.0,"raw_peak_contact_force":544.07069,"subtask_id":"push_to_goal","tcp_end":[0.50815,-0.07831,0.03093],"tcp_start":[0.5046,-0.05461,0.02574],"tcp_to_object_dist_end":0.01209,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":568.0,"n_steps_budget":720.0,"object_pos_end":[0.50273,-0.07794,0.03456],"object_pos_start":[0.48144,-0.08177,0.04419],"object_to_goal_dist_end":0.00642,"object_to_goal_dist_start":0.0191,"object_z_max":0.07305,"peak_contact_force":0.55782,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1141.0,"raw_peak_contact_force":186.98965,"tcp_end":[0.50492,-0.12273,0.12134],"tcp_start":[0.50815,-0.07831,0.03093],"tcp_to_object_dist_end":0.09768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21477,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14226,"push_1.push_distance":0.15727,"push_1.push_speed":0.13981,"side_contact.contact_force_threshold":9.31121},"optimized_scores":{"best_composite_score":0.58433,"best_fitness_score":0.51099,"best_task_score":0.39618},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":1114.0,"contact_point_centroid":[0.57569,-0.11423,0.06495],"force_p95":468.08301,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.18866,"mean_force":265.77095,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50565,-0.06014,0.03692]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1034.0,"contact_point_centroid":[0.52504,-0.06778,0.05999],"force_p95":306.99203,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":431.71662,"mean_force":224.82242,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50846,-0.06293,0.03851]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":874.0,"contact_point_centroid":[0.47499,0.11995,0.05351],"force_p95":241.24158,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":246.54894,"mean_force":192.22078,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47406,0.13315,0.0353]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2618.0,"contact_point_centroid":[0.49375,-0.02538,0.00909],"force_p95":51.86869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":220.96656,"mean_force":16.89998,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49374,0.01218,0.03516]},{"body_a":"attachment","body_b":"peg","contact_count":1578.0,"contact_point_centroid":[0.50125,-0.06401,0.04084],"force_p95":166.3414,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.66647,"mean_force":89.35121,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50516,-0.05486,0.03594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1440.0,"contact_point_centroid":[0.49654,-0.10184,0.03103],"force_p95":163.77195,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.28024,"mean_force":76.44364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50556,-0.05767,0.03597]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.58,-0.11998,0.0649],"force_p95":131.84442,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.87078,"mean_force":68.16372,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50866,-0.07226,0.04267]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52502,-0.07791,0.05999],"force_p95":126.02263,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.05272,"mean_force":57.14287,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50866,-0.07226,0.04267]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1043.0,"contact_point_centroid":[0.47463,-0.07482,0.02529],"force_p95":46.54934,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.26703,"mean_force":19.49819,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50829,-0.06216,0.03849]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.11995,0.03294],"force_p95":57.29531,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.80784,"mean_force":45.22049,"phase_index":1.0,"phase_name":"side_contact","phase_type":"contact","tcp_position_centroid":[0.47645,0.13182,0.03277]},{"body_a":"peg","body_b":"link7","contact_count":139.0,"contact_point_centroid":[0.50034,-0.03517,0.06968],"force_p95":40.72891,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.22482,"mean_force":23.72503,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49543,0.00993,0.02945]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50048,-0.08101,0.0426],"force_p95":18.45388,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.54872,"mean_force":5.83145,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50858,-0.07226,0.04293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.49336,-0.07477,0.00813],"force_p95":0.71094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.12124,"mean_force":0.81147,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50573,-0.08883,0.09023]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":29.0,"contact_point_centroid":[0.47486,-0.0741,0.02643],"force_p95":9.09452,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.29909,"mean_force":4.90058,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50789,-0.07312,0.04705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49003,-0.10001,0.02318],"force_p95":5.50553,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.15195,"mean_force":2.30509,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50862,-0.07226,0.04281]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52593,0.04448,0.03153],"force_p95":4.92735,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.01828,"mean_force":4.26828,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49407,0.07311,0.03587]}],"total_contact_groups":19},"final_pose_error":0.011,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49313,-0.07477,0.02413],"final_tcp_position":[0.50576,-0.11676,0.13357],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":520.18866,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55477,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":745.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.46848,0.16092,0.04453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":277.0,"n_steps_budget":600.0,"object_pos_end":[0.4938,0.07993,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16017,"object_z_max":0.03379,"peak_contact_force":43.68258,"phase_name":"side_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":280.0,"raw_peak_contact_force":58.80784,"subtask_id":"reach_peg","tcp_end":[0.47651,0.13174,0.03272],"tcp_start":[0.47649,0.13176,0.03274],"tcp_to_object_dist_end":0.05463,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":2697.0,"n_steps_budget":960.0,"object_pos_end":[0.49506,-0.01863,0.03834],"object_pos_start":[0.4938,0.07996,0.03378],"object_to_goal_dist_end":0.06159,"object_to_goal_dist_start":0.1602,"object_z_max":0.05016,"peak_contact_force":453.28672,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9847.0,"raw_peak_contact_force":520.18866,"subtask_id":"push_to_goal","tcp_end":[0.50866,-0.07229,0.04262],"tcp_start":[0.50827,-0.05114,0.03622],"tcp_to_object_dist_end":0.05553,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.49313,-0.07477,0.02413],"object_pos_start":[0.49266,-0.075,0.02661],"object_to_goal_dist_end":0.01807,"object_to_goal_dist_start":0.01607,"object_z_max":0.02677,"peak_contact_force":0.60162,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":683.0,"raw_peak_contact_force":146.87078,"tcp_end":[0.50576,-0.11676,0.13357],"tcp_start":[0.50866,-0.07229,0.04262],"tcp_to_object_dist_end":0.1179,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```