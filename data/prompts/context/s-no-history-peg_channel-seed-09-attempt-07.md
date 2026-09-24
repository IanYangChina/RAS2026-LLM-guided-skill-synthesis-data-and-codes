## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

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

## Current Skill (Q=0.509) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.08
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
    entity: peg
    offset:
    - 0.0
    - 0.08
    - 0.1
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
- id: descend_1
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
    - 0.0
    - -0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descent_force_threshold:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_guard
    when: after_phase
    predicate: force_below
    threshold: 15.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - -0.01
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
    - 0.0
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
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.08, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, -0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=after_phase, predicate=force_below, on_failure=retry, threshold=15.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, -0.01]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, -0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.509
- **task_score** (E): 0.228
- **fitness_score**: 0.435  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1629 |
| descend_1 | 1.00 | 1.00 | 0.0412 |
| push_1 | 1.00 | 1.00 | 0.1523 |
| retract_1 | 1.00 | 1.00 | 0.1010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.150, 0.148) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.548 | 4.034 |
| descend_1 | contact | 1.00 / force_exceeded | (0.507, 0.113, 0.086)→(0.499, 0.092, 0.051) | (0.502, 0.067, 0.034)→(0.502, 0.064, 0.036) | 0.147→0.145 | 1.00 / 2.000 | 24.831 | 37.514 |
| push_1 | push | 1.00 / time_limit | (0.499, 0.092, 0.051)→(0.502, -0.059, 0.036) | (0.502, 0.064, 0.036)→(0.495, -0.052, 0.031) | 0.144→0.035 | 1.00 / 2.333 | 28.165 | 129.174 |
| retract_1 | retract | 1.00 / step_budget | (0.502, -0.059, 0.036)→(0.499, -0.104, 0.126) | (0.495, -0.052, 0.031)→(0.504, -0.043, 0.024) | 0.035→0.045 | 1.00 / 1.000 | 0.684 | 49.827 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.857
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.342
- phase_score: 0.641
- phase_breakdown.reach_peg_score: 0.110
- phase_breakdown.push_to_goal_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.522
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.342
- **Median Q (composite search score)**: 0.560
- **K-run variance**: 0.0096
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95495,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14849,"descend_1.descent_force_threshold":9.22904,"push_1.push_distance":0.1539,"push_1.push_speed":0.11912},"optimized_scores":{"best_composite_score":0.59497,"best_fitness_score":0.52163,"best_task_score":0.34248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":912.0,"contact_point_centroid":[0.50053,-0.02071,0.00869],"force_p95":77.50437,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.79145,"mean_force":37.89528,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5047,0.00325,0.04072]},{"body_a":"attachment","body_b":"peg","contact_count":875.0,"contact_point_centroid":[0.50257,-0.00614,0.04152],"force_p95":80.48953,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.51688,"mean_force":38.99327,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5047,0.00448,0.04078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.49937,-0.07525,0.00814],"force_p95":7.10266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.64091,"mean_force":1.53901,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50327,-0.0995,0.08449]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.49596,-0.08937,0.04215],"force_p95":23.98315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.68986,"mean_force":13.50034,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50558,-0.08326,0.04003]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50304,-0.10001,0.065],"force_p95":48.75162,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.60832,"mean_force":36.73294,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50283,-0.08801,0.06382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.47963,-0.10023,0.02295],"force_p95":33.55471,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.76872,"mean_force":23.80772,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50569,-0.06539,0.0378]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":203.0,"contact_point_centroid":[0.47496,-0.04922,0.02237],"force_p95":21.30423,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.46318,"mean_force":15.66809,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50537,-0.05996,0.03785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":562.0,"contact_point_centroid":[0.5058,0.06121,0.00941],"force_p95":0.55275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.71734,"mean_force":0.69424,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.5146,0.11648,0.09565]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50702,0.07831,0.0533],"force_p95":13.46336,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.60293,"mean_force":7.63224,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50801,0.09024,0.05321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.47614,-0.10005,0.02438],"force_p95":13.17188,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.5025,"mean_force":8.59035,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5065,-0.08306,0.03743]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":41.0,"contact_point_centroid":[0.47489,-0.04936,0.02552],"force_p95":9.18906,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.14927,"mean_force":3.64,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50536,-0.08331,0.04079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50563,0.063,0.00935],"force_p95":0.58017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57624,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51181,0.17203,0.21925]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50017,0.19844,0.2959]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52506,0.06029,0.05973],"force_p95":0.75753,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80291,"mean_force":0.27651,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50841,0.09076,0.05424]}],"total_contact_groups":14},"final_pose_error":0.0116,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50628,-0.07418,0.02413],"final_tcp_position":[0.50329,-0.12745,0.12771],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":100.79145,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":750.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55038,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":490.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52425,0.14669,0.14755],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":562.0,"n_steps_budget":990.0,"object_pos_end":[0.50566,0.06105,0.03572],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.14123,"object_to_goal_dist_start":0.14329,"object_z_max":0.03717,"peak_contact_force":11.14006,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":581.0,"raw_peak_contact_force":16.71734,"subtask_id":"reach_peg","tcp_end":[0.50636,0.08715,0.04759],"tcp_start":[0.50819,0.08974,0.05258],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":912.0,"n_steps_budget":960.0,"object_pos_end":[0.49361,-0.07477,0.02376],"object_pos_start":[0.50533,0.05867,0.03717],"object_to_goal_dist_end":0.01822,"object_to_goal_dist_start":0.1388,"object_z_max":0.04031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2164.0,"raw_peak_contact_force":100.79145,"subtask_id":"push_to_goal","tcp_end":[0.50655,-0.08294,0.03741],"tcp_start":[0.50636,0.08715,0.04759],"tcp_to_object_dist_end":0.0205,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50628,-0.07418,0.02413],"object_pos_start":[0.49361,-0.07477,0.02376],"object_to_goal_dist_end":0.01803,"object_to_goal_dist_start":0.01822,"object_z_max":0.02672,"peak_contact_force":0.60162,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":729.0,"raw_peak_contact_force":74.64091,"tcp_end":[0.50329,-0.12745,0.12771],"tcp_start":[0.50655,-0.08294,0.03741],"tcp_to_object_dist_end":0.11652,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07692,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29608,"descend_1.descent_force_threshold":11.80871,"push_1.push_distance":0.1074,"push_1.push_speed":0.14233},"optimized_scores":{"best_composite_score":0.55997,"best_fitness_score":0.48664,"best_task_score":0.22876},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":595.0,"contact_point_centroid":[0.50439,0.01165,0.04172],"force_p95":76.34796,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.30957,"mean_force":37.7661,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5067,0.02272,0.04095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":595.0,"contact_point_centroid":[0.50029,-0.00841,0.00968],"force_p95":74.20068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.35681,"mean_force":37.44537,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5067,0.02272,0.04095]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.49783,-0.04958,0.04371],"force_p95":24.36083,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.91379,"mean_force":7.24689,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50764,-0.04321,0.0415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":629.0,"contact_point_centroid":[0.50384,-0.07205,0.00823],"force_p95":0.90239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.14745,"mean_force":1.00418,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50536,-0.05971,0.08652]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.48787,-0.10035,0.01525],"force_p95":34.40598,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.91371,"mean_force":30.50348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50849,-0.04068,0.03907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":58.0,"contact_point_centroid":[0.48235,-0.10024,0.0185],"force_p95":14.43029,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.9285,"mean_force":3.82422,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50718,-0.04343,0.04314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":550.0,"contact_point_centroid":[0.50573,0.05505,0.00941],"force_p95":0.55676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.59483,"mean_force":0.72381,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51887,0.11051,0.09543]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50844,0.07157,0.05233],"force_p95":13.28864,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.41144,"mean_force":8.71111,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51036,0.08336,0.0521]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52506,-0.09821,0.02431],"force_p95":9.12685,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35689,"mean_force":2.66695,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50495,-0.04914,0.06828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.50575,0.05662,0.00935],"force_p95":0.61353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.5825,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51527,0.16866,0.21821]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50047,0.19797,0.29482]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47499,-0.05004,0.02801],"force_p95":0.3637,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36769,"mean_force":0.30126,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5066,-0.04359,0.04463]}],"total_contact_groups":12},"final_pose_error":0.01138,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50602,-0.07413,0.02409],"final_tcp_position":[0.50538,-0.08745,0.12951],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":86.30957,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55132,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":479.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.53064,0.14064,0.14683],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":550.0,"n_steps_budget":990.0,"object_pos_end":[0.50584,0.05246,0.03701],"object_pos_start":[0.50615,0.05663,0.03378],"object_to_goal_dist_end":0.13262,"object_to_goal_dist_start":0.13691,"object_z_max":0.037,"peak_contact_force":13.59483,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":562.0,"raw_peak_contact_force":13.59483,"subtask_id":"reach_peg","tcp_end":[0.50957,0.08066,0.04773],"tcp_start":[0.53064,0.14064,0.14683],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":595.0,"n_steps_budget":630.0,"object_pos_end":[0.49577,-0.07468,0.02776],"object_pos_start":[0.50584,0.05246,0.03701],"object_to_goal_dist_end":0.014,"object_to_goal_dist_start":0.13262,"object_z_max":0.04029,"peak_contact_force":84.00551,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1212.0,"raw_peak_contact_force":86.30957,"subtask_id":"push_to_goal","tcp_end":[0.50864,-0.04269,0.03907],"tcp_start":[0.50957,0.08066,0.04773],"tcp_to_object_dist_end":0.03629,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50602,-0.07413,0.02409],"object_pos_start":[0.49577,-0.07468,0.02776],"object_to_goal_dist_end":0.01799,"object_to_goal_dist_start":0.014,"object_z_max":0.02898,"peak_contact_force":0.72551,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":741.0,"raw_peak_contact_force":67.91379,"tcp_end":[0.50538,-0.08745,0.12951],"tcp_start":[0.50864,-0.04269,0.03907],"tcp_to_object_dist_end":0.10625,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00952,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.20318,"descend_1.descent_force_threshold":7.17618,"push_1.push_distance":0.13751,"push_1.push_speed":0.10185},"optimized_scores":{"best_composite_score":0.37131,"best_fitness_score":0.29798,"best_task_score":0.11299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":431.0,"contact_point_centroid":[0.47499,0.0739,0.05541],"force_p95":187.24399,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.42159,"mean_force":106.76064,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48551,0.07729,0.05392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":982.0,"contact_point_centroid":[0.49868,0.02475,0.00901],"force_p95":92.32269,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.05457,"mean_force":30.42611,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48849,0.0341,0.04741]},{"body_a":"attachment","body_b":"peg","contact_count":481.0,"contact_point_centroid":[0.4988,0.00879,0.04356],"force_p95":94.8127,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.59775,"mean_force":60.6646,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49082,0.00507,0.0435]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.0996,0.05992],"force_p95":81.95349,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.23093,"mean_force":70.48213,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48169,0.10932,0.05889]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":39.0,"contact_point_centroid":[0.47499,0.01852,0.05046],"force_p95":15.13342,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.37964,"mean_force":10.4598,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49398,-0.03904,0.03754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":627.0,"contact_point_centroid":[0.50036,0.0136,0.00847],"force_p95":0.73,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.92741,"mean_force":0.59971,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48746,-0.0682,0.07911]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,-0.00292,0.02434],"force_p95":5.19389,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.76547,"mean_force":1.44967,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48717,-0.06332,0.076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.49424,0.07992,0.00936],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.57922,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48389,0.18016,0.22005]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49876,0.19853,0.2951]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47499,0.00875,0.05795],"force_p95":0.36727,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82169,"mean_force":0.08069,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48906,-0.05204,0.03504]},{"body_a":"peg","body_b":"channel_base_body","contact_count":627.0,"contact_point_centroid":[0.49382,0.07997,0.00938],"force_p95":0.56393,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58631,"mean_force":0.54662,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.47471,0.13543,0.10216]}],"total_contact_groups":11},"final_pose_error":0.01117,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49953,0.01917,0.02409],"final_tcp_position":[0.48751,-0.09591,0.1222],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":200.42159,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":419.0,"n_steps_budget":600.0,"object_pos_end":[0.49382,0.07993,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54338,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":426.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47024,0.16256,0.14964],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07996,0.03377],"object_pos_start":[0.49382,0.07993,0.03377],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":49.75893,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":630.0,"raw_peak_contact_force":82.23093,"subtask_id":"reach_peg","tcp_end":[0.48175,0.10918,0.05879],"tcp_start":[0.48172,0.10924,0.05882],"tcp_to_object_dist_end":0.04032,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,-0.00637,0.04074],"object_pos_start":[0.49383,0.07993,0.03377],"object_to_goal_dist_end":0.07374,"object_to_goal_dist_start":0.16017,"object_z_max":0.04074,"peak_contact_force":0.4891,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1933.0,"raw_peak_contact_force":200.42159,"subtask_id":"push_to_goal","tcp_end":[0.49073,-0.05122,0.03148],"tcp_start":[0.48175,0.10918,0.05879],"tcp_to_object_dist_end":0.0461,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":635.0,"n_steps_budget":720.0,"object_pos_end":[0.49953,0.01917,0.02409],"object_pos_start":[0.49599,-0.00637,0.04074],"object_to_goal_dist_end":0.10044,"object_to_goal_dist_start":0.07374,"object_z_max":0.04075,"peak_contact_force":0.72553,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":654.0,"raw_peak_contact_force":6.92741,"tcp_end":[0.48751,-0.09591,0.1222],"tcp_start":[0.49073,-0.05122,0.03148],"tcp_to_object_dist_end":0.1517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```