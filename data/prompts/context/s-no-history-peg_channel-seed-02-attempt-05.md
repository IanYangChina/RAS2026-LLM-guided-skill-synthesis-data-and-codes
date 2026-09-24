## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

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

## Current Skill (Q=-0.442) — your mutation base

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

- **Composite score**: -0.442
- **task_score** (E): 0.260
- **fitness_score**: 0.448  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.890

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0661 |
| descend_behind_peg | 1.00 | 1.00 | 0.2046 |
| contact_behind | 0.00 | 1.00 | 0.1195 |
| push_through_channel | 1.00 | 1.00 | 0.0993 |
| retract_tcp | 1.00 | 1.00 | 0.0508 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.503, 0.249, 0.264) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.532 | 3.659 |
| descend_behind_peg | descend | 1.00 / step_budget | (0.503, 0.249, 0.264)→(0.497, 0.218, 0.063) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.549 | 0.565 |
| contact_behind | contact | 0.00 / step_budget | (0.497, 0.218, 0.063)→(0.502, 0.103, 0.031) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.545 | 0.552 |
| push_through_channel | push | 1.00 / time_limit | (0.502, 0.103, 0.031)→(0.496, 0.004, 0.028) | (0.498, 0.068, 0.034)→(0.498, -0.026, 0.035) | 0.148→0.055 | 1.00 / 2.333 | 1.444 | 5.180 |
| retract_tcp | retract | 1.00 / step_budget | (0.496, 0.004, 0.028)→(0.492, 0.004, 0.079) | (0.498, -0.026, 0.035)→(0.498, -0.026, 0.034) | 0.055→0.055 | 1.00 / 1.000 | 0.543 | 3.911 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.569
- alignment_error: None
- force_efficiency: 0.943
- terminal_score: 0.395
- phase_score: 0.594
- phase_breakdown.push_complete_score: 0.624
- phase_breakdown.reach_contact_score: 0.523

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.514
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.395
- **Median Q (composite search score)**: -0.457
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60265,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.01073,"approach_peg.approach_offset_y":0.10628,"approach_peg.approach_offset_z":0.1244,"approach_peg.pose_tolerance":0.02341,"contact_behind.contact_offset_x":0.01322,"contact_behind.contact_offset_y":0.01331,"contact_behind.force_threshold":8.65442,"descend_behind_peg.descend_offset_x":-0.00168,"descend_behind_peg.descend_offset_y":0.07651,"descend_behind_peg.pose_tolerance":0.02514,"push_through_channel.force_limit":29.37087,"push_through_channel.max_time":5.98571,"push_through_channel.push_distance":0.15195,"push_through_channel.push_speed":0.05989,"push_through_channel.retry_offset_x":0.00307,"push_through_channel.retry_offset_y":-0.00518},"optimized_scores":{"best_composite_score":-0.37564,"best_fitness_score":0.51436,"best_task_score":0.39526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.49285,0.01611,0.0099],"force_p95":1.2632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.82658,"mean_force":0.78577,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4973,0.05307,0.02695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.49714,0.06354,0.00925],"force_p95":1.25403,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.64194,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49565,0.2277,0.28176]},{"body_a":"attachment","body_b":"peg","contact_count":819.0,"contact_point_centroid":[0.49578,0.03672,0.02705],"force_p95":0.854,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.32654,"mean_force":0.50786,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49692,0.04863,0.02684]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47499,-0.01344,0.03908],"force_p95":1.15945,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09448,"mean_force":0.34702,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49541,0.01644,0.02753]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49428,-0.0087,0.02789],"force_p95":1.99512,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.05785,"mean_force":1.43052,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4948,0.00326,0.0278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":452.0,"contact_point_centroid":[0.4931,-0.02734,0.00941],"force_p95":0.57532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60905,"mean_force":0.55092,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49149,0.00324,0.05307]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49939,0.20318,0.29745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.49502,0.06414,0.00939],"force_p95":0.55223,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56397,"mean_force":0.54585,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.49149,0.23117,0.16588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":722.0,"contact_point_centroid":[0.49504,0.06383,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54541,"phase_index":2.0,"phase_name":"contact_behind","phase_type":"contact","tcp_position_centroid":[0.4953,0.15822,0.04221]}],"total_contact_groups":9},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49322,-0.02718,0.03379],"final_tcp_position":[0.49126,0.00327,0.07847],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":2.82658,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.49524,0.06389,0.03387],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1441,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54634,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":115.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.49293,0.2476,0.27043],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.06376,0.03393],"object_pos_start":[0.49524,0.06389,0.03387],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.1441,"object_z_max":0.03393,"peak_contact_force":0.55076,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":338.0,"raw_peak_contact_force":0.56397,"subtask_id":"reach_contact","tcp_end":[0.49088,0.21392,0.05862],"tcp_start":[0.49293,0.2476,0.27043],"tcp_to_object_dist_end":0.15223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.49502,0.0636,0.03402],"object_pos_start":[0.49493,0.06376,0.03393],"object_to_goal_dist_end":0.14381,"object_to_goal_dist_start":0.14398,"object_z_max":0.03402,"peak_contact_force":0.54259,"phase_name":"contact_behind","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":722.0,"raw_peak_contact_force":0.55289,"subtask_id":"reach_contact","tcp_end":[0.50329,0.10246,0.03036],"tcp_start":[0.49088,0.21392,0.05862],"tcp_to_object_dist_end":0.0399,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49348,-0.02659,0.03498],"object_pos_start":[0.49502,0.0636,0.03402],"object_to_goal_dist_end":0.05404,"object_to_goal_dist_start":0.14381,"object_z_max":0.03506,"peak_contact_force":0.35516,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1769.0,"raw_peak_contact_force":2.82658,"subtask_id":"push_complete","tcp_end":[0.49481,0.00329,0.02781],"tcp_start":[0.50329,0.10246,0.03036],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":600.0,"object_pos_end":[0.49322,-0.02718,0.03379],"object_pos_start":[0.49348,-0.02659,0.03498],"object_to_goal_dist_end":0.05361,"object_to_goal_dist_start":0.05404,"object_z_max":0.03498,"peak_contact_force":0.55037,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":454.0,"raw_peak_contact_force":2.05785,"tcp_end":[0.49126,0.00327,0.07847],"tcp_start":[0.49481,0.00329,0.02781],"tcp_to_object_dist_end":0.05411,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00199,"approach_peg.approach_offset_y":0.09837,"approach_peg.approach_offset_z":0.0984,"approach_peg.pose_tolerance":0.03125,"contact_behind.contact_offset_x":0.01238,"contact_behind.contact_offset_y":0.01079,"contact_behind.force_threshold":5.09447,"descend_behind_peg.descend_offset_x":0.00559,"descend_behind_peg.descend_offset_y":0.08158,"descend_behind_peg.pose_tolerance":0.03073,"push_through_channel.force_limit":28.84733,"push_through_channel.max_time":11.2317,"push_through_channel.push_distance":0.14535,"push_through_channel.push_speed":0.0598,"push_through_channel.retry_offset_x":0.00375,"push_through_channel.retry_offset_y":-0.00245},"optimized_scores":{"best_composite_score":-0.45667,"best_fitness_score":0.43333,"best_task_score":0.19911},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":794.0,"contact_point_centroid":[0.49469,0.03089,0.02721],"force_p95":1.07406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.94508,"mean_force":0.57637,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49567,0.04281,0.02703]},{"body_a":"peg","body_b":"channel_base_body","contact_count":59.0,"contact_point_centroid":[0.49671,0.0584,0.0091],"force_p95":2.41979,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.79336,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48729,0.22177,0.27251]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":394.0,"contact_point_centroid":[0.47495,0.00403,0.034],"force_p95":0.72012,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.11306,"mean_force":0.2958,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4952,0.03389,0.02717]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49726,0.20429,0.29387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":895.0,"contact_point_centroid":[0.49322,0.00929,0.0099],"force_p95":1.35151,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.83109,"mean_force":0.80015,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49599,0.04621,0.02714]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49327,-0.01584,0.02798],"force_p95":1.81211,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.84344,"mean_force":1.53009,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49344,-0.00385,0.02796]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47484,-0.03431,0.05265],"force_p95":1.07247,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57974,"mean_force":0.1839,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49291,-0.00399,0.02829]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.49308,-0.03455,0.00942],"force_p95":0.57974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08643,"mean_force":0.54755,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49014,-0.00382,0.05328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.49393,0.05907,0.00938],"force_p95":0.55479,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57617,"mean_force":0.54637,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.4864,0.22474,0.16214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":752.0,"contact_point_centroid":[0.49413,0.05902,0.00939],"force_p95":0.55033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54603,"phase_index":2.0,"phase_name":"contact_behind","phase_type":"contact","tcp_position_centroid":[0.4963,0.15432,0.04475]}],"total_contact_groups":10},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49333,-0.03428,0.03378],"final_tcp_position":[0.4899,-0.00379,0.07865],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":4.94508,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.49414,0.05898,0.03374],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.50216,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":94.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.47973,0.23523,0.25701],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.49416,0.05887,0.03385],"object_pos_start":[0.49414,0.05898,0.03374],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13924,"object_z_max":0.03385,"peak_contact_force":0.54513,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":267.0,"raw_peak_contact_force":0.57617,"subtask_id":"reach_contact","tcp_end":[0.49424,0.21336,0.06372],"tcp_start":[0.47973,0.23523,0.25701],"tcp_to_object_dist_end":0.15735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.49399,0.05881,0.03394],"object_pos_start":[0.49416,0.05887,0.03385],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.13913,"object_z_max":0.03394,"peak_contact_force":0.54726,"phase_name":"contact_behind","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":752.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_contact","tcp_end":[0.50198,0.09521,0.03053],"tcp_start":[0.49424,0.21336,0.06372],"tcp_to_object_dist_end":0.03742,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49305,-0.03384,0.03494],"object_pos_start":[0.49399,0.05881,0.03394],"object_to_goal_dist_end":0.04696,"object_to_goal_dist_start":0.13907,"object_z_max":0.03535,"peak_contact_force":0.74709,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2083.0,"raw_peak_contact_force":4.94508,"subtask_id":"push_complete","tcp_end":[0.49345,-0.00382,0.02797],"tcp_start":[0.50198,0.09521,0.03053],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":449.0,"n_steps_budget":600.0,"object_pos_end":[0.49333,-0.03428,0.03378],"object_pos_start":[0.49305,-0.03384,0.03494],"object_to_goal_dist_end":0.04662,"object_to_goal_dist_start":0.04696,"object_z_max":0.035,"peak_contact_force":0.54144,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":465.0,"raw_peak_contact_force":1.84344,"tcp_end":[0.4899,-0.00379,0.07865],"tcp_start":[0.49345,-0.00382,0.02797],"tcp_to_object_dist_end":0.05436,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61538,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.01751,"approach_peg.approach_offset_y":0.11395,"approach_peg.approach_offset_z":0.11448,"approach_peg.pose_tolerance":0.03682,"contact_behind.contact_offset_x":-0.00261,"contact_behind.contact_offset_y":0.00581,"contact_behind.force_threshold":6.28467,"descend_behind_peg.descend_offset_x":-0.00496,"descend_behind_peg.descend_offset_y":0.06974,"descend_behind_peg.pose_tolerance":0.03362,"push_through_channel.force_limit":35.6649,"push_through_channel.max_time":10.58606,"push_through_channel.push_distance":0.13874,"push_through_channel.push_speed":0.05971,"push_through_channel.retry_offset_x":0.00293,"push_through_channel.retry_offset_y":-0.00672},"optimized_scores":{"best_composite_score":-0.49264,"best_fitness_score":0.39736,"best_task_score":0.18674},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":456.0,"contact_point_centroid":[0.50651,-0.01748,0.00943],"force_p95":0.58362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83149,"mean_force":0.56244,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49623,0.01303,0.05353]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.5067,0.01735,0.00993],"force_p95":6.12735,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.76713,"mean_force":3.48869,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49784,0.06296,0.02727]},{"body_a":"attachment","body_b":"peg","contact_count":837.0,"contact_point_centroid":[0.50302,0.04863,0.04231],"force_p95":5.95496,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.5677,"mean_force":2.57881,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49781,0.06025,0.02716]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50456,0.0011,0.05772],"force_p95":0.37378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.3939,"mean_force":0.49432,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49825,0.01294,0.02999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":82.0,"contact_point_centroid":[0.50415,0.08074,0.00923],"force_p95":1.98681,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.7331,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52166,0.23818,0.27806]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50438,0.20683,0.29585]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":501.0,"contact_point_centroid":[0.52503,0.03081,0.02373],"force_p95":2.20816,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.09219,"mean_force":0.81448,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49784,0.05932,0.02718]},{"body_a":"peg","body_b":"channel_base_body","contact_count":248.0,"contact_point_centroid":[0.50592,0.08097,0.00938],"force_p95":0.55083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55543,"mean_force":0.54669,"phase_index":1.0,"phase_name":"descend_behind_peg","phase_type":"descend","tcp_position_centroid":[0.52067,0.2461,0.16698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":722.0,"contact_point_centroid":[0.50602,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54676,"phase_index":2.0,"phase_name":"contact_behind","phase_type":"contact","tcp_position_centroid":[0.50036,0.16938,0.04583]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.01587,0.0105],"force_p95":0.31835,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31854,"mean_force":0.2923,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49948,0.01302,0.02796]}],"total_contact_groups":10},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50677,-0.01669,0.03379],"final_tcp_position":[0.49606,0.01306,0.07871],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":7.83149,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":111.0,"n_steps_budget":750.0,"object_pos_end":[0.50596,0.08088,0.03377],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54671,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":118.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.5358,0.26389,0.26441],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08088,0.03377],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":0.55023,"phase_name":"descend_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":248.0,"raw_peak_contact_force":0.55543,"subtask_id":"reach_contact","tcp_end":[0.5047,0.22662,0.0661],"tcp_start":[0.5358,0.26389,0.26441],"tcp_to_object_dist_end":0.14929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"contact_behind","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":722.0,"raw_peak_contact_force":0.55014,"subtask_id":"reach_contact","tcp_end":[0.49955,0.11217,0.03062],"tcp_start":[0.5047,0.22662,0.0661],"tcp_to_object_dist_end":0.03212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.0162,0.03542],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.06434,"object_to_goal_dist_start":0.16109,"object_z_max":0.03589,"peak_contact_force":3.2294,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2011.0,"raw_peak_contact_force":7.76713,"subtask_id":"push_complete","tcp_end":[0.49961,0.01315,0.028],"tcp_start":[0.49955,0.11217,0.03062],"tcp_to_object_dist_end":0.03115,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.50677,-0.01669,0.03379],"object_pos_start":[0.50695,-0.0162,0.03542],"object_to_goal_dist_end":0.06397,"object_to_goal_dist_start":0.06434,"object_z_max":0.03544,"peak_contact_force":0.5373,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":482.0,"raw_peak_contact_force":7.83149,"tcp_end":[0.49606,0.01306,0.07871],"tcp_start":[0.49961,0.01315,0.028],"tcp_to_object_dist_end":0.05494,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```