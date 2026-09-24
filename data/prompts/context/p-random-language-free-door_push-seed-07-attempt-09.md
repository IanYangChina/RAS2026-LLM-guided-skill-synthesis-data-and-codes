## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9027 | 0.96 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9026 | 0.96 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9045 | 0.96 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9026 | 0.96 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.8537 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.96). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`
- Frozen initial hinge angle: 0.044 rad
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
  frozen_initial_hinge_angle_rad: 0.0437
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.966, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.903) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: fixture
  offset:
  - -0.45
  - 0.03
  - 0.45
  weight: 0.3
- id: push_goal
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - -0.05
    - 0.05
    - 0.1
    tolerance: 0.01
  parameters:
    approach_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: scale
  subtask_id: pre_contact
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
    - -0.01
    - 0.03
    - 0.0
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: add
  subtask_id: push_goal
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
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
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: world_y
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: push_goal
- id: retract_1
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
    tolerance: 0.01

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[-0.05, 0.05, 0.1], tolerance=0.01
  - parameter_bindings:
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (scale)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[-0.01, 0.03, 0.0]
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=world_y
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.02, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.903
- **task_score** (E): 0.963
- **fitness_score**: 0.963  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.33 | 0.1918 |
| contact_1 | 1.00 | 1.00 | 0.0510 |
| push_1 | 1.00 | 1.00 | 0.2143 |
| retract_1 | 1.00 | 0.33 | 0.0401 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.057, 0.235, 0.438) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 3.314 | 11.602 |
| contact_1 | contact | 1.00 / force_exceeded | (0.057, 0.235, 0.438)→(0.073, 0.210, 0.396) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 35.139 | 18.107 |
| push_1 | push | 1.00 / step_budget | (0.073, 0.210, 0.396)→(0.075, -0.004, 0.401) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 22.518 | 133.820 |
| retract_1 | retract | 1.00 / step_budget | (0.075, -0.004, 0.401)→(0.075, -0.004, 0.441) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 142.956 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.940
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.478


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49741,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tol":0.05679,"approach_1.speed":0.06215,"contact_1.contact_force_threshold":14.81854,"push_1.push_distance":0.24433,"push_1.push_tol":0.01552},"optimized_scores":{"best_composite_score":0.94,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":435.0,"contact_point_centroid":[0.14129,0.02613,0.55009],"force_p95":51.88491,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.49823,"mean_force":21.86392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07625,0.0489,0.40841]},{"body_a":"door_panel","body_b":"link7","contact_count":79.0,"contact_point_centroid":[0.11866,0.09272,0.41774],"force_p95":43.93007,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.94662,"mean_force":21.99329,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07758,0.16285,0.38849]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.16624,-0.02042,0.53701],"force_p95":30.77252,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.0986,"mean_force":27.83778,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.07726,-0.00461,0.39939]},{"body_a":"door_panel","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.10646,0.176,0.48112],"force_p95":16.83976,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.06483,"mean_force":12.25759,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05763,0.23607,0.43491]},{"body_a":"door_panel","body_b":"link7","contact_count":182.0,"contact_point_centroid":[0.1126,0.1542,0.46266],"force_p95":14.99636,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.99515,"mean_force":11.76821,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.06533,0.21388,0.41433]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.30065,0.18113,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07788,0.31416,0.39282]},{"body_a":"world","body_b":"door_panel","contact_count":352.0,"contact_point_centroid":[0.30269,0.16613,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.06591,0.2131,0.41297]},{"body_a":"world","body_b":"door_panel","contact_count":1056.0,"contact_point_centroid":[0.31937,0.11545,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07566,0.0862,0.40377]},{"body_a":"world","body_b":"door_panel","contact_count":184.0,"contact_point_centroid":[0.33868,0.08136,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.07743,-0.00435,0.42171]}],"total_contact_groups":9},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07736,-0.00436,0.43943],"hinge_angle":0.58136,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":188.49823,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.94288,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":983.0,"raw_peak_contact_force":18.06483,"subtask_id":"pre_contact","tcp_end":[0.0555,0.22794,0.43926],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":42.51422,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":534.0,"raw_peak_contact_force":17.99515,"subtask_id":"push_goal","tcp_end":[0.07543,0.20005,0.39009],"tcp_start":[0.0555,0.22794,0.43926],"tcp_to_object_dist_end":0.44484,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.17218,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1570.0,"raw_peak_contact_force":188.49823,"subtask_id":"push_goal","tcp_end":[0.07726,-0.00461,0.39938],"tcp_start":[0.07543,0.20005,0.39009],"tcp_to_object_dist_end":0.40681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":186.0,"raw_peak_contact_force":31.0986,"tcp_end":[0.07736,-0.00436,0.43943],"tcp_start":[0.07726,-0.00461,0.39938],"tcp_to_object_dist_end":0.44621,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32178,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tol":0.05573,"approach_1.speed":0.01145,"contact_1.contact_force_threshold":12.36591,"push_1.push_distance":0.24829,"push_1.push_tol":0.01442},"optimized_scores":{"best_composite_score":0.94,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":477.0,"contact_point_centroid":[0.1312,0.04975,0.55314],"force_p95":46.37219,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":146.28409,"mean_force":17.55438,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06686,0.07747,0.40772]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.16121,-0.01252,0.55443],"force_p95":102.65046,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.36714,"mean_force":69.2003,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.0672,0.00773,0.40394]},{"body_a":"door_panel","body_b":"link7","contact_count":117.0,"contact_point_centroid":[0.10906,0.1274,0.43439],"force_p95":39.01732,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.39065,"mean_force":17.42415,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06775,0.19159,0.40414]},{"body_a":"door_panel","body_b":"link7","contact_count":120.0,"contact_point_centroid":[0.10768,0.19179,0.46868],"force_p95":13.28125,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.164,"mean_force":11.38456,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.05903,0.25054,0.42388]},{"body_a":"door_panel","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.10514,0.21219,0.47789],"force_p95":16.52404,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.74077,"mean_force":12.59575,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05566,0.27112,0.43549]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.29976,0.20117,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07659,0.33151,0.39369]},{"body_a":"world","body_b":"door_panel","contact_count":276.0,"contact_point_centroid":[0.30029,0.18552,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.05944,0.24999,0.42286]},{"body_a":"world","body_b":"door_panel","contact_count":1048.0,"contact_point_centroid":[0.31422,0.12937,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06714,0.11948,0.40642]},{"body_a":"world","body_b":"door_panel","contact_count":176.0,"contact_point_centroid":[0.33612,0.08492,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.06727,0.00796,0.42413]}],"total_contact_groups":9},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.06717,0.00794,0.44404],"hinge_angle":0.5595,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":146.28409,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1007.0,"raw_peak_contact_force":16.74077,"subtask_id":"pre_contact","tcp_end":[0.05197,0.26054,0.44281],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":266.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":27.37928,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":396.0,"raw_peak_contact_force":17.164,"subtask_id":"push_goal","tcp_end":[0.0662,0.241,0.40609],"tcp_start":[0.05197,0.26054,0.44281],"tcp_to_object_dist_end":0.47683,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.77086,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1642.0,"raw_peak_contact_force":146.28409,"subtask_id":"push_goal","tcp_end":[0.0672,0.00775,0.40393],"tcp_start":[0.0662,0.241,0.40609],"tcp_to_object_dist_end":0.40955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":178.0,"raw_peak_contact_force":106.36714,"tcp_end":[0.06717,0.00794,0.44404],"tcp_start":[0.0672,0.00775,0.40393],"tcp_to_object_dist_end":0.44917,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51366,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tol":0.06874,"approach_1.speed":0.13282,"contact_1.contact_force_threshold":12.01414,"push_1.push_distance":0.23157,"push_1.push_tol":0.04089},"optimized_scores":{"best_composite_score":0.828,"best_fitness_score":0.888,"best_task_score":0.888},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.16875,-0.02416,0.54444],"force_p95":291.4014,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":291.4014,"mean_force":291.4014,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.07963,-0.01494,0.39838]},{"body_a":"door_panel","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.12206,0.083,0.41879],"force_p95":40.74084,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.67771,"mean_force":22.37487,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.08024,0.15324,0.39016]},{"body_a":"door_panel","body_b":"link6","contact_count":437.0,"contact_point_centroid":[0.14324,0.02178,0.55128],"force_p95":26.93809,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.77288,"mean_force":14.48751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07898,0.04516,0.4083]},{"body_a":"door_panel","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.11715,0.14095,0.45802],"force_p95":15.98008,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.16203,"mean_force":12.1842,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.07162,0.20139,0.40897]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.30285,0.16488,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.08206,0.30931,0.38816]},{"body_a":"world","body_b":"door_panel","contact_count":292.0,"contact_point_centroid":[0.30384,0.15996,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.07108,0.20237,0.41046]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.32148,0.11112,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07884,0.07805,0.403]},{"body_a":"world","body_b":"door_panel","contact_count":172.0,"contact_point_centroid":[0.34027,0.07923,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.07981,-0.01472,0.41979]}],"total_contact_groups":8},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07978,-0.01466,0.43843],"hinge_angle":0.59455,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":291.4014,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.06363,0.21605,0.43081],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":302.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":35.52454,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":437.0,"raw_peak_contact_force":19.16203,"subtask_id":"push_goal","tcp_end":[0.07827,0.18976,0.39197],"tcp_start":[0.06363,0.21605,0.43081],"tcp_to_object_dist_end":0.44247,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":45.61171,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1430.0,"raw_peak_contact_force":66.67771,"subtask_id":"push_goal","tcp_end":[0.07963,-0.01494,0.39838],"tcp_start":[0.07827,0.18976,0.39197],"tcp_to_object_dist_end":0.40653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":173.0,"raw_peak_contact_force":291.4014,"tcp_end":[0.07978,-0.01466,0.43843],"tcp_start":[0.07963,-0.01494,0.39838],"tcp_to_object_dist_end":0.44587,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```