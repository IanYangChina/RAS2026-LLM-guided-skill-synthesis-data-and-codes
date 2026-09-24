## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

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

- Task name: door_push
- Frozen realised-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`
- Frozen initial hinge angle: 0.129 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.1292
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=1.132) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_target
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.48
  weight: 0.3
- id: push_hinge
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.13
    tolerance: 0.015
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    approach_offset_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    approach_offset_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
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
    approach_z:
      type: scalar
      range:
      - 0.1
      - 0.16
      default: 0.13
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_target
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_z:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_target
- id: push_door_open
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
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    force_threshold:
      type: scalar
      range:
      - 20.0
      - 30.0
      default: 30.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
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
    push_time:
      type: scalar
      range:
      - 4.0
      - 18.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.03
      default: 0.01
      binds_to:
      - path: retry.offset.x
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_hinge

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.13], tolerance=0.015
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - approach_offset_x: status=consumed; consumers=target.offset.x (replace)
    - approach_offset_y: status=consumed; consumers=target.offset.y (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - push_z: status=consumed; consumers=target.offset.z (replace)
- **push_door_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=guards.force_limit.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 1.132
- **task_score** (E): 0.712
- **fitness_score**: 0.712  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 0.67 | 0.1160 |
| descend_to_contact | 1.00 | 1.00 | 0.0572 |
| push_door_open | 1.00 | 0.33 | 0.1361 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.107, 0.298, 0.405) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 4.154 | 9.414 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.107, 0.298, 0.405)→(0.106, 0.243, 0.388) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 19.363 | 5.986 |
| push_door_open | push | 1.00 / time_limit | (0.106, 0.243, 0.388)→(0.106, 0.108, 0.400) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 27.836 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.916
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.916
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.916
- **Median Q (composite search score)**: 1.045
- **K-run variance**: 0.0211
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.350


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d324a70682be50916187e25da5a0a59a7678607fbe49b53fdc39aa246f41ddf9`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d82b7d31aa43f8d3a4479d5f34069ef44e70dc4ca62021414a1e013fa43805ad`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78947,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_x":0.02047,"approach_handle.approach_offset_y":0.01971,"approach_handle.approach_speed":0.06146,"approach_handle.approach_z":0.13771,"descend_to_contact.contact_force":6.94197,"descend_to_contact.push_z":0.0009,"push_door_open.force_threshold":29.97521,"push_door_open.push_distance":0.21723,"push_door_open.push_speed":0.07467,"push_door_open.push_time":14.74904,"push_door_open.retry_offset_x":-0.0021},"optimized_scores":{"best_composite_score":1.04514,"best_fitness_score":0.62514,"best_task_score":0.62514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":665.0,"contact_point_centroid":[0.17237,0.09324,0.4],"force_p95":19.32484,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.77925,"mean_force":13.69484,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10685,0.15036,0.37516]},{"body_a":"door_panel","body_b":"link6","contact_count":95.0,"contact_point_centroid":[0.10393,0.14447,0.47887],"force_p95":14.71305,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.79529,"mean_force":8.3122,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10681,0.21432,0.37153]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10295,0.15189,0.48084],"force_p95":8.3685,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.40458,"mean_force":8.1893,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10705,0.22426,0.37299]},{"body_a":"world","body_b":"door_panel","contact_count":1100.0,"contact_point_centroid":[0.30285,0.16488,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10417,0.35431,0.37152]},{"body_a":"world","body_b":"door_panel","contact_count":536.0,"contact_point_centroid":[0.3027,0.16576,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10789,0.26913,0.38448]},{"body_a":"world","body_b":"door_panel","contact_count":1024.0,"contact_point_centroid":[0.31279,0.13187,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10686,0.15547,0.37504]}],"total_contact_groups":6},"final_pose_error":0.09223,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10689,0.0964,0.39425],"hinge_angle":0.45682,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.77925,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_target","tcp_end":[0.10897,0.30902,0.39639],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51429,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.40458,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":540.0,"raw_peak_contact_force":8.40458,"subtask_id":"approach_target","tcp_end":[0.10703,0.22391,0.3729],"tcp_start":[0.10897,0.30902,0.39639],"tcp_to_object_dist_end":0.44794,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1784.0,"raw_peak_contact_force":29.77925,"subtask_id":"push_hinge","tcp_end":[0.10689,0.0964,0.39425],"tcp_start":[0.10703,0.22391,0.3729],"tcp_to_object_dist_end":0.41971,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80208,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_x":0.00562,"approach_handle.approach_offset_y":0.02973,"approach_handle.approach_speed":0.07629,"approach_handle.approach_z":0.13787,"descend_to_contact.contact_force":8.93098,"descend_to_contact.push_z":0.00297,"push_door_open.force_threshold":29.71979,"push_door_open.push_distance":0.1368,"push_door_open.push_speed":0.06505,"push_door_open.push_time":8.89995,"push_door_open.retry_offset_x":0.00724},"optimized_scores":{"best_composite_score":1.01358,"best_fitness_score":0.59358,"best_task_score":0.59358},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":733.0,"contact_point_centroid":[0.1717,0.09141,0.40555],"force_p95":19.23824,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.03105,"mean_force":13.51444,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10611,0.14853,0.3807]},{"body_a":"door_panel","body_b":"link6","contact_count":21.0,"contact_point_centroid":[0.10472,0.13894,0.48626],"force_p95":15.03746,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.55376,"mean_force":6.55461,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10622,0.20702,0.37983]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10443,0.14081,0.48709],"force_p95":9.45661,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.55216,"mean_force":8.71422,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10631,0.20962,0.38058]},{"body_a":"world","body_b":"door_panel","contact_count":1048.0,"contact_point_centroid":[0.30397,0.1591,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10245,0.34607,0.37592]},{"body_a":"world","body_b":"door_panel","contact_count":504.0,"contact_point_centroid":[0.30374,0.1602,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10585,0.24924,0.39353]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.31381,0.12904,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10612,0.14931,0.38114]}],"total_contact_groups":6},"final_pose_error":0.02306,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10614,0.09048,0.39493],"hinge_angle":0.47021,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.03105,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_target","tcp_end":[0.1057,0.28787,0.40773],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51018,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.55216,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":508.0,"raw_peak_contact_force":9.55216,"subtask_id":"approach_target","tcp_end":[0.10631,0.20931,0.38049],"tcp_start":[0.1057,0.28787,0.40773],"tcp_to_object_dist_end":0.44708,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1622.0,"raw_peak_contact_force":27.03105,"subtask_id":"push_hinge","tcp_end":[0.10614,0.09048,0.39493],"tcp_start":[0.10631,0.20931,0.38049],"tcp_to_object_dist_end":0.41884,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.12965,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_x":0.00913,"approach_handle.approach_offset_y":-0.01387,"approach_handle.approach_speed":0.07297,"approach_handle.approach_z":0.11501,"descend_to_contact.contact_force":4.33081,"descend_to_contact.push_z":-0.00159,"push_door_open.force_threshold":27.03723,"push_door_open.push_distance":0.21649,"push_door_open.push_speed":0.09709,"push_door_open.push_time":12.44191,"push_door_open.retry_offset_x":7e-05},"optimized_scores":{"best_composite_score":1.336,"best_fitness_score":0.916,"best_task_score":0.916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":178.0,"contact_point_centroid":[0.10093,0.22596,0.51716],"force_p95":16.34609,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.24063,"mean_force":13.55473,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10421,0.31072,0.40273]},{"body_a":"door_panel","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.17018,0.11628,0.43409],"force_p95":18.80103,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.69635,"mean_force":13.80184,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10482,0.17353,0.41006]},{"body_a":"door_panel","body_b":"link6","contact_count":474.0,"contact_point_centroid":[0.1013,0.17614,0.51895],"force_p95":11.95461,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.11417,"mean_force":7.66306,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10469,0.25195,0.40991]},{"body_a":"world","body_b":"door_panel","contact_count":944.0,"contact_point_centroid":[0.29994,0.2077,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10235,0.34656,0.38013]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10019,0.21235,0.5251],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10501,0.29613,0.41203]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.29979,0.19615,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10503,0.29612,0.41203]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.30508,0.16011,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10475,0.21383,0.40998]}],"total_contact_groups":7},"final_pose_error":0.05719,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10481,0.13662,0.41006],"hinge_angle":0.35033,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":40.13312,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.46198,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1122.0,"raw_peak_contact_force":28.24063,"subtask_id":"approach_target","tcp_end":[0.10501,0.29613,0.41203],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51816,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":40.13312,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_target","tcp_end":[0.10503,0.29595,0.41191],"tcp_start":[0.10501,0.29613,0.41203],"tcp_to_object_dist_end":0.51796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1763.0,"raw_peak_contact_force":26.69635,"subtask_id":"push_hinge","tcp_end":[0.10481,0.13662,0.41006],"tcp_start":[0.10503,0.29595,0.41191],"tcp_to_object_dist_end":0.44475,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```