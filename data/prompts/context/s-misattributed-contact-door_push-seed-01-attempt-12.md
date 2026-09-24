## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ✅ accepted |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 1.0033 | 1.00 | ✅ accepted |
| 10 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | time_limit | 3 | 0.8500 | 1.00 | ✅ accepted |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.6700 | 1.00 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.3197 | 0.60 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`
- Frozen initial hinge angle: 0.004 rad
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
  frozen_initial_hinge_angle_rad: 0.0041
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91

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

## Current Skill (Q=1.120) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_sub
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.45
  weight: 0.3
- id: push_sub
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.45
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_sub
- id: contact_handle
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.2
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_sub
- id: push_door
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    offset_along_axis:
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.2
  parameters:
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
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_sub

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.45], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **contact_handle** (`descend`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.2
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}, tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.2
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 1.120
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2330 |
| contact_handle | 1.00 | 1.00 | 0.0048 |
| push_door | 1.00 | 0.33 | 0.1342 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.195, 0.463) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 1361.083 | 61.086 |
| contact_handle | descend | 1.00 / force_exceeded | (0.100, 0.195, 0.463)→(0.100, 0.192, 0.459) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 626.780 | 536.304 |
| push_door | push | 1.00 / time_limit | (0.100, 0.192, 0.459)→(0.149, 0.083, 0.402) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 37.579 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.262


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `083132501f1ba139cf05fa7994a1ee954b157d46058e9396ba8b78c93b367725`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a0caaf91521131af8da2ca1e0ce4fb631dc10b8d496fc3757eb1acd97f543da3`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.00413,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.43617,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.09093,"approach_handle.arc_height":0.10386,"contact_handle.contact_force_threshold":8.77712,"contact_handle.descend_speed":0.0569,"push_door.push_distance":0.29912,"push_door.push_speed":0.0968,"push_door.push_timeout":11.55334},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link6","contact_count":160.0,"contact_point_centroid":[0.10265,0.00682,0.37825],"force_p95":482.1039,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":589.26117,"mean_force":335.8438,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12283,0.08999,0.39474]},{"body_a":"door_panel","body_b":"link6","contact_count":50.0,"contact_point_centroid":[0.13135,0.05112,0.60808],"force_p95":390.20055,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":404.14428,"mean_force":200.26605,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.02376,0.17592,0.56465]},{"body_a":"door_panel","body_b":"link5","contact_count":430.0,"contact_point_centroid":[0.18087,-0.03821,0.52862],"force_p95":214.70709,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":363.0116,"mean_force":120.44471,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10933,0.12112,0.42633]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.14082,0.10926,0.48856],"force_p95":74.93918,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.11266,"mean_force":31.28949,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09733,0.18345,0.45776]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.13602,0.12003,0.50065],"force_p95":55.20392,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.20392,"mean_force":55.20392,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09996,0.19412,0.46401]},{"body_a":"door_panel","body_b":"link7","contact_count":144.0,"contact_point_centroid":[0.13922,0.16075,0.52379],"force_p95":33.82006,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.07152,"mean_force":17.51507,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1,0.23419,0.48934]},{"body_a":"world","body_b":"door_panel","contact_count":816.0,"contact_point_centroid":[0.30074,0.18381,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1001,0.33376,0.45311]},{"body_a":"world","body_b":"door_panel","contact_count":856.0,"contact_point_centroid":[0.3394,0.08307,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10318,0.13651,0.45816]}],"total_contact_groups":8},"final_pose_error":0.19394,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.14419,0.06444,0.39433],"hinge_angle":0.88996,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":3994.93886,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3994.93886,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":55.20392,"subtask_id":"approach_sub","tcp_end":[0.09996,0.19412,0.46401],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1371.42901,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":589.26117,"subtask_id":"approach_sub","tcp_end":[0.09996,0.19261,0.4622],"tcp_start":[0.09996,0.19412,0.46401],"tcp_to_object_dist_end":0.51061,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":960.0,"raw_peak_contact_force":35.07152,"subtask_id":"push_sub","tcp_end":[0.14419,0.06444,0.39433],"tcp_start":[0.09996,0.19261,0.4622],"tcp_to_object_dist_end":0.42478,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.27397,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.15487,"approach_handle.arc_height":0.08492,"contact_handle.contact_force_threshold":9.07646,"contact_handle.descend_speed":0.05455,"push_door.push_distance":0.16362,"push_door.push_speed":0.08365,"push_door.push_timeout":6.58108},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link6","contact_count":156.0,"contact_point_centroid":[0.11308,-0.00514,0.37153],"force_p95":548.15007,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":608.16219,"mean_force":363.24744,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1626,0.07854,0.37356]},{"body_a":"door_panel","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.13467,0.04319,0.59289],"force_p95":395.3313,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":421.39493,"mean_force":174.31227,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.04183,0.17985,0.54941]},{"body_a":"door_panel","body_b":"link5","contact_count":471.0,"contact_point_centroid":[0.18506,-0.04036,0.53917],"force_p95":219.89349,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":312.3737,"mean_force":130.80529,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14846,0.12021,0.43371]},{"body_a":"door_panel","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.14041,0.1123,0.48741],"force_p95":65.20006,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.05895,"mean_force":37.67131,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09783,0.18601,0.45535]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.13655,0.1228,0.49824],"force_p95":63.05653,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.05653,"mean_force":63.05653,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10006,0.19599,0.46042]},{"body_a":"door_panel","body_b":"link7","contact_count":189.0,"contact_point_centroid":[0.14158,0.1781,0.51528],"force_p95":32.65455,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.68121,"mean_force":16.80828,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10009,0.24959,0.47941]},{"body_a":"world","body_b":"door_panel","contact_count":696.0,"contact_point_centroid":[0.3004,0.19795,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10017,0.32921,0.44459]},{"body_a":"world","body_b":"door_panel","contact_count":816.0,"contact_point_centroid":[0.34199,0.08055,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12872,0.13731,0.46505]}],"total_contact_groups":8},"final_pose_error":0.08526,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.17423,0.05561,0.36484],"hinge_angle":0.9446,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":608.16219,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":626.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":36.73829,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":63.05653,"subtask_id":"approach_sub","tcp_end":[0.10006,0.19646,0.46083],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":338.19691,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1500.0,"raw_peak_contact_force":608.16219,"subtask_id":"approach_sub","tcp_end":[0.10005,0.19544,0.45989],"tcp_start":[0.10006,0.19646,0.46083],"tcp_to_object_dist_end":0.50961,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":885.0,"raw_peak_contact_force":42.68121,"subtask_id":"push_sub","tcp_end":[0.17423,0.05561,0.36484],"tcp_start":[0.10005,0.19544,0.45989],"tcp_to_object_dist_end":0.40811,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.48936,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.09939,"approach_handle.arc_height":0.09531,"contact_handle.contact_force_threshold":8.01393,"contact_handle.descend_speed":0.04146,"push_door.push_distance":0.26253,"push_door.push_speed":0.03851,"push_door.push_timeout":7.26364},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.13495,0.04254,0.5894],"force_p95":398.43725,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":411.48864,"mean_force":165.0207,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.04426,0.18163,0.5486]},{"body_a":"door_panel","body_b":"link5","contact_count":316.0,"contact_point_centroid":[0.16159,-0.01308,0.55834],"force_p95":205.3226,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":249.60881,"mean_force":155.70586,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11637,0.13602,0.44972]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.1369,0.11875,0.49597],"force_p95":64.85406,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.99843,"mean_force":60.84437,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09993,0.1926,0.45985]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.14153,0.10888,0.48651],"force_p95":40.13393,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.13426,"mean_force":29.03936,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09728,0.18298,0.45567]},{"body_a":"door_panel","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.14122,0.17976,0.52226],"force_p95":26.8594,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.98292,"mean_force":16.34923,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10004,0.25191,0.48692]},{"body_a":"world","body_b":"door_panel","contact_count":664.0,"contact_point_centroid":[0.30074,0.19785,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10006,0.32459,0.45214]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30694,0.14682,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09995,0.19295,0.46022]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.33207,0.09216,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10492,0.15339,0.48653]}],"total_contact_groups":8},"final_pose_error":0.23425,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12969,0.12914,0.44585],"hinge_angle":0.58425,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":411.48864,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":51.57258,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12.0,"raw_peak_contact_force":64.99843,"subtask_id":"approach_sub","tcp_end":[0.1,0.19517,0.46272],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":170.71425,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1249.0,"raw_peak_contact_force":411.48864,"subtask_id":"approach_sub","tcp_end":[0.09929,0.18746,0.45523],"tcp_start":[0.1,0.19517,0.46272],"tcp_to_object_dist_end":0.50223,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":880.0,"raw_peak_contact_force":34.98292,"subtask_id":"push_sub","tcp_end":[0.12969,0.12914,0.44585],"tcp_start":[0.09929,0.18746,0.45523],"tcp_to_object_dist_end":0.48196,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```