## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

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

## Current Skill (Q=-0.565) — your mutation base

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

- **Composite score**: -0.565
- **task_score** (E): 0.000
- **fitness_score**: 0.125  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.940

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0531 |
| descend_to_peg | 1.00 | 1.00 | 0.1522 |
| contact_peg | 1.00 | 1.00 | 0.0730 |
| push_phase | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.161, 0.271) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.516 | 3.659 |
| descend_to_peg | descend | 1.00 / step_budget | (0.503, 0.161, 0.271)→(0.498, 0.112, 0.127) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.547 | 0.631 |
| contact_peg | contact | 1.00 / force_exceeded | (0.498, 0.112, 0.127)→(0.492, 0.082, 0.061) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 59.979 | 59.979 |
| push_phase | push | 0.00 / guard_failure | (0.492, 0.082, 0.061)→(0.492, 0.082, 0.061) | (0.498, 0.068, 0.034)→(0.499, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 302.002 | 302.002 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.216
- phase_breakdown.push_complete_score: 0.000
- phase_breakdown.reach_contact_score: 0.720

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.130
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.561
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93902,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00621,"approach_peg.approach_offset_y":0.04587,"approach_peg.approach_offset_z":0.12368,"approach_peg.pose_tolerance":0.03992,"contact_peg.approach_offset_x":-0.00945,"contact_peg.contact_offset_y":0.00961,"contact_peg.force_threshold":12.24872,"descend_to_peg.approach_offset_x":-0.01058,"descend_to_peg.approach_offset_y":0.02234,"descend_to_peg.descend_offset_z":0.03934,"descend_to_peg.pose_tolerance":0.02422,"push_phase.force_limit_guard":36.01243,"push_phase.max_time":7.91002,"push_phase.push_distance":0.15884,"push_phase.push_speed":0.03434,"push_phase.retry_offset_x":-0.0019,"push_phase.retry_offset_y":-0.00182},"optimized_scores":{"best_composite_score":-0.55982,"best_fitness_score":0.13018,"best_task_score":0.00097},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49379,0.07764,0.05893],"force_p95":146.24073,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.24073,"mean_force":146.24073,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48193,0.07751,0.06059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50684,0.05023,0.0094],"force_p95":146.13003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.13003,"mean_force":146.13003,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48193,0.07751,0.06059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.49486,0.06389,0.0094],"force_p95":0.55024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.06062,"mean_force":0.59693,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48154,0.09196,0.09052]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49376,0.07778,0.05902],"force_p95":19.64096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.64096,"mean_force":19.64096,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4819,0.07758,0.06074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.5106,0.06481,0.00902],"force_p95":2.14508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":1.0463,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49539,0.18076,0.28624]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49846,0.19493,0.29641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.49491,0.06369,0.00937],"force_p95":0.58586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75051,"mean_force":0.54531,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48865,0.1412,0.20345]}],"total_contact_groups":7},"final_pose_error":0.16147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49543,0.06363,0.03399],"final_tcp_position":[0.48221,0.07729,0.06038],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":146.24073,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.49521,0.06394,0.03327],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14417,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.44345,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":45.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.49405,0.17416,0.28177],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.49521,0.064,0.03391],"object_pos_start":[0.49521,0.06394,0.03327],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14417,"object_z_max":0.03391,"peak_contact_force":0.54542,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":282.0,"raw_peak_contact_force":0.75051,"subtask_id":"reach_contact","tcp_end":[0.48372,0.10706,0.12409],"tcp_start":[0.49405,0.17416,0.28177],"tcp_to_object_dist_end":0.10059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.49525,0.06368,0.03397],"object_pos_start":[0.49521,0.064,0.03391],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14421,"object_z_max":0.03397,"peak_contact_force":20.06062,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":382.0,"raw_peak_contact_force":20.06062,"subtask_id":"reach_contact","tcp_end":[0.48193,0.07751,0.06059],"tcp_start":[0.48372,0.10706,0.12409],"tcp_to_object_dist_end":0.03282,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49543,0.06363,0.03399],"object_pos_start":[0.49525,0.06368,0.03397],"object_to_goal_dist_end":0.14383,"object_to_goal_dist_start":0.14388,"object_z_max":0.03397,"peak_contact_force":146.24073,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":146.24073,"subtask_id":"push_complete","tcp_end":[0.48221,0.07729,0.06038],"tcp_start":[0.48193,0.07751,0.06059],"tcp_to_object_dist_end":0.03252,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82927,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00887,"approach_peg.approach_offset_y":0.02289,"approach_peg.approach_offset_z":0.11377,"approach_peg.pose_tolerance":0.037,"contact_peg.approach_offset_x":-0.01815,"contact_peg.contact_offset_y":0.00999,"contact_peg.force_threshold":6.76242,"descend_to_peg.approach_offset_x":-0.00774,"descend_to_peg.approach_offset_y":0.02579,"descend_to_peg.descend_offset_z":0.0247,"descend_to_peg.pose_tolerance":0.02488,"push_phase.force_limit_guard":28.70388,"push_phase.max_time":13.52747,"push_phase.push_distance":0.16784,"push_phase.push_speed":0.05568,"push_phase.retry_offset_x":0.00821,"push_phase.retry_offset_y":-0.00487},"optimized_scores":{"best_composite_score":-0.56059,"best_fitness_score":0.12941,"best_task_score":6e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48549,0.07303,0.05871],"force_p95":79.50471,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.50471,"mean_force":79.50471,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.47366,0.07373,0.06047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48245,0.07264,0.00939],"force_p95":78.23716,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.23716,"mean_force":78.23716,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.47366,0.07373,0.06047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":311.0,"contact_point_centroid":[0.49412,0.05903,0.00939],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.01808,"mean_force":0.61525,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47748,0.08771,0.08458]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48549,0.07306,0.05878],"force_p95":21.58489,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.58489,"mean_force":21.58489,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47366,0.07382,0.06062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":56.0,"contact_point_centroid":[0.49645,0.05919,0.00908],"force_p95":2.49461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.80821,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48984,0.16491,0.27865]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49733,0.19206,0.29502]},{"body_a":"peg","body_b":"channel_base_body","contact_count":263.0,"contact_point_centroid":[0.49431,0.05895,0.00938],"force_p95":0.55479,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57617,"mean_force":0.54603,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48363,0.12353,0.19042]}],"total_contact_groups":7},"final_pose_error":0.17022,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49416,0.05892,0.03373],"final_tcp_position":[0.47394,0.07341,0.06026],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":79.50471,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":85.0,"n_steps_budget":660.0,"object_pos_end":[0.49413,0.0589,0.03373],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.56936,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":91.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.48429,0.14455,0.26718],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.49408,0.05905,0.03385],"object_pos_start":[0.49413,0.0589,0.03373],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.13916,"object_z_max":0.03385,"peak_contact_force":0.54674,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":263.0,"raw_peak_contact_force":0.57617,"subtask_id":"reach_contact","tcp_end":[0.48375,0.10188,0.11165],"tcp_start":[0.48429,0.14455,0.26718],"tcp_to_object_dist_end":0.08942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":311.0,"n_steps_budget":600.0,"object_pos_end":[0.49404,0.05906,0.03388],"object_pos_start":[0.49408,0.05905,0.03385],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.13931,"object_z_max":0.03388,"peak_contact_force":22.01808,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":312.0,"raw_peak_contact_force":22.01808,"subtask_id":"reach_contact","tcp_end":[0.47366,0.07373,0.06047],"tcp_start":[0.48375,0.10188,0.11165],"tcp_to_object_dist_end":0.03658,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.05892,0.03373],"object_pos_start":[0.49404,0.05906,0.03388],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.13932,"object_z_max":0.03388,"peak_contact_force":79.50471,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":79.50471,"subtask_id":"push_complete","tcp_end":[0.47394,0.07341,0.06026],"tcp_start":[0.47366,0.07373,0.06047],"tcp_to_object_dist_end":0.03637,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94937,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.0188,"approach_peg.approach_offset_y":0.02761,"approach_peg.approach_offset_z":0.10439,"approach_peg.pose_tolerance":0.03902,"contact_peg.approach_offset_x":0.01893,"contact_peg.contact_offset_y":0.00932,"contact_peg.force_threshold":3.98204,"descend_to_peg.approach_offset_x":0.01666,"descend_to_peg.approach_offset_y":0.02233,"descend_to_peg.descend_offset_z":0.03417,"descend_to_peg.pose_tolerance":0.04919,"push_phase.force_limit_guard":29.15986,"push_phase.max_time":5.94609,"push_phase.push_distance":0.182,"push_phase.push_speed":0.05784,"push_phase.retry_offset_x":-0.00463,"push_phase.retry_offset_y":0.00999},"optimized_scores":{"best_composite_score":-0.57406,"best_fitness_score":0.11594,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53296,0.09371,0.05992],"force_p95":680.25922,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":680.25922,"mean_force":680.25922,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52113,0.09429,0.0617]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53294,0.09377,0.06],"force_p95":137.85804,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.85804,"mean_force":137.85804,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5211,0.09435,0.06186]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.50303,0.08121,0.00914],"force_p95":2.70717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.85423,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5204,0.17663,0.27584]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50499,0.19441,0.29412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":115.0,"contact_point_centroid":[0.50609,0.0807,0.00938],"force_p95":0.55754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56764,"mean_force":0.54578,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.52915,0.14694,0.20724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55176,"mean_force":0.54677,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52165,0.11051,0.09925]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49063,0.07157,0.00938],"force_p95":0.54639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54639,"mean_force":0.54639,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52113,0.09429,0.0617]}],"total_contact_groups":7},"final_pose_error":0.18441,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.08089,0.03378],"final_tcp_position":[0.52117,0.09422,0.06161],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":680.25922,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":79.0,"n_steps_budget":630.0,"object_pos_end":[0.50599,0.08088,0.0337],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.53394,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":86.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.53176,0.16343,0.26291],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08088,0.0337],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":0.54832,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":115.0,"raw_peak_contact_force":0.56764,"subtask_id":"reach_contact","tcp_end":[0.52525,0.12849,0.1445],"tcp_start":[0.53176,0.16343,0.26291],"tcp_to_object_dist_end":0.12206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":414.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":137.85804,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":415.0,"raw_peak_contact_force":137.85804,"subtask_id":"reach_contact","tcp_end":[0.52113,0.09429,0.0617],"tcp_start":[0.52525,0.12849,0.1445],"tcp_to_object_dist_end":0.0345,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":680.25922,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":680.25922,"subtask_id":"push_complete","tcp_end":[0.52117,0.09422,0.06161],"tcp_start":[0.52113,0.09429,0.0617],"tcp_to_object_dist_end":0.03441,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```