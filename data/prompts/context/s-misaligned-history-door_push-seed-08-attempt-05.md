## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1700 | 1.00 | ❌ rejected |
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1700 | 1.00 | ✅ accepted |
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 0.5269 | 0.52 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 0.8440 | 0.69 | ✅ accepted |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 4  | 1.1700 | 1.00 | ❌ rejected |

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

## Current Skill (Q=1.170) — your mutation base

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
  anchor: world
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_handle
- id: descend_1
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
  parameters:
    descend_force:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
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
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.170
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.67 | 0.2585 |
| descend_1 | 1.00 | 1.00 | 0.0127 |
| push_1 | 1.00 | 0.67 | 0.2095 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.105, 0.167, 0.461) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 4.982 | 57.778 |
| descend_1 | descend | 1.00 / force_exceeded | (0.105, 0.167, 0.461)→(0.106, 0.158, 0.452) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 20.127 | 20.328 |
| push_1 | push | 1.00 / time_limit | (0.106, 0.158, 0.452)→(0.106, -0.051, 0.450) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 0.000 | 43.155 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.170
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolfun
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.72727,"average_solve_count":55.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.27039,"approach_1.arc_height":0.14676,"descend_1.descend_force":15.42633,"push_1.push_distance":0.21389,"push_1.push_max_time":6.97348,"push_1.push_speed":0.14301},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":135.0,"contact_point_centroid":[0.14252,0.18466,0.51054],"force_p95":22.013,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.21766,"mean_force":16.59372,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09989,0.25535,0.47459]},{"body_a":"door_panel","body_b":"link7","contact_count":572.0,"contact_point_centroid":[0.139,0.0638,0.49092],"force_p95":18.13658,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.99811,"mean_force":13.70133,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09976,0.13471,0.45291]},{"body_a":"door_panel","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.139,0.14571,0.49508],"force_p95":15.82396,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.51152,"mean_force":12.25247,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09967,0.21721,0.45671]},{"body_a":"world","body_b":"door_panel","contact_count":608.0,"contact_point_centroid":[0.30007,0.19652,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10013,0.33482,0.4407]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.30369,0.16047,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09966,0.21742,0.457]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.32002,0.11653,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09976,0.12063,0.45292]}],"total_contact_groups":6},"final_pose_error":0.00922,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09975,0.01068,0.45291],"hinge_angle":0.57411,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":52.21766,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":743.0,"raw_peak_contact_force":52.21766,"subtask_id":"reach_handle","tcp_end":[0.09963,0.21892,0.45886],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":33.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":24.51152,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":48.0,"raw_peak_contact_force":24.51152,"subtask_id":"reach_handle","tcp_end":[0.09972,0.21549,0.45452],"tcp_start":[0.09963,0.21892,0.45886],"tcp_to_object_dist_end":0.5128,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":890.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1440.0,"raw_peak_contact_force":42.99811,"subtask_id":"open_door","tcp_end":[0.09975,0.01068,0.45291],"tcp_start":[0.09972,0.21549,0.45452],"tcp_to_object_dist_end":0.46388,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.08772,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29767,"approach_1.arc_height":0.08055,"descend_1.descend_force":11.84851,"push_1.push_distance":0.24735,"push_1.push_max_time":6.97703,"push_1.push_speed":0.15475},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":125.0,"contact_point_centroid":[0.13928,0.11194,0.51288],"force_p95":32.25451,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.26034,"mean_force":18.45642,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10538,0.18726,0.47469]},{"body_a":"door_panel","body_b":"link7","contact_count":309.0,"contact_point_centroid":[0.14758,0.02382,0.49145],"force_p95":18.76411,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.902,"mean_force":14.66127,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10641,0.0946,0.45532]},{"body_a":"door_panel","body_b":"link6","contact_count":97.0,"contact_point_centroid":[0.1756,-0.03384,0.58505],"force_p95":18.14492,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.67382,"mean_force":11.09692,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10643,-0.04882,0.45534]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13581,0.06817,0.49848],"force_p95":12.95405,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.99406,"mean_force":8.52931,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.10626,0.14494,0.45769]},{"body_a":"world","body_b":"door_panel","contact_count":660.0,"contact_point_centroid":[0.30421,0.15951,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10274,0.30123,0.43787]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.31536,0.12249,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.10617,0.1451,0.45791]},{"body_a":"world","body_b":"door_panel","contact_count":828.0,"contact_point_centroid":[0.33528,0.08753,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10642,0.02751,0.45531]}],"total_contact_groups":7},"final_pose_error":0.01039,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1064,-0.09279,0.45543],"hinge_angle":0.65697,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":59.26034,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.94465,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":785.0,"raw_peak_contact_force":59.26034,"subtask_id":"reach_handle","tcp_end":[0.10615,0.14598,0.45898],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":15.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.99406,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15.0,"raw_peak_contact_force":12.99406,"subtask_id":"reach_handle","tcp_end":[0.10635,0.14427,0.45685],"tcp_start":[0.10615,0.14598,0.45898],"tcp_to_object_dist_end":0.49075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":955.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1234.0,"raw_peak_contact_force":45.902,"subtask_id":"open_door","tcp_end":[0.1064,-0.09279,0.45543],"tcp_start":[0.10635,0.14427,0.45685],"tcp_to_object_dist_end":0.47681,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44615,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.37984,"approach_1.arc_height":0.11424,"descend_1.descend_force":13.9024,"push_1.push_distance":0.25147,"push_1.push_max_time":4.50144,"push_1.push_speed":0.11459},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":108.0,"contact_point_centroid":[0.13913,0.10062,0.53005],"force_p95":30.93808,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.85692,"mean_force":20.38868,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10754,0.17895,0.49472]},{"body_a":"door_panel","body_b":"link7","contact_count":313.0,"contact_point_centroid":[0.16298,0.0066,0.47382],"force_p95":18.433,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.56513,"mean_force":14.18301,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11327,0.07436,0.44196]},{"body_a":"door_panel","body_b":"link6","contact_count":133.0,"contact_point_centroid":[0.18206,-0.04254,0.57033],"force_p95":21.10409,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.88499,"mean_force":11.32893,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11326,-0.04934,0.44189]},{"body_a":"door_panel","body_b":"link7","contact_count":98.0,"contact_point_centroid":[0.13759,0.04545,0.49159],"force_p95":18.53171,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.47712,"mean_force":12.97765,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.11095,0.12481,0.45415]},{"body_a":"world","body_b":"door_panel","contact_count":608.0,"contact_point_centroid":[0.30519,0.15473,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10355,0.31258,0.45398]},{"body_a":"world","body_b":"door_panel","contact_count":148.0,"contact_point_centroid":[0.31978,0.11275,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.11071,0.12575,0.45529]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.33861,0.08227,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11326,0.02539,0.4419]}],"total_contact_groups":7},"final_pose_error":0.06482,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11326,-0.07093,0.44194],"hinge_angle":0.68771,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":61.85692,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":716.0,"raw_peak_contact_force":61.85692,"subtask_id":"reach_handle","tcp_end":[0.1086,0.13463,0.46632],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":183.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.8744,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":246.0,"raw_peak_contact_force":23.47712,"subtask_id":"reach_handle","tcp_end":[0.11336,0.11573,0.44359],"tcp_start":[0.1086,0.13463,0.46632],"tcp_to_object_dist_end":0.47224,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1294.0,"raw_peak_contact_force":40.56513,"subtask_id":"open_door","tcp_end":[0.11326,-0.07093,0.44194],"tcp_start":[0.11336,0.11573,0.44359],"tcp_to_object_dist_end":0.4617,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```