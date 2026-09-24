## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 6 | 1.6700 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 6 | 1.6700 | 1.00 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 6 | 1.6700 | 1.00 | ❌ rejected |
| 7 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |

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

## Current Skill (Q=1.670) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.3
- id: open_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - -0.05
    - 0.0
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    approach_timeout:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: reach_handle
- id: contact_1
  type: contact
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
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_handle
- id: push_1
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
      distance: 0.4
      axis: world_y
      mode: add_to_offset
      sign: negative
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.4
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_lateral_x:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.x
        mode: add
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.05, 0.0], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_timeout: status=consumed; consumers=duration.max_time (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.4, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_x: status=consumed; consumers=target.offset.x (add)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.02, 0.0]

## Design Metrics

- **Composite score**: 1.670
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.67 | 0.2288 |
| contact_1 | 1.00 | 1.00 | 0.0010 |
| push_1 | 1.00 | 1.00 | 0.1372 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.100, 0.171, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 8.751 | 40.294 |
| contact_1 | contact | 1.00 / force_exceeded | (0.100, 0.171, 0.349)→(0.100, 0.170, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 15.830 | 16.485 |
| push_1 | push | 1.00 / time_limit | (0.100, 0.170, 0.349)→(0.136, 0.038, 0.350) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 9.116 | 31.520 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.670
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24194,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.23225,"approach_1.approach_timeout":3.82809,"contact_1.contact_force_threshold":11.54673,"push_1.push_distance":0.12979,"push_1.push_lateral_x":0.04671,"push_1.push_speed":0.08378},"optimized_scores":{"best_composite_score":1.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":271.0,"contact_point_centroid":[0.14766,0.14216,0.39841],"force_p95":29.47835,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.08743,"mean_force":15.51288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10016,0.20002,0.3487]},{"body_a":"door_panel","body_b":"link7","contact_count":781.0,"contact_point_centroid":[0.18361,0.02494,0.38396],"force_p95":17.66571,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.97711,"mean_force":13.93271,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.12274,0.07788,0.34798]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.14187,0.08276,0.40255],"force_p95":16.94132,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.30713,"mean_force":10.31873,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10035,0.1413,0.34885]},{"body_a":"world","body_b":"door_panel","contact_count":760.0,"contact_point_centroid":[0.30165,0.17881,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09987,0.2838,0.34829]},{"body_a":"world","body_b":"door_panel","contact_count":876.0,"contact_point_centroid":[0.32885,0.09836,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1204,0.08429,0.3479]}],"total_contact_groups":5},"final_pose_error":0.00692,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1463,0.01738,0.35128],"hinge_angle":0.6895,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":42.08743,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.88644,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1031.0,"raw_peak_contact_force":42.08743,"subtask_id":"reach_handle","tcp_end":[0.10035,0.14154,0.34891],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.38967,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.30713,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":17.30713,"subtask_id":"reach_handle","tcp_end":[0.10045,0.14078,0.34876],"tcp_start":[0.10035,0.14154,0.34891],"tcp_to_object_dist_end":0.38928,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.3781,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1657.0,"raw_peak_contact_force":30.97711,"subtask_id":"open_door","tcp_end":[0.1463,0.01738,0.35128],"tcp_start":[0.10045,0.14078,0.34876],"tcp_to_object_dist_end":0.38092,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60759,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.18713,"approach_1.approach_timeout":3.75197,"contact_1.contact_force_threshold":12.62608,"push_1.push_distance":0.20801,"push_1.push_lateral_x":0.05995,"push_1.push_speed":0.05192},"optimized_scores":{"best_composite_score":1.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":59.0,"contact_point_centroid":[0.10095,0.22664,0.47121],"force_p95":19.94408,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.14974,"mean_force":10.55351,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09942,0.28366,0.348]},{"body_a":"door_panel","body_b":"link7","contact_count":306.0,"contact_point_centroid":[0.14914,0.16923,0.3959],"force_p95":21.82461,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.73308,"mean_force":14.27332,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09958,0.22678,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":793.0,"contact_point_centroid":[0.16883,0.06146,0.38982],"force_p95":20.0691,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.30721,"mean_force":13.19646,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11547,0.11643,0.3472]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14507,0.11491,0.39982],"force_p95":13.07132,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.11245,"mean_force":12.70113,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09984,0.17293,0.34861]},{"body_a":"world","body_b":"door_panel","contact_count":764.0,"contact_point_centroid":[0.30072,0.19426,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09955,0.30074,0.34813]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30782,0.14371,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09981,0.17311,0.34864]},{"body_a":"world","body_b":"door_panel","contact_count":896.0,"contact_point_centroid":[0.31983,0.11456,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11498,0.11817,0.34721]}],"total_contact_groups":7},"final_pose_error":0.09993,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13146,0.06047,0.34713],"hinge_angle":0.56836,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.14974,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":779.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1129.0,"raw_peak_contact_force":37.14974,"subtask_id":"reach_handle","tcp_end":[0.09975,0.17372,0.34879],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40222,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.11245,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":13.11245,"subtask_id":"reach_handle","tcp_end":[0.09988,0.17267,0.34858],"tcp_start":[0.09975,0.17372,0.34879],"tcp_to_object_dist_end":0.40162,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1689.0,"raw_peak_contact_force":24.30721,"subtask_id":"open_door","tcp_end":[0.13146,0.06047,0.34713],"tcp_start":[0.09988,0.17267,0.34858],"tcp_to_object_dist_end":0.37608,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27941,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15649,"approach_1.approach_timeout":4.58017,"contact_1.contact_force_threshold":12.81975,"push_1.push_distance":0.37315,"push_1.push_lateral_x":0.06637,"push_1.push_speed":0.1006},"optimized_scores":{"best_composite_score":1.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":115.0,"contact_point_centroid":[0.10116,0.22894,0.47135],"force_p95":19.97524,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.64441,"mean_force":12.06288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1001,0.28811,0.34793]},{"body_a":"door_panel","body_b":"link7","contact_count":785.0,"contact_point_centroid":[0.16903,0.06102,0.38845],"force_p95":18.44832,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.27605,"mean_force":14.11845,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11473,0.11651,0.34719]},{"body_a":"door_panel","body_b":"link7","contact_count":298.0,"contact_point_centroid":[0.15099,0.17856,0.3949],"force_p95":16.20869,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.59967,"mean_force":13.16929,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10067,0.23626,0.34832]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.14799,0.13777,0.3989],"force_p95":18.83808,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.03453,"mean_force":12.03484,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10109,0.19598,0.34846]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.30063,0.19501,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10025,0.29328,0.34813]},{"body_a":"world","body_b":"door_panel","contact_count":996.0,"contact_point_centroid":[0.31952,0.11709,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11366,0.12247,0.34714]}],"total_contact_groups":6},"final_pose_error":0.21568,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13104,0.03465,0.3512],"hinge_angle":0.62953,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":41.64441,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":831.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.36658,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1233.0,"raw_peak_contact_force":41.64441,"subtask_id":"reach_handle","tcp_end":[0.10109,0.19629,0.34855],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4126,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.06999,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":19.03453,"subtask_id":"reach_handle","tcp_end":[0.10111,0.19524,0.34831],"tcp_start":[0.10109,0.19629,0.34855],"tcp_to_object_dist_end":0.4119,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.97124,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1781.0,"raw_peak_contact_force":39.27605,"subtask_id":"open_door","tcp_end":[0.13104,0.03465,0.3512],"tcp_start":[0.10111,0.19524,0.34831],"tcp_to_object_dist_end":0.37645,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```