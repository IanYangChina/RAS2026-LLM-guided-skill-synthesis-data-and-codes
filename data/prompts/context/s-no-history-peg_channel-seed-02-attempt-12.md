## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

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

## Current Skill (Q=-0.457) — your mutation base

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

- **Composite score**: -0.457
- **task_score** (E): 0.359
- **fitness_score**: 0.483  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.940

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0393 |
| descend_to_peg | 1.00 | 1.00 | 0.1626 |
| contact_peg | 0.00 | 1.00 | 0.0938 |
| push_phase | 1.00 | 1.00 | 0.1500 |
| retract_tcp | 1.00 | 1.00 | 0.0412 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.186, 0.268) | (0.494, 0.068, 0.040)→(0.497, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.362 | 3.398 |
| descend_to_peg | descend | 1.00 / step_budget | (0.502, 0.186, 0.268)→(0.492, 0.167, 0.108) | (0.497, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 1.774 |
| contact_peg | contact | 0.00 / step_budget | (0.492, 0.167, 0.108)→(0.498, 0.093, 0.051) | (0.498, 0.068, 0.034)→(0.498, 0.064, 0.037) | 0.148→0.144 | 1.00 / 1.333 | 0.457 | 10.099 |
| push_phase | push | 1.00 / time_limit | (0.498, 0.093, 0.051)→(0.499, -0.055, 0.027) | (0.498, 0.064, 0.037)→(0.497, -0.078, 0.028) | 0.144→0.016 | 1.00 / 3.333 | 2185.380 | 178.053 |
| retract_tcp | retract | 1.00 / step_budget | (0.499, -0.055, 0.027)→(0.495, -0.053, 0.068) | (0.497, -0.078, 0.028)→(0.496, -0.075, 0.043) | 0.016→0.016 | 1.00 / 1.667 | 11.677 | 59.469 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.877
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.596
- phase_score: 0.585
- phase_breakdown.push_complete_score: 0.542
- phase_breakdown.reach_contact_score: 0.684

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.596
- **Median Q (composite search score)**: -0.482
- **K-run variance**: 0.0062
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69853,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.0016,"approach_peg.approach_offset_y":0.04295,"approach_peg.approach_offset_z":0.11381,"approach_peg.pose_tolerance":0.01355,"contact_peg.approach_offset_x":0.00708,"contact_peg.contact_offset_y":0.0134,"contact_peg.contact_offset_z":0.01291,"contact_peg.force_threshold":13.03613,"descend_to_peg.approach_offset_x":-0.00412,"descend_to_peg.approach_offset_y":0.03773,"descend_to_peg.descend_offset_z":0.01516,"descend_to_peg.pose_tolerance":0.0329,"push_phase.max_time":6.95896,"push_phase.push_distance":0.17627,"push_phase.push_speed":0.09194,"push_phase.retry_offset_x":-0.00257,"push_phase.retry_offset_y":-0.00219},"optimized_scores":{"best_composite_score":-0.35075,"best_fitness_score":0.58925,"best_task_score":0.59611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.54964,-0.1,0.06499],"force_p95":125.03974,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.98603,"mean_force":82.48135,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49431,-0.05026,0.02579]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54927,-0.1,0.06499],"force_p95":56.39878,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.33302,"mean_force":47.99057,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49537,-0.05324,0.02602]},{"body_a":"attachment","body_b":"peg","contact_count":842.0,"contact_point_centroid":[0.49436,0.01147,0.03889],"force_p95":20.14599,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.86147,"mean_force":9.32392,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49411,0.02327,0.03667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49301,-0.10023,0.04039],"force_p95":15.42057,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.17571,"mean_force":6.98175,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49503,-0.05243,0.02595]},{"body_a":"attachment","body_b":"peg","contact_count":429.0,"contact_point_centroid":[0.49259,-0.06364,0.04783],"force_p95":11.58949,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.54399,"mean_force":8.73608,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49179,-0.05185,0.04721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.49334,-0.10026,0.06127],"force_p95":11.41437,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.46215,"mean_force":8.41575,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49183,-0.05188,0.04674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":864.0,"contact_point_centroid":[0.49352,-0.01624,0.00987],"force_p95":19.85247,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.76177,"mean_force":8.97173,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49414,0.02179,0.03649]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":230.0,"contact_point_centroid":[0.47497,0.00984,0.03193],"force_p95":7.80444,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.72227,"mean_force":3.78476,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49429,0.03723,0.03889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.49523,0.06314,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.71122,"mean_force":0.5892,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49103,0.12268,0.07419]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49624,0.08154,0.05222],"force_p95":7.95147,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.1894,"mean_force":3.26412,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49688,0.09334,0.05209]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":132.0,"contact_point_centroid":[0.47485,-0.08123,0.03244],"force_p95":5.25666,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21745,"mean_force":1.41822,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4925,-0.05236,0.03631]},{"body_a":"peg","body_b":"channel_base_body","contact_count":114.0,"contact_point_centroid":[0.49635,0.06423,0.00928],"force_p95":1.13478,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.61904,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49132,0.18165,0.27729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.50496,-0.08617,0.00996],"force_p95":0.74645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23206,"mean_force":0.39419,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49431,-0.0531,0.02739]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49869,0.1977,0.29729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.4954,0.06395,0.00939],"force_p95":0.55205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55842,"mean_force":0.54593,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4866,0.16088,0.18384]}],"total_contact_groups":15},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49364,-0.07639,0.05023],"final_tcp_position":[0.49166,-0.05156,0.06696],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":143.98603,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":141.0,"n_steps_budget":600.0,"object_pos_end":[0.49504,0.06374,0.03388],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14396,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55502,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":142.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.48533,0.16767,0.26144],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.06394,0.03392],"object_pos_start":[0.49504,0.06374,0.03388],"object_to_goal_dist_end":0.14416,"object_to_goal_dist_start":0.14396,"object_z_max":0.03392,"peak_contact_force":0.54495,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":210.0,"raw_peak_contact_force":0.55842,"subtask_id":"reach_contact","tcp_end":[0.48814,0.15392,0.10166],"tcp_start":[0.48533,0.16767,0.26144],"tcp_to_object_dist_end":0.11283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49545,0.06153,0.03569],"object_pos_start":[0.49493,0.06394,0.03392],"object_to_goal_dist_end":0.14167,"object_to_goal_dist_start":0.14416,"object_z_max":0.03562,"peak_contact_force":0.40686,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":550.0,"raw_peak_contact_force":8.71122,"subtask_id":"reach_contact","tcp_end":[0.49725,0.09134,0.05061],"tcp_start":[0.48814,0.15392,0.10166],"tcp_to_object_dist_end":0.03338,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49373,-0.08258,0.03511],"object_pos_start":[0.49545,0.06153,0.03569],"object_to_goal_dist_end":0.00836,"object_to_goal_dist_start":0.14167,"object_z_max":0.04041,"peak_contact_force":40.86147,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2007.0,"raw_peak_contact_force":143.98603,"subtask_id":"push_complete","tcp_end":[0.49536,-0.05316,0.02603],"tcp_start":[0.49725,0.09134,0.05061],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.49364,-0.07639,0.05023],"object_pos_start":[0.49373,-0.08258,0.03511],"object_to_goal_dist_end":0.01257,"object_to_goal_dist_start":0.00836,"object_z_max":0.05018,"peak_contact_force":6.63675,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1019.0,"raw_peak_contact_force":57.33302,"tcp_end":[0.49166,-0.05156,0.06696],"tcp_start":[0.49536,-0.05316,0.02603],"tcp_to_object_dist_end":0.03001,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68794,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.01377,"approach_peg.approach_offset_y":0.07018,"approach_peg.approach_offset_z":0.1083,"approach_peg.pose_tolerance":0.04239,"contact_peg.approach_offset_x":0.00794,"contact_peg.contact_offset_y":0.0059,"contact_peg.contact_offset_z":0.01239,"contact_peg.force_threshold":21.48657,"descend_to_peg.approach_offset_x":0.00143,"descend_to_peg.approach_offset_y":0.0618,"descend_to_peg.descend_offset_z":0.02585,"descend_to_peg.pose_tolerance":0.03212,"push_phase.max_time":5.49083,"push_phase.push_distance":0.16001,"push_phase.push_speed":0.09835,"push_phase.retry_offset_x":-0.00364,"push_phase.retry_offset_y":0.00107},"optimized_scores":{"best_composite_score":-0.48202,"best_fitness_score":0.45798,"best_task_score":0.28111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":149.0,"contact_point_centroid":[0.5503,-0.1,0.06498],"force_p95":221.67778,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":267.09493,"mean_force":142.9972,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49659,-0.05321,0.02549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.49835,-0.10135,0.04262],"force_p95":55.42957,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.46333,"mean_force":26.61321,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49748,-0.05532,0.02564]},{"body_a":"attachment","body_b":"peg","contact_count":799.0,"contact_point_centroid":[0.49562,-0.00214,0.03995],"force_p95":33.3502,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.38452,"mean_force":16.14053,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49525,0.00958,0.03519]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52968,-0.03936,0.05999],"force_p95":43.3149,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.42587,"mean_force":17.83194,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49375,-0.04577,0.02498]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.55057,-0.1,0.065],"force_p95":44.46668,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.28639,"mean_force":37.08924,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49943,-0.05906,0.02593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.49404,-0.10127,0.05528],"force_p95":33.08723,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.03077,"mean_force":27.8399,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49576,-0.0554,0.04626]},{"body_a":"attachment","body_b":"peg","contact_count":463.0,"contact_point_centroid":[0.4955,-0.06695,0.04867],"force_p95":33.22036,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.70845,"mean_force":27.88037,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49576,-0.0554,0.04626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":786.0,"contact_point_centroid":[0.49429,-0.0254,0.00985],"force_p95":26.95486,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.77631,"mean_force":12.07901,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49502,0.01243,0.03555]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.49606,0.07411,0.0538],"force_p95":11.27915,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.82993,"mean_force":6.14675,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49683,0.08598,0.05373]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":338.0,"contact_point_centroid":[0.47494,0.02065,0.03247],"force_p95":10.08501,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.72633,"mean_force":6.5752,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.4954,0.04768,0.04176]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.49414,0.05725,0.00942],"force_p95":0.55151,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.61397,"mean_force":0.66921,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49195,0.12709,0.07916]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,-0.08458,0.06],"force_p95":5.49018,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.30458,"mean_force":3.3884,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49526,-0.05542,0.0448]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47481,0.05098,0.05979],"force_p95":4.51227,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.89834,"mean_force":0.95005,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49717,0.08324,0.05204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.49488,0.05909,0.00931],"force_p95":0.68875,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.61142,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49187,0.18418,0.19923]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.46656,0.05895,0.0414],"force_p95":1.25039,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.51415,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49809,0.19788,0.29496]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47413,0.05896,0.02422],"force_p95":0.89792,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95784,"mean_force":0.46267,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49406,0.19369,0.28268]}],"total_contact_groups":16},"final_pose_error":0.01072,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49455,-0.08098,0.0536],"final_tcp_position":[0.49592,-0.05428,0.06699],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":267.09493,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.48913,0.05896,0.03518],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13947,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":3.42382,"subtask_id":"reach_contact","tcp_end":[0.49471,0.19424,0.28453],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.059,0.03383],"object_pos_start":[0.48913,0.05896,0.03518],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.13947,"object_z_max":0.03518,"peak_contact_force":0.5439,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":231.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.48955,0.17412,0.11233],"tcp_start":[0.49471,0.19424,0.28453],"tcp_to_object_dist_end":0.13941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.49295,0.05171,0.03853],"object_pos_start":[0.49405,0.059,0.03383],"object_to_goal_dist_end":0.13191,"object_to_goal_dist_start":0.13927,"object_z_max":0.03851,"peak_contact_force":0.55855,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":721.0,"raw_peak_contact_force":12.82993,"subtask_id":"reach_contact","tcp_end":[0.49757,0.07988,0.04998],"tcp_start":[0.48955,0.17412,0.11233],"tcp_to_object_dist_end":0.03075,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.49843,-0.0881,0.03518],"object_pos_start":[0.49295,0.05171,0.03853],"object_to_goal_dist_end":0.00956,"object_to_goal_dist_start":0.13191,"object_z_max":0.04043,"peak_contact_force":225.14151,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2188.0,"raw_peak_contact_force":267.09493,"subtask_id":"push_complete","tcp_end":[0.49941,-0.05906,0.02593],"tcp_start":[0.49757,0.07988,0.04998],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.49455,-0.08098,0.0536],"object_pos_start":[0.49843,-0.0881,0.03518],"object_to_goal_dist_end":0.01468,"object_to_goal_dist_start":0.00956,"object_z_max":0.05356,"peak_contact_force":27.70228,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":936.0,"raw_peak_contact_force":45.28639,"tcp_end":[0.49592,-0.05428,0.06699],"tcp_start":[0.49941,-0.05906,0.02593],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74074,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00403,"approach_peg.approach_offset_y":0.06243,"approach_peg.approach_offset_z":0.10636,"approach_peg.pose_tolerance":0.01991,"contact_peg.approach_offset_x":-0.0023,"contact_peg.contact_offset_y":0.01277,"contact_peg.contact_offset_z":0.01394,"contact_peg.force_threshold":22.5302,"descend_to_peg.approach_offset_x":-0.01063,"descend_to_peg.approach_offset_y":0.03784,"descend_to_peg.descend_offset_z":0.02401,"descend_to_peg.pose_tolerance":0.03222,"push_phase.max_time":9.82289,"push_phase.push_distance":0.17652,"push_phase.push_speed":0.09958,"push_phase.retry_offset_x":-0.00809,"push_phase.retry_offset_y":-0.00164},"optimized_scores":{"best_composite_score":-0.53905,"best_fitness_score":0.40095,"best_task_score":0.20114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":928.0,"contact_point_centroid":[0.50251,0.01895,0.03857],"force_p95":111.7851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.07875,"mean_force":61.07097,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49845,0.02947,0.03863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.5043,0.00748,0.00695],"force_p95":106.15383,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.58686,"mean_force":54.17975,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49849,0.02914,0.03863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50028,-0.06722,0.00744],"force_p95":51.13518,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.78764,"mean_force":10.13338,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49895,-0.05273,0.05086]},{"body_a":"attachment","body_b":"peg","contact_count":84.0,"contact_point_centroid":[0.50236,-0.0647,0.03626],"force_p95":52.95129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.11234,"mean_force":28.90497,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50055,-0.05286,0.03625]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":172.0,"contact_point_centroid":[0.47487,-0.0371,0.01317],"force_p95":48.58728,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.03589,"mean_force":30.70897,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50024,-0.03799,0.03029]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":145.0,"contact_point_centroid":[0.47494,-0.0483,0.02073],"force_p95":32.87723,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.02191,"mean_force":10.06681,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49979,-0.05281,0.0434]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":112.0,"contact_point_centroid":[0.52502,-0.08428,0.02225],"force_p95":29.19948,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.06889,"mean_force":9.49553,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49951,-0.05276,0.046]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":634.0,"contact_point_centroid":[0.52535,0.02616,0.02964],"force_p95":38.72608,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.34036,"mean_force":22.03616,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49774,0.05169,0.04124]},{"body_a":"peg","body_b":"world","contact_count":349.0,"contact_point_centroid":[0.4983,-0.03978,-0.00203],"force_p95":7.46159,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.37855,"mean_force":1.14528,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49973,-0.0266,0.03153]},{"body_a":"peg","body_b":"world","contact_count":46.0,"contact_point_centroid":[0.50156,-0.07077,-0.0021],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.99178,"mean_force":0.71581,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50103,-0.05297,0.03181]},{"body_a":"peg","body_b":"channel_base_body","contact_count":535.0,"contact_point_centroid":[0.50607,0.08023,0.00939],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.75546,"mean_force":0.6085,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.498,0.14014,0.07824]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50245,0.09762,0.05571],"force_p95":8.44184,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.49818,"mean_force":5.94864,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49954,0.10933,0.05314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":76.0,"contact_point_centroid":[0.50402,0.08063,0.00921],"force_p95":2.10826,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.74771,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51484,0.19681,0.27493]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50291,0.19925,0.29497]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.50606,0.08095,0.00938],"force_p95":0.5515,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55706,"mean_force":0.5467,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51259,0.18432,0.1861]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49999,-0.06662,0.02411],"final_tcp_position":[0.49815,-0.05266,0.06984],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":6290.13844,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":105.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08089,0.03377],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.53052,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":112.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.52486,0.19492,0.25951],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50597,0.08089,0.03377],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54802,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":197.0,"raw_peak_contact_force":0.55706,"subtask_id":"reach_contact","tcp_end":[0.49948,0.17316,0.10912],"tcp_start":[0.52486,0.19492,0.25951],"tcp_to_object_dist_end":0.11932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":535.0,"n_steps_budget":600.0,"object_pos_end":[0.50649,0.07934,0.03545],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.15954,"object_to_goal_dist_start":0.1611,"object_z_max":0.03538,"peak_contact_force":0.40497,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":541.0,"raw_peak_contact_force":8.75546,"subtask_id":"reach_contact","tcp_end":[0.4996,0.10773,0.05185],"tcp_start":[0.49948,0.17316,0.10912],"tcp_to_object_dist_end":0.03351,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49988,-0.06482,0.01286],"object_pos_start":[0.50649,0.07934,0.03545],"object_to_goal_dist_end":0.0311,"object_to_goal_dist_start":0.15954,"object_z_max":0.04003,"peak_contact_force":6290.13844,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3079.0,"raw_peak_contact_force":123.07875,"subtask_id":"push_complete","tcp_end":[0.50177,-0.053,0.02914],"tcp_start":[0.4996,0.10773,0.05185],"tcp_to_object_dist_end":0.02021,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":366.0,"n_steps_budget":600.0,"object_pos_end":[0.49999,-0.06662,0.02411],"object_pos_start":[0.49988,-0.06482,0.01286],"object_to_goal_dist_end":0.02077,"object_to_goal_dist_start":0.0311,"object_z_max":0.02575,"peak_contact_force":0.69053,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":753.0,"raw_peak_contact_force":75.78764,"tcp_end":[0.49815,-0.05266,0.06984],"tcp_start":[0.50177,-0.053,0.02914],"tcp_to_object_dist_end":0.04785,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```