## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | contact → push | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | time_limit | 5 | 1.4167 | 1.00 | ❌ rejected |
| 6 | contact → push | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | force_exceeded | time_limit | 5 | 1.7500 | 1.00 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 4 | 0.8000 | 1.00 | ✅ accepted |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | time_limit | time_limit | 5 | 0.7500 | 1.00 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.7200 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`
- Frozen initial hinge angle: -0.145 rad
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
  frozen_initial_hinge_angle_rad: -0.1446
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f

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

## Current Skill (Q=1.417) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: hinge_progress
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
phases:
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
    tolerance: 0.07
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: hinge_progress
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: hinge_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.07
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.417
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| contact_1 | 0.67 | 0.1384 |
| push_1 | 1.00 | 0.2615 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| contact_1 | contact | 0.67 / force_exceeded | (0.100, 0.399, 0.350)→(0.102, 0.261, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| push_1 | push | 1.00 / time_limit | (0.102, 0.261, 0.348)→(0.105, 0.006, 0.405) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.750
- **K-run variance**: 0.2222
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 5.0
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bba62da7f52483738d4dc6e46310e5298b0e0489aa689b981e86db9abdda203f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `789e053c0bcbffe7b16f252cc6b64c92268fc5193521b308e129f45c08e7a265`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37931,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_speed":0.08087,"contact_1.force_threshold":10.30457,"push_1.push_distance":0.32779,"push_1.push_max_time":17.39287,"push_1.push_speed":0.13725},"optimized_scores":{"best_composite_score":1.75,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.1651,0.1059,0.38716],"force_p95":22.20163,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.27838,"mean_force":15.18844,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09963,0.16302,0.3624]},{"body_a":"door_panel","body_b":"link6","contact_count":422.0,"contact_point_centroid":[0.101,0.19116,0.45457],"force_p95":19.06761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.2248,"mean_force":8.42268,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09972,0.26648,0.34637]},{"body_a":"door_panel","body_b":"link6","contact_count":38.0,"contact_point_centroid":[0.10175,0.237,0.4596],"force_p95":10.25704,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.82972,"mean_force":7.22694,"phase_index":0.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10013,0.32123,0.34766]},{"body_a":"world","body_b":"door_panel","contact_count":524.0,"contact_point_centroid":[0.3,0.21002,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09987,0.35825,0.34767]},{"body_a":"world","body_b":"door_panel","contact_count":944.0,"contact_point_centroid":[0.30558,0.16122,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09971,0.21455,0.35398]}],"total_contact_groups":5},"final_pose_error":0.22587,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09782,0.10703,0.40063],"hinge_angle":0.41934,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"hinge_progress","tcp_end":[0.10013,0.31868,0.34769],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48216,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"hinge_progress","tcp_end":[0.09782,0.10703,0.40063],"tcp_start":[0.10013,0.31868,0.34769],"tcp_to_object_dist_end":0.42606,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5a9939150766bec2b15bab1845f15dc59243da82175f4d23a01f9499c42cbd2f`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.5625,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_speed":0.14808,"contact_1.force_threshold":18.60969,"push_1.push_distance":0.38782,"push_1.push_max_time":8.38318,"push_1.push_speed":0.13591},"optimized_scores":{"best_composite_score":1.75,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10471,0.13916,0.4538],"force_p95":82.28273,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.6134,"mean_force":43.3067,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10516,0.20714,0.34837]},{"body_a":"door_panel","body_b":"link7","contact_count":712.0,"contact_point_centroid":[0.17201,0.04829,0.41396],"force_p95":22.22831,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.98745,"mean_force":14.43746,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10485,0.1025,0.38746]},{"body_a":"door_panel","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.10461,0.14016,0.45382],"force_p95":21.35825,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.67323,"mean_force":11.36108,"phase_index":0.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10517,0.20828,0.34831]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.30381,0.15986,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10227,0.3058,0.3481]},{"body_a":"world","body_b":"door_panel","contact_count":832.0,"contact_point_centroid":[0.32532,0.10778,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10485,0.0966,0.38992]}],"total_contact_groups":5},"final_pose_error":0.24453,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10908,-0.03111,0.40983],"hinge_angle":0.69873,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"hinge_progress","tcp_end":[0.1052,0.20716,0.34835],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41873,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"hinge_progress","tcp_end":[0.10908,-0.03111,0.40983],"tcp_start":[0.1052,0.20716,0.34835],"tcp_to_object_dist_end":0.42524,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `2f40317e91cda9d20f75f9f44171fa9a28a4706ede195f831595653d78bddc9d`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.09589,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_speed":0.08174,"contact_1.force_threshold":18.52442,"push_1.push_distance":0.2816,"push_1.push_max_time":10.25128,"push_1.push_speed":0.18428},"optimized_scores":{"best_composite_score":0.75,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":581.0,"contact_point_centroid":[0.17074,0.04262,0.41446],"force_p95":32.79103,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.38486,"mean_force":15.58606,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10224,0.09464,0.3888]},{"body_a":"door_panel","body_b":"link6","contact_count":65.0,"contact_point_centroid":[0.10311,0.1509,0.45259],"force_p95":26.12513,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.56383,"mean_force":9.03544,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10209,0.21921,0.34658]},{"body_a":"world","body_b":"door_panel","contact_count":1068.0,"contact_point_centroid":[0.30212,0.16926,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1007,0.3317,0.34776]},{"body_a":"world","body_b":"door_panel","contact_count":904.0,"contact_point_centroid":[0.32041,0.12062,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10243,0.12322,0.37878]}],"total_contact_groups":4},"final_pose_error":0.09896,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10703,-0.05857,0.40305],"hinge_angle":0.72277,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"hinge_progress","tcp_end":[0.10205,0.25678,0.34791],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44429,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"hinge_progress","tcp_end":[0.10703,-0.05857,0.40305],"tcp_start":[0.10205,0.25678,0.34791],"tcp_to_object_dist_end":0.42111,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```