## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0700 | 1.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0578 | 0.99 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0700 | 1.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0700 | 1.00 | ✅ accepted |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 0.6537 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`
- Frozen initial hinge angle: -0.060 rad
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
  frozen_initial_hinge_angle_rad: -0.0604
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09

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

## Current Skill (Q=1.070) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_door
  anchor: fixture
  offset:
  - -0.45
  - -0.02
  - 0.35
  weight: 0.2
- id: open_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.8
phases:
- id: pre_approach
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
    - 0.1
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.008
      - 0.025
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_door
- id: descend_to_handle
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: approach_door
- id: push_open
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
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 25.0
      - 30.0
      default: 28.0
      binds_to:
      - path: guards.force_limit_check.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 3.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit_check
    when: during_phase
    predicate: force_below
    threshold: 28.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **pre_approach** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_limit_check.threshold (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit_check, when=during_phase, predicate=force_below, on_failure=abort, threshold=28.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 1.070
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_approach | 1.00 | 1.00 | 0.2568 |
| descend_to_handle | 1.00 | 1.00 | 0.0012 |
| push_open | 1.00 | 1.00 | 0.1441 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.104, 0.163, 0.448) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 10.460 | 51.840 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.104, 0.163, 0.448)→(0.104, 0.162, 0.447) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 14.463 | 16.077 |
| push_open | push | 1.00 / time_limit | (0.104, 0.162, 0.447)→(0.104, 0.018, 0.445) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 7.374 | 26.471 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.070
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.465


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22222,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_handle.contact_threshold":5.21327,"pre_approach.approach_height":0.11134,"pre_approach.approach_speed":0.19814,"pre_approach.approach_tolerance":0.01642,"push_open.force_guard_threshold":27.65982,"push_open.max_time":5.0309,"push_open.push_distance":0.23075,"push_open.push_speed":0.08177},"optimized_scores":{"best_composite_score":1.07,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":172.0,"contact_point_centroid":[0.10082,0.18704,0.53347],"force_p95":34.69012,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.34131,"mean_force":20.65927,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.09949,0.26064,0.42636]},{"body_a":"door_panel","body_b":"link7","contact_count":808.0,"contact_point_centroid":[0.16474,0.09207,0.47419],"force_p95":19.00579,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.53659,"mean_force":13.21967,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.0991,0.14923,0.44947]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.1646,0.1577,0.47537],"force_p95":17.63456,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.63456,"mean_force":17.63456,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.0993,0.21511,0.45143]},{"body_a":"world","body_b":"door_panel","contact_count":568.0,"contact_point_centroid":[0.30023,0.19329,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.09969,0.30738,0.39974]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.1031,0.1504,0.55672],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09942,0.21585,0.45222]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.3028,0.1652,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09936,0.21566,0.45207]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.31363,0.12993,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09909,0.14855,0.44948]}],"total_contact_groups":7},"final_pose_error":0.09616,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09907,0.08038,0.44944],"hinge_angle":0.48562,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":71.34131,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":576.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.5957,"phase_name":"pre_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":71.34131,"subtask_id":"approach_door","tcp_end":[0.09942,0.21585,0.45222],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":9.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.63456,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":17.63456,"subtask_id":"approach_door","tcp_end":[0.09931,0.21499,0.45127],"tcp_start":[0.09942,0.21585,0.45222],"tcp_to_object_dist_end":0.50963,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.5508,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1736.0,"raw_peak_contact_force":25.53659,"subtask_id":"open_door","tcp_end":[0.09907,0.08038,0.44944],"tcp_start":[0.09931,0.21499,0.45127],"tcp_to_object_dist_end":0.4672,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24615,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_handle.contact_threshold":6.47799,"pre_approach.approach_height":0.09331,"pre_approach.approach_speed":0.23268,"pre_approach.approach_tolerance":0.01513,"push_open.force_guard_threshold":28.52525,"push_open.max_time":6.78368,"push_open.push_distance":0.28596,"push_open.push_speed":0.08857},"optimized_scores":{"best_composite_score":1.07,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.10391,0.14474,0.51774],"force_p95":28.56014,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.07302,"mean_force":14.56134,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10421,0.21281,0.41222]},{"body_a":"door_panel","body_b":"link7","contact_count":160.0,"contact_point_centroid":[0.17027,0.11679,0.44924],"force_p95":29.4773,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33704,"mean_force":16.7409,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10498,0.17423,0.42544]},{"body_a":"door_panel","body_b":"link7","contact_count":720.0,"contact_point_centroid":[0.17318,0.01642,0.46047],"force_p95":21.37029,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.78671,"mean_force":13.4768,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10558,0.07185,0.43426]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17103,0.08397,0.46011],"force_p95":13.26307,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.96112,"mean_force":6.98056,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10572,0.14145,0.43641]},{"body_a":"world","body_b":"door_panel","contact_count":704.0,"contact_point_centroid":[0.30406,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.1026,0.28141,0.38836]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.31472,0.12404,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10563,0.14165,0.43668]},{"body_a":"world","body_b":"door_panel","contact_count":776.0,"contact_point_centroid":[0.33088,0.09451,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10558,0.07142,0.4343]}],"total_contact_groups":7},"final_pose_error":0.14084,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10558,-0.00419,0.43433],"hinge_angle":0.65636,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":45.07302,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":696.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"pre_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":891.0,"raw_peak_contact_force":45.07302,"subtask_id":"approach_door","tcp_end":[0.10569,0.14182,0.4367],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":8.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.11771,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":13.96112,"subtask_id":"approach_door","tcp_end":[0.10577,0.14094,0.43597],"tcp_start":[0.10569,0.14182,0.4367],"tcp_to_object_dist_end":0.47024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.57219,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1496.0,"raw_peak_contact_force":26.78671,"subtask_id":"open_door","tcp_end":[0.10558,-0.00419,0.43433],"tcp_start":[0.10577,0.14094,0.43597],"tcp_to_object_dist_end":0.447,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.3,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_handle.contact_threshold":6.03724,"pre_approach.approach_height":0.11155,"pre_approach.approach_speed":0.20327,"pre_approach.approach_tolerance":0.01957,"push_open.force_guard_threshold":28.80805,"push_open.max_time":3.8468,"push_open.push_distance":0.1713,"push_open.push_speed":0.09496},"optimized_scores":{"best_composite_score":1.07,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":188.0,"contact_point_centroid":[0.17204,0.1106,0.46294],"force_p95":28.8772,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.10653,"mean_force":16.89252,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10673,0.16802,0.43917]},{"body_a":"door_panel","body_b":"link7","contact_count":722.0,"contact_point_centroid":[0.17678,0.00308,0.47788],"force_p95":19.58013,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.09041,"mean_force":13.074,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10769,0.05628,0.45173]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17317,0.07214,0.47764],"force_p95":15.80419,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.63599,"mean_force":8.318,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10784,0.12957,0.45395]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10491,0.13782,0.52997],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10577,0.20521,0.42466]},{"body_a":"world","body_b":"door_panel","contact_count":808.0,"contact_point_centroid":[0.30563,0.15325,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10367,0.27305,0.39756]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.31739,0.11782,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10775,0.12977,0.45426]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.33415,0.08939,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10769,0.05826,0.45177]}],"total_contact_groups":7},"final_pose_error":0.01891,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10769,-0.02338,0.45181],"hinge_angle":0.68516,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":39.10653,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.7851,"phase_name":"pre_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":39.10653,"subtask_id":"approach_door","tcp_end":[0.1078,0.12996,0.45435],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":9.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.63599,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":16.63599,"subtask_id":"approach_door","tcp_end":[0.1079,0.12907,0.45341],"tcp_start":[0.1078,0.12996,0.45435],"tcp_to_object_dist_end":0.48361,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1570.0,"raw_peak_contact_force":27.09041,"subtask_id":"open_door","tcp_end":[0.10769,-0.02338,0.45181],"tcp_start":[0.1079,0.12907,0.45341],"tcp_to_object_dist_end":0.46506,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```