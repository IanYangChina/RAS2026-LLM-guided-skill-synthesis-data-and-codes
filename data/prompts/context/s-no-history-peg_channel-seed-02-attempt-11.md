## Search State

- **Seed**: 2
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=-0.272) — your mutation base

```yaml
skill: peg_channel_new
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.02
  weight: 0.3
- id: push_complete
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.05
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_contact
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    descend_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: add
    pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_contact
- id: contact_peg
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
    - 0.01
    - 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    contact_offset_y:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.y
        mode: add
    contact_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: add
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_contact
- id: push_phase
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
    - -0.026
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
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
    retry_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: add
    retry_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: add
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_complete
- id: retract_tcp
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
    - 0.05
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (add)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - descend_offset_z: status=consumed; consumers=target.offset.z (add)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.01, 0.005]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (add)
    - contact_offset_y: status=consumed; consumers=target.offset.y (add)
    - contact_offset_z: status=consumed; consumers=target.offset.z (add)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_phase** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.026], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract_tcp** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.272
- **task_score** (E): 0.277
- **fitness_score**: 0.552  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.990

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0252 |
| descend_to_peg | 1.00 | 1.00 | 0.1692 |
| contact_peg | 0.67 | 1.00 | 0.1040 |
| push_phase | 0.67 | 1.00 | 0.1236 |
| retract_tcp | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.189, 0.281) | (0.494, 0.068, 0.040)→(0.499, 0.068, 0.033) | 0.151→0.148 | 1.00 / 1.333 | 1.306 | 3.659 |
| descend_to_peg | descend | 1.00 / step_budget | (0.493, 0.189, 0.281)→(0.502, 0.177, 0.113) | (0.499, 0.068, 0.033)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 1.139 |
| contact_peg | contact | 0.67 / force_exceeded | (0.502, 0.177, 0.113)→(0.504, 0.096, 0.048) | (0.498, 0.068, 0.034)→(0.498, 0.067, 0.034) | 0.148→0.147 | 1.00 / 1.667 | 6.739 | 9.523 |
| push_phase | push | 0.67 / time_limit | (0.504, 0.096, 0.048)→(0.500, -0.026, 0.027) | (0.498, 0.067, 0.034)→(0.503, -0.055, 0.035) | 0.147→0.026 | 1.00 / 2.000 | 10.972 | 26.233 |
| retract_tcp | retract | 1.00 / step_budget | (0.498, -0.022, 0.027)→(0.495, -0.022, 0.068) | (0.507, -0.052, 0.036)→(0.507, -0.052, 0.034) | 0.030→0.030 | 1.00 / 1.500 | 1.391 | 1.674 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.781
- alignment_error: None
- force_efficiency: 0.404
- terminal_score: 0.241
- phase_score: 0.695
- phase_breakdown.push_complete_score: 0.768
- phase_breakdown.reach_contact_score: 0.526

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.649
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.460
- **Median Q (composite search score)**: -0.248
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: contact_peg.contact_offset_y
- **Final σ (mean)**: 0.279


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7377,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":-0.00867,"approach_peg.approach_offset_y":0.07404,"approach_peg.approach_offset_z":0.11665,"approach_peg.pose_tolerance":0.03227,"contact_peg.approach_offset_x":0.01514,"contact_peg.contact_offset_y":0.01161,"contact_peg.contact_offset_z":0.00968,"contact_peg.force_threshold":7.77101,"descend_to_peg.approach_offset_x":0.01533,"descend_to_peg.approach_offset_y":0.06445,"descend_to_peg.descend_offset_z":0.02748,"descend_to_peg.pose_tolerance":0.03544,"push_phase.force_limit_guard":30.0714,"push_phase.max_time":14.35194,"push_phase.push_distance":0.18058,"push_phase.push_speed":0.07735,"push_phase.retry_offset_x":0.00035,"push_phase.retry_offset_y":0.00666},"optimized_scores":{"best_composite_score":-0.34138,"best_fitness_score":0.64862,"best_task_score":0.46029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53812,-0.02533,0.05999],"force_p95":31.01636,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.35193,"mean_force":26.67634,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50205,-0.03178,0.02512]},{"body_a":"attachment","body_b":"peg","contact_count":697.0,"contact_point_centroid":[0.49918,0.0147,0.03421],"force_p95":8.08081,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.42319,"mean_force":2.01353,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50231,0.02618,0.03374]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":489.0,"contact_point_centroid":[0.47489,0.02489,0.02972],"force_p95":4.79362,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.64858,"mean_force":1.12899,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50249,0.05312,0.03779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":791.0,"contact_point_centroid":[0.4947,-0.01237,0.00989],"force_p95":7.25577,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.41829,"mean_force":1.93822,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50231,0.02377,0.03339]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.49518,0.06351,0.0094],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.77322,"mean_force":0.57006,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50396,0.1355,0.07891]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.5017,0.0805,0.04905],"force_p95":7.45132,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.13599,"mean_force":2.31386,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50596,0.09156,0.04844]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.50867,0.06395,0.00913],"force_p95":2.29527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":1.46669,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49158,0.19614,0.2857]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49735,0.19857,0.29581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.49523,0.06412,0.00934],"force_p95":0.61146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76766,"mean_force":0.5462,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49696,0.18832,0.20065]}],"total_contact_groups":9},"final_pose_error":0.05883,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49657,-0.06147,0.03471],"final_tcp_position":[0.5021,-0.03202,0.02513],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":31.35193,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.49543,0.06388,0.03306],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.86338,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.48972,0.19536,0.28249],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.06376,0.0339],"object_pos_start":[0.49543,0.06388,0.03306],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14412,"object_z_max":0.03389,"peak_contact_force":0.55029,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":207.0,"raw_peak_contact_force":0.76766,"subtask_id":"reach_contact","tcp_end":[0.50515,0.18091,0.11482],"tcp_start":[0.48972,0.19536,0.28249],"tcp_to_object_dist_end":0.14274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.49455,0.06256,0.03463],"object_pos_start":[0.49498,0.06376,0.0339],"object_to_goal_dist_end":0.14277,"object_to_goal_dist_start":0.14398,"object_z_max":0.03459,"peak_contact_force":0.42078,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":700.0,"raw_peak_contact_force":8.77322,"subtask_id":"reach_contact","tcp_end":[0.50602,0.08998,0.04737],"tcp_start":[0.50515,0.18091,0.11482],"tcp_to_object_dist_end":0.03233,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.49657,-0.06147,0.03471],"object_pos_start":[0.49455,0.06256,0.03463],"object_to_goal_dist_end":0.01957,"object_to_goal_dist_start":0.14277,"object_z_max":0.03611,"peak_contact_force":31.35193,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1982.0,"raw_peak_contact_force":31.35193,"subtask_id":"push_complete","tcp_end":[0.5021,-0.03202,0.02513],"tcp_start":[0.50602,0.08998,0.04737],"tcp_to_object_dist_end":0.03146,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74648,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00157,"approach_peg.approach_offset_y":0.04215,"approach_peg.approach_offset_z":0.12289,"approach_peg.pose_tolerance":0.03414,"contact_peg.approach_offset_x":0.01094,"contact_peg.contact_offset_y":0.01184,"contact_peg.contact_offset_z":0.00542,"contact_peg.force_threshold":7.7451,"descend_to_peg.approach_offset_x":-0.00017,"descend_to_peg.approach_offset_y":0.06053,"descend_to_peg.descend_offset_z":0.02737,"descend_to_peg.pose_tolerance":0.04191,"push_phase.force_limit_guard":27.59889,"push_phase.max_time":8.92842,"push_phase.push_distance":0.19993,"push_phase.push_speed":0.07323,"push_phase.retry_offset_x":-0.00615,"push_phase.retry_offset_y":-0.00593},"optimized_scores":{"best_composite_score":-0.2478,"best_fitness_score":0.4922,"best_task_score":0.12848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":761.0,"contact_point_centroid":[0.49865,-0.01273,0.00991],"force_p95":7.73725,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.55577,"mean_force":3.1559,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49656,0.03003,0.03405]},{"body_a":"attachment","body_b":"peg","contact_count":713.0,"contact_point_centroid":[0.49886,0.01088,0.04209],"force_p95":7.52348,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.31232,"mean_force":3.03488,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49651,0.02271,0.03303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":672.0,"contact_point_centroid":[0.49415,0.05892,0.00939],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.79444,"mean_force":0.5689,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49389,0.12906,0.08192]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.49769,0.07649,0.04685],"force_p95":11.49634,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.32943,"mean_force":3.96303,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50008,0.08821,0.04651]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":102.0,"contact_point_centroid":[0.47484,0.04922,0.0288],"force_p95":4.61475,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.54542,"mean_force":1.07141,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49769,0.07872,0.04163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":126.0,"contact_point_centroid":[0.52507,-0.04916,0.02751],"force_p95":3.76883,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.64247,"mean_force":1.57957,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49635,-0.02104,0.02717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.49885,0.05862,0.0089],"force_p95":3.38912,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":1.20457,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48831,0.18263,0.28459]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49589,0.19419,0.2949]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52502,-0.05959,0.05851],"force_p95":1.54604,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64944,"mean_force":0.48751,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49344,-0.03091,0.03821]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.50189,-0.04256,0.05981],"force_p95":1.42142,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.61325,"mean_force":0.4256,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4937,-0.03096,0.0322]},{"body_a":"peg","body_b":"channel_base_body","contact_count":398.0,"contact_point_centroid":[0.50719,-0.06418,0.00958],"force_p95":0.57327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71322,"mean_force":0.50536,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49299,-0.03084,0.04621]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.49415,0.05888,0.00934],"force_p95":0.57351,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64567,"mean_force":0.54302,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48748,0.17313,0.20368]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5068,-0.05907,0.03382],"final_tcp_position":[0.49271,-0.03078,0.06659],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":17.55577,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":52.0,"n_steps_budget":600.0,"object_pos_end":[0.49424,0.05897,0.03301],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.63279,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":58.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.48414,0.17613,0.2791],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.49418,0.05891,0.03382],"object_pos_start":[0.49424,0.05897,0.03301],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.13927,"object_z_max":0.03382,"peak_contact_force":0.53905,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":169.0,"raw_peak_contact_force":0.64567,"subtask_id":"reach_contact","tcp_end":[0.491,0.17042,0.12207],"tcp_start":[0.48414,0.17613,0.2791],"tcp_to_object_dist_end":0.14224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":672.0,"n_steps_budget":750.0,"object_pos_end":[0.4941,0.05844,0.03381],"object_pos_start":[0.49418,0.05891,0.03382],"object_to_goal_dist_end":0.1387,"object_to_goal_dist_start":0.13917,"object_z_max":0.03391,"peak_contact_force":13.79444,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":676.0,"raw_peak_contact_force":13.79444,"subtask_id":"reach_contact","tcp_end":[0.50021,0.08745,0.04584],"tcp_start":[0.491,0.17042,0.12207],"tcp_to_object_dist_end":0.03199,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.05964,0.03594],"object_pos_start":[0.4941,0.05844,0.03381],"object_to_goal_dist_end":0.0219,"object_to_goal_dist_start":0.1387,"object_z_max":0.036,"peak_contact_force":1.42753,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1702.0,"raw_peak_contact_force":17.55577,"subtask_id":"push_complete","tcp_end":[0.49635,-0.03097,0.02586],"tcp_start":[0.50021,0.08745,0.04584],"tcp_to_object_dist_end":0.0322,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":600.0,"object_pos_end":[0.5068,-0.05907,0.03382],"object_pos_start":[0.50698,-0.05964,0.03594],"object_to_goal_dist_end":0.02286,"object_to_goal_dist_start":0.0219,"object_z_max":0.03594,"peak_contact_force":0.55135,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":515.0,"raw_peak_contact_force":1.64944,"tcp_end":[0.49271,-0.03078,0.06659],"tcp_start":[0.49635,-0.03097,0.02586],"tcp_to_object_dist_end":0.04553,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6087,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":-0.01613,"approach_peg.approach_offset_y":0.05475,"approach_peg.approach_offset_z":0.11261,"approach_peg.pose_tolerance":0.03466,"contact_peg.approach_offset_x":0.00199,"contact_peg.contact_offset_y":0.005,"contact_peg.contact_offset_z":0.00809,"contact_peg.force_threshold":4.02859,"descend_to_peg.approach_offset_x":0.00467,"descend_to_peg.approach_offset_y":0.04777,"descend_to_peg.descend_offset_z":0.02615,"descend_to_peg.pose_tolerance":0.02356,"push_phase.force_limit_guard":38.29689,"push_phase.max_time":11.56159,"push_phase.push_distance":0.17268,"push_phase.push_speed":0.077,"push_phase.retry_offset_x":0.00304,"push_phase.retry_offset_y":-0.0028},"optimized_scores":{"best_composite_score":-0.22628,"best_fitness_score":0.51372,"best_task_score":0.24129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":861.0,"contact_point_centroid":[0.50389,0.04082,0.04072],"force_p95":25.56338,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.79158,"mean_force":12.58293,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50096,0.05227,0.03918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":841.0,"contact_point_centroid":[0.50682,0.01723,0.00985],"force_p95":22.18981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.06918,"mean_force":11.86842,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50104,0.05592,0.03983]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":494.0,"contact_point_centroid":[0.52503,0.03017,0.02768],"force_p95":9.93979,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.26311,"mean_force":5.60785,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50098,0.05526,0.03966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.50595,0.08078,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.00149,"mean_force":0.55934,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50496,0.14508,0.07494]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50558,0.09873,0.0588],"force_p95":5.30205,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.5125,"mean_force":3.40798,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50433,0.11067,0.05218]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49815,0.08213,0.00931],"force_p95":4.17894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":2.829,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5054,0.19588,0.28478]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53283,0.0809,0.02746],"force_p95":1.27982,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.53073,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50216,0.19822,0.29384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":297.0,"contact_point_centroid":[0.50566,0.0809,0.00934],"force_p95":0.56156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00389,"mean_force":0.55972,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50698,0.18745,0.19239]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.50665,-0.04576,0.00946],"force_p95":0.56153,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69919,"mean_force":0.54413,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49712,-0.01397,0.04905]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":61.0,"contact_point_centroid":[0.52501,-0.04404,0.05728],"force_p95":0.19242,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97601,"mean_force":0.04319,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49708,-0.01396,0.05517]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.5049,-0.02623,0.0583],"force_p95":0.37086,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.82531,"mean_force":0.22097,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49893,-0.01423,0.03057]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.5252,0.08088,0.01],"force_p95":0.40223,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40652,"mean_force":0.36356,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50619,0.19519,0.28228]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,-0.04404,0.0338],"final_tcp_position":[0.49684,-0.0139,0.06943],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":29.79158,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50724,0.08087,0.03298],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16119,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":2.42137,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.50614,0.19527,0.28263],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.50724,0.08087,0.03298],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16119,"object_z_max":0.03378,"peak_contact_force":0.5462,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":299.0,"raw_peak_contact_force":2.00389,"subtask_id":"reach_contact","tcp_end":[0.50861,0.17997,0.10206],"tcp_start":[0.50614,0.19527,0.28263],"tcp_to_object_dist_end":0.12039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":660.0,"object_pos_end":[0.506,0.08073,0.03386],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16096,"object_to_goal_dist_start":0.16109,"object_z_max":0.03379,"peak_contact_force":6.00149,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":521.0,"raw_peak_contact_force":6.00149,"subtask_id":"reach_contact","tcp_end":[0.50433,0.11046,0.05204],"tcp_start":[0.50861,0.17997,0.10206],"tcp_to_object_dist_end":0.03489,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50672,-0.04353,0.03554],"object_pos_start":[0.506,0.08073,0.03386],"object_to_goal_dist_end":0.03735,"object_to_goal_dist_start":0.16096,"object_z_max":0.04068,"peak_contact_force":0.1352,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2196.0,"raw_peak_contact_force":29.79158,"subtask_id":"push_complete","tcp_end":[0.50047,-0.01398,0.02869],"tcp_start":[0.50433,0.11046,0.05204],"tcp_to_object_dist_end":0.03097,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":403.0,"n_steps_budget":600.0,"object_pos_end":[0.50696,-0.04404,0.0338],"object_pos_start":[0.50672,-0.04353,0.03554],"object_to_goal_dist_end":0.03715,"object_to_goal_dist_start":0.03735,"object_z_max":0.03554,"peak_contact_force":2.2303,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":484.0,"raw_peak_contact_force":1.69919,"tcp_end":[0.49684,-0.0139,0.06943],"tcp_start":[0.50047,-0.01398,0.02869],"tcp_to_object_dist_end":0.04775,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```