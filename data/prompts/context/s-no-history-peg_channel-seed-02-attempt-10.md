## Search State

- **Seed**: 2
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

## Current Skill (Q=-0.478) — your mutation base

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

- **Composite score**: -0.478
- **task_score** (E): 0.396
- **fitness_score**: 0.462  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.940

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.0320 |
| descend_to_peg | 1.00 | 1.00 | 0.1606 |
| contact_peg | 0.33 | 1.00 | 0.1118 |
| push_phase | 1.00 | 1.00 | 0.1428 |
| retract_tcp | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.187, 0.275) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.033) | 0.151→0.148 | 1.00 / 1.000 | 0.602 | 3.659 |
| descend_to_peg | descend | 1.00 / step_budget | (0.499, 0.187, 0.275)→(0.496, 0.186, 0.115) | (0.498, 0.068, 0.033)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.549 | 0.648 |
| contact_peg | contact | 0.33 / step_budget | (0.496, 0.186, 0.115)→(0.496, 0.096, 0.050) | (0.498, 0.068, 0.034)→(0.498, 0.067, 0.035) | 0.148→0.147 | 1.00 / 1.333 | 2.988 | 6.383 |
| push_phase | push | 1.00 / time_limit | (0.496, 0.096, 0.050)→(0.496, -0.045, 0.025) | (0.498, 0.067, 0.035)→(0.503, -0.073, 0.036) | 0.147→0.015 | 1.00 / 3.333 | 78.179 | 183.425 |
| retract_tcp | retract | 1.00 / step_budget | (0.496, -0.045, 0.025)→(0.493, -0.043, 0.066) | (0.503, -0.073, 0.036)→(0.498, -0.077, 0.038) | 0.015→0.015 | 1.00 / 1.667 | 9.660 | 165.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.863
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.590
- phase_score: 0.485
- phase_breakdown.push_complete_score: 0.362
- phase_breakdown.reach_contact_score: 0.771

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.527
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.590
- **Median Q (composite search score)**: -0.474
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62143,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.00119,"approach_peg.approach_offset_y":0.07171,"approach_peg.approach_offset_z":0.12028,"approach_peg.pose_tolerance":0.02269,"contact_peg.approach_offset_x":-0.00097,"contact_peg.contact_offset_y":0.01426,"contact_peg.contact_offset_z":0.01281,"contact_peg.force_threshold":11.50702,"descend_to_peg.approach_offset_x":0.00257,"descend_to_peg.approach_offset_y":0.05409,"descend_to_peg.descend_offset_z":0.03187,"descend_to_peg.pose_tolerance":0.03354,"push_phase.max_time":9.26551,"push_phase.push_distance":0.16507,"push_phase.push_speed":0.08644,"push_phase.retry_offset_x":0.00113,"push_phase.retry_offset_y":0.00593},"optimized_scores":{"best_composite_score":-0.41297,"best_fitness_score":0.52703,"best_task_score":0.59029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":292.0,"contact_point_centroid":[0.47494,-0.03249,0.0402],"force_p95":361.20103,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.14097,"mean_force":231.59625,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48672,-0.03247,0.03828]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":254.0,"contact_point_centroid":[0.47499,-0.0096,0.03241],"force_p95":126.61808,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.97254,"mean_force":62.25176,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48683,-0.0096,0.03048]},{"body_a":"attachment","body_b":"peg","contact_count":962.0,"contact_point_centroid":[0.49386,0.0175,0.03549],"force_p95":120.0567,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.10387,"mean_force":42.8784,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48701,0.02568,0.03644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":517.0,"contact_point_centroid":[0.52587,-0.01706,0.0222],"force_p95":113.38536,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.10907,"mean_force":53.35854,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48684,-0.00392,0.03147]},{"body_a":"attachment","body_b":"peg","contact_count":132.0,"contact_point_centroid":[0.49589,-0.03744,0.02921],"force_p95":116.45599,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.43172,"mean_force":85.88426,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48667,-0.03285,0.0279]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":161.0,"contact_point_centroid":[0.52673,-0.05233,0.02798],"force_p95":109.50704,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.1566,"mean_force":70.42624,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48669,-0.03263,0.02927]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.50205,-0.00363,0.00964],"force_p95":83.64499,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.41803,"mean_force":31.91567,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48706,0.02686,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50024,-0.0653,0.00885],"force_p95":29.03391,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.15605,"mean_force":5.7323,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48646,-0.03254,0.04381]},{"body_a":"peg","body_b":"link7","contact_count":370.0,"contact_point_centroid":[0.50647,-0.04401,0.06848],"force_p95":36.26113,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.07779,"mean_force":26.40716,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.48684,-0.0126,0.03004]},{"body_a":"peg","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.50665,-0.07315,0.06574],"force_p95":15.64297,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.9073,"mean_force":5.3746,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48661,-0.03335,0.02632]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47482,-0.0604,0.02454],"force_p95":12.33429,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.61412,"mean_force":3.90667,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48679,-0.03233,0.04943]},{"body_a":"peg","body_b":"channel_base_body","contact_count":625.0,"contact_point_centroid":[0.49516,0.06371,0.0094],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.37345,"mean_force":0.56174,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49099,0.13209,0.08244]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49305,0.08149,0.05898],"force_p95":3.54255,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.81226,"mean_force":1.38162,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4904,0.09321,0.05156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.50728,0.06601,0.00903],"force_p95":2.06998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.95965,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4936,0.19499,0.28516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":31.0,"contact_point_centroid":[0.50391,-0.10007,0.02844],"force_p95":1.57481,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81306,"mean_force":0.61792,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.48679,-0.03193,0.03957]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49824,0.1985,0.29638]}],"total_contact_groups":17},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49353,-0.07422,0.02412],"final_tcp_position":[0.4842,-0.03282,0.06587],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":386.14097,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":48.0,"n_steps_budget":600.0,"object_pos_end":[0.49482,0.06384,0.03331],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.71366,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":49.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.49124,0.19317,0.27959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.49505,0.06403,0.0339],"object_pos_start":[0.49482,0.06384,0.03331],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14409,"object_z_max":0.0339,"peak_contact_force":0.54957,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":207.0,"raw_peak_contact_force":0.68508,"subtask_id":"reach_contact","tcp_end":[0.49462,0.17212,0.11828],"tcp_start":[0.49124,0.19317,0.27959],"tcp_to_object_dist_end":0.13712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":625.0,"n_steps_budget":690.0,"object_pos_end":[0.49504,0.0632,0.03419],"object_pos_start":[0.49505,0.06403,0.0339],"object_to_goal_dist_end":0.1434,"object_to_goal_dist_start":0.14425,"object_z_max":0.03409,"peak_contact_force":0.60833,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":633.0,"raw_peak_contact_force":4.37345,"subtask_id":"reach_contact","tcp_end":[0.49038,0.09265,0.05111],"tcp_start":[0.49462,0.17212,0.11828],"tcp_to_object_dist_end":0.03428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50778,-0.05978,0.03684],"object_pos_start":[0.49504,0.0632,0.03419],"object_to_goal_dist_end":0.0219,"object_to_goal_dist_start":0.1434,"object_z_max":0.0407,"peak_contact_force":132.65274,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3077.0,"raw_peak_contact_force":149.97254,"subtask_id":"push_complete","tcp_end":[0.48677,-0.03319,0.02552],"tcp_start":[0.49038,0.09265,0.05111],"tcp_to_object_dist_end":0.03573,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":391.0,"n_steps_budget":600.0,"object_pos_end":[0.49353,-0.07422,0.02412],"object_pos_start":[0.50778,-0.05978,0.03684],"object_to_goal_dist_end":0.01809,"object_to_goal_dist_start":0.0219,"object_z_max":0.03875,"peak_contact_force":0.55812,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1053.0,"raw_peak_contact_force":386.14097,"tcp_end":[0.4842,-0.03282,0.06587],"tcp_start":[0.48677,-0.03319,0.02552],"tcp_to_object_dist_end":0.05953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75694,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":0.01907,"approach_peg.approach_offset_y":0.03132,"approach_peg.approach_offset_z":0.12865,"approach_peg.pose_tolerance":0.03752,"contact_peg.approach_offset_x":0.00697,"contact_peg.contact_offset_y":0.01513,"contact_peg.contact_offset_z":0.01241,"contact_peg.force_threshold":15.09547,"descend_to_peg.approach_offset_x":0.0047,"descend_to_peg.approach_offset_y":0.07616,"descend_to_peg.descend_offset_z":0.01962,"descend_to_peg.pose_tolerance":0.03298,"push_phase.max_time":2.0034,"push_phase.push_distance":0.17914,"push_phase.push_speed":0.09889,"push_phase.retry_offset_x":-0.00012,"push_phase.retry_offset_y":0.00633},"optimized_scores":{"best_composite_score":-0.47431,"best_fitness_score":0.46569,"best_task_score":0.29636},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":121.0,"contact_point_centroid":[0.54922,-0.1,0.06498],"force_p95":192.0629,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.81574,"mean_force":112.56601,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49536,-0.0533,0.02574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.49415,-0.10141,0.02616],"force_p95":67.62997,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.60902,"mean_force":33.17539,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.4962,-0.05547,0.02591]},{"body_a":"attachment","body_b":"peg","contact_count":865.0,"contact_point_centroid":[0.49418,0.00083,0.03727],"force_p95":28.8591,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.54833,"mean_force":9.91847,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49398,0.01263,0.03463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49316,-0.10116,0.05559],"force_p95":32.60323,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.97131,"mean_force":27.49359,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49405,-0.05512,0.04693]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54905,-0.1,0.06496],"force_p95":54.55796,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.62336,"mean_force":44.55754,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49764,-0.05877,0.02614]},{"body_a":"attachment","body_b":"peg","contact_count":449.0,"contact_point_centroid":[0.49403,-0.06666,0.04936],"force_p95":32.55097,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.606,"mean_force":27.26736,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49404,-0.05511,0.04697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":810.0,"contact_point_centroid":[0.49338,-0.0199,0.0099],"force_p95":17.3005,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.20428,"mean_force":7.06401,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49385,0.01779,0.03534]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":64.0,"contact_point_centroid":[0.47493,-0.08626,0.04626],"force_p95":14.3959,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.21653,"mean_force":4.33502,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.4956,-0.05697,0.0329]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":157.0,"contact_point_centroid":[0.47497,0.01138,0.03663],"force_p95":9.82397,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.46046,"mean_force":3.44725,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49409,0.04,0.03877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.50249,0.05926,0.0089],"force_p95":3.59859,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":1.43709,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49463,0.17976,0.2871]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49776,0.19279,0.29537]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.49428,0.05894,0.00934],"force_p95":0.56943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69057,"mean_force":0.54394,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49443,0.17707,0.19607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.49413,0.05891,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54612,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49484,0.1358,0.075]}],"total_contact_groups":13},"final_pose_error":0.01073,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49352,-0.08118,0.05583],"final_tcp_position":[0.49401,-0.05407,0.06713],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":239.81574,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.49391,0.05896,0.03279],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.56593,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":52.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.49318,0.17333,0.28326],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.27535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.4941,0.05905,0.03384],"object_pos_start":[0.49391,0.05896,0.03279],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.13928,"object_z_max":0.03384,"peak_contact_force":0.54908,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":232.0,"raw_peak_contact_force":0.69057,"subtask_id":"reach_contact","tcp_end":[0.49591,0.18219,0.10465],"tcp_start":[0.49318,0.17333,0.28326],"tcp_to_object_dist_end":0.14206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.4942,0.05912,0.03392],"object_pos_start":[0.4941,0.05905,0.03384],"object_to_goal_dist_end":0.13938,"object_to_goal_dist_start":0.13931,"object_z_max":0.03392,"peak_contact_force":0.54238,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":662.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_contact","tcp_end":[0.49699,0.08914,0.04959],"tcp_start":[0.49591,0.18219,0.10465],"tcp_to_object_dist_end":0.03398,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49336,-0.0873,0.03565],"object_pos_start":[0.4942,0.05912,0.03392],"object_to_goal_dist_end":0.01078,"object_to_goal_dist_start":0.13938,"object_z_max":0.03994,"peak_contact_force":100.47044,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2044.0,"raw_peak_contact_force":239.81574,"subtask_id":"push_complete","tcp_end":[0.49761,-0.0587,0.02611],"tcp_start":[0.49699,0.08914,0.04959],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.49352,-0.08118,0.05583],"object_pos_start":[0.49336,-0.0873,0.03565],"object_to_goal_dist_end":0.01714,"object_to_goal_dist_start":0.01078,"object_z_max":0.05579,"peak_contact_force":27.88608,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":968.0,"raw_peak_contact_force":55.97131,"tcp_end":[0.49401,-0.05407,0.06713],"tcp_start":[0.49761,-0.0587,0.02611],"tcp_to_object_dist_end":0.02938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75177,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_offset_x":-0.00958,"approach_peg.approach_offset_y":0.06222,"approach_peg.approach_offset_z":0.09859,"approach_peg.pose_tolerance":0.02685,"contact_peg.approach_offset_x":0.00021,"contact_peg.contact_offset_y":0.01057,"contact_peg.contact_offset_z":0.00998,"contact_peg.force_threshold":16.32999,"descend_to_peg.approach_offset_x":-0.01433,"descend_to_peg.approach_offset_y":0.07603,"descend_to_peg.descend_offset_z":0.02861,"descend_to_peg.pose_tolerance":0.04212,"push_phase.max_time":7.61624,"push_phase.push_distance":0.17704,"push_phase.push_speed":0.09882,"push_phase.retry_offset_x":-0.00026,"push_phase.retry_offset_y":-0.00063},"optimized_scores":{"best_composite_score":-0.54623,"best_fitness_score":0.39377,"best_task_score":0.30041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":165.0,"contact_point_centroid":[0.53645,-0.02353,0.05998],"force_p95":149.74482,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.48723,"mean_force":90.95691,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50061,-0.03031,0.02495]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53858,-0.03542,0.06],"force_p95":54.63676,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.92667,"mean_force":52.02761,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50301,-0.04243,0.02474]},{"body_a":"peg","body_b":"channel_base_body","contact_count":684.0,"contact_point_centroid":[0.50521,-0.00712,0.0099],"force_p95":14.32545,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.80036,"mean_force":6.95358,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49904,0.0358,0.03378]},{"body_a":"attachment","body_b":"peg","contact_count":796.0,"contact_point_centroid":[0.50284,0.024,0.04125],"force_p95":14.31785,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.34135,"mean_force":5.98611,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49887,0.03555,0.0336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":752.0,"contact_point_centroid":[0.50608,0.07997,0.00939],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.22133,"mean_force":0.8056,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49752,0.15458,0.08322]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50369,0.096,0.05003],"force_p95":12.08589,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.02579,"mean_force":8.75231,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50177,0.10784,0.04913]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":499.0,"contact_point_centroid":[0.52512,-0.01462,0.02907],"force_p95":6.20023,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.05077,"mean_force":1.7656,"phase_index":3.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49876,0.01364,0.03018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50247,0.08067,0.00909],"force_p95":2.941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.92393,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50889,0.19713,0.2748]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50246,0.19914,0.29328]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.52509,-0.07453,0.04011],"force_p95":0.44408,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16679,"mean_force":0.18258,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50037,-0.04222,0.03905]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50828,-0.05445,0.06067],"force_p95":1.89188,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.16086,"mean_force":0.71258,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50301,-0.04242,0.02475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.5056,-0.07516,0.00944],"force_p95":0.63099,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02392,"mean_force":0.54308,"phase_index":4.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49962,-0.0421,0.0455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":148.0,"contact_point_centroid":[0.50605,0.08091,0.00937],"force_p95":0.55935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56764,"mean_force":0.54538,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50566,0.19897,0.19532]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50697,-0.07452,0.0338],"final_tcp_position":[0.49935,-0.04204,0.06552],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":160.48723,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":70.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08087,0.03361],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.52755,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":77.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.51348,0.19569,0.26218],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50597,0.08087,0.03361],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54876,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":148.0,"raw_peak_contact_force":0.56764,"subtask_id":"reach_contact","tcp_end":[0.49646,0.20324,0.12323],"tcp_start":[0.51348,0.19569,0.26218],"tcp_to_object_dist_end":0.15188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.50617,0.07745,0.03621],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.15762,"object_to_goal_dist_start":0.1611,"object_z_max":0.03619,"peak_contact_force":7.81268,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":775.0,"raw_peak_contact_force":14.22133,"subtask_id":"reach_contact","tcp_end":[0.50196,0.10615,0.04788],"tcp_start":[0.49646,0.20324,0.12323],"tcp_to_object_dist_end":0.03126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50757,-0.07232,0.03599],"object_pos_start":[0.50617,0.07745,0.03621],"object_to_goal_dist_end":0.0115,"object_to_goal_dist_start":0.15762,"object_z_max":0.03958,"peak_contact_force":1.41381,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2144.0,"raw_peak_contact_force":160.48723,"subtask_id":"push_complete","tcp_end":[0.50301,-0.04232,0.02475],"tcp_start":[0.50196,0.10615,0.04788],"tcp_to_object_dist_end":0.03236,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50697,-0.07452,0.0338],"object_pos_start":[0.50757,-0.07232,0.03599],"object_to_goal_dist_end":0.01082,"object_to_goal_dist_start":0.0115,"object_z_max":0.03599,"peak_contact_force":0.53636,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":534.0,"raw_peak_contact_force":54.92667,"tcp_end":[0.49935,-0.04204,0.06552],"tcp_start":[0.50301,-0.04232,0.02475],"tcp_to_object_dist_end":0.04604,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```