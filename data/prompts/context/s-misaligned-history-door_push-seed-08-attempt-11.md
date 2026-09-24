## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7  | 1.1700 | 1.00 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1700 | 1.00 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1700 | 1.00 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1700 | 1.00 | ❌ rejected |
| 7 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1200 | 1.00 | ❌ rejected |

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

## Current Skill (Q=1.120) — your mutation base

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

- **Composite score**: 1.120
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.67 | 0.2598 |
| descend_1 | 1.00 | 1.00 | 0.0270 |
| push_1 | 1.00 | 0.00 | 0.1509 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.105, 0.170, 0.471) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 6.400 | 61.724 |
| descend_1 | descend | 1.00 / force_exceeded | (0.105, 0.170, 0.471)→(0.109, 0.154, 0.451) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 22.307 | 22.336 |
| push_1 | push | 1.00 / time_limit | (0.109, 0.154, 0.451)→(0.109, 0.003, 0.449) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 31.803 |

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
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.267


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.83333,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31039,"approach_1.approach_tol":0.02949,"approach_1.arc_height":0.10895,"descend_1.descend_force":12.99597,"push_1.push_distance":0.16774,"push_1.push_max_time":5.34752,"push_1.push_speed":0.15209},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":81.0,"contact_point_centroid":[0.14216,0.18854,0.52571],"force_p95":34.27779,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.88107,"mean_force":21.63512,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10036,0.26033,0.4908]},{"body_a":"door_panel","body_b":"link7","contact_count":548.0,"contact_point_centroid":[0.14087,0.0766,0.50167],"force_p95":17.55339,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.09811,"mean_force":13.33191,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09995,0.14784,0.46353]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13947,0.1508,0.50187],"force_p95":18.52696,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.76228,"mean_force":16.71376,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.10002,0.22318,0.46536]},{"body_a":"world","body_b":"door_panel","contact_count":432.0,"contact_point_centroid":[0.30002,0.19743,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10083,0.34337,0.45723]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30317,0.16315,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09998,0.22401,0.46653]},{"body_a":"world","body_b":"door_panel","contact_count":652.0,"contact_point_centroid":[0.31503,0.12668,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09995,0.14776,0.46354]}],"total_contact_groups":6},"final_pose_error":0.00944,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1,0.06452,0.46351],"hinge_angle":0.51666,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":57.88107,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":413.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":513.0,"raw_peak_contact_force":57.88107,"subtask_id":"reach_handle","tcp_end":[0.09996,0.22634,0.46978],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":31.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.96994,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23.0,"raw_peak_contact_force":18.76228,"subtask_id":"reach_handle","tcp_end":[0.10002,0.22294,0.46506],"tcp_start":[0.09996,0.22634,0.46978],"tcp_to_object_dist_end":0.52534,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":681.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1200.0,"raw_peak_contact_force":31.09811,"subtask_id":"open_door","tcp_end":[0.1,0.06452,0.46351],"tcp_start":[0.10002,0.22294,0.46506],"tcp_to_object_dist_end":0.47855,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.40845,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.21531,"approach_1.approach_tol":0.03133,"approach_1.arc_height":0.1189,"descend_1.descend_force":19.74369,"push_1.push_distance":0.24485,"push_1.push_max_time":5.70165,"push_1.push_speed":0.11579},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":95.0,"contact_point_centroid":[0.13871,0.11354,0.53414],"force_p95":38.25111,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.64344,"mean_force":21.53763,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10538,0.19121,0.4989]},{"body_a":"door_panel","body_b":"link7","contact_count":542.0,"contact_point_centroid":[0.15504,0.00277,0.48794],"force_p95":15.8791,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.01238,"mean_force":12.85367,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10887,0.06976,0.45289]},{"body_a":"door_panel","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.1365,0.06407,0.49954],"force_p95":15.40596,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.79509,"mean_force":12.8303,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.10758,0.14271,0.46198]},{"body_a":"world","body_b":"door_panel","contact_count":548.0,"contact_point_centroid":[0.30406,0.16015,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10272,0.316,0.46042]},{"body_a":"world","body_b":"door_panel","contact_count":88.0,"contact_point_centroid":[0.31632,0.12026,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.10773,0.14201,0.46111]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.33599,0.08661,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10888,0.04521,0.45291]}],"total_contact_groups":6},"final_pose_error":0.05882,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10903,-0.04948,0.45302],"hinge_angle":0.65545,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":59.64344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":518.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":643.0,"raw_peak_contact_force":59.64344,"subtask_id":"reach_handle","tcp_end":[0.10629,0.14954,0.47087],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":23.42732,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":152.0,"raw_peak_contact_force":23.79509,"subtask_id":"reach_handle","tcp_end":[0.10897,0.13657,0.45454],"tcp_start":[0.10629,0.14954,0.47087],"tcp_to_object_dist_end":0.48696,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1458.0,"raw_peak_contact_force":30.01238,"subtask_id":"open_door","tcp_end":[0.10903,-0.04948,0.45302],"tcp_start":[0.10897,0.13657,0.45454],"tcp_to_object_dist_end":0.46858,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.57895,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.2967,"approach_1.approach_tol":0.03174,"approach_1.arc_height":0.1603,"descend_1.descend_force":20.20977,"push_1.push_distance":0.11622,"push_1.push_max_time":4.83386,"push_1.push_speed":0.11969},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.13861,0.10009,0.54347],"force_p95":39.15993,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.64605,"mean_force":23.15094,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10765,0.18017,0.51149]},{"body_a":"door_panel","body_b":"link7","contact_count":393.0,"contact_point_centroid":[0.17257,-0.01441,0.46023],"force_p95":21.62804,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.29746,"mean_force":13.87073,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11723,0.04927,0.43028]},{"body_a":"door_panel","body_b":"link7","contact_count":184.0,"contact_point_centroid":[0.14149,0.03865,0.48619],"force_p95":17.24083,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.44931,"mean_force":13.00505,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.11304,0.11809,0.45192]},{"body_a":"world","body_b":"door_panel","contact_count":596.0,"contact_point_centroid":[0.30507,0.15516,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10372,0.3166,0.47503]},{"body_a":"world","body_b":"door_panel","contact_count":284.0,"contact_point_centroid":[0.32204,0.10832,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.11332,0.11701,0.45063]},{"body_a":"world","body_b":"door_panel","contact_count":484.0,"contact_point_centroid":[0.3387,0.08221,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11723,0.04815,0.43034]}],"total_contact_groups":6},"final_pose_error":0.00815,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11723,-0.00662,0.43025],"hinge_angle":0.68694,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":67.64605,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":539.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.19881,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":686.0,"raw_peak_contact_force":67.64605,"subtask_id":"reach_handle","tcp_end":[0.10877,0.13523,0.47365],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":28.52333,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":468.0,"raw_peak_contact_force":24.44931,"subtask_id":"reach_handle","tcp_end":[0.11738,0.10163,0.43196],"tcp_start":[0.10877,0.13523,0.47365],"tcp_to_object_dist_end":0.45901,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":579.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":877.0,"raw_peak_contact_force":34.29746,"subtask_id":"open_door","tcp_end":[0.11723,-0.00662,0.43025],"tcp_start":[0.11738,0.10163,0.43196],"tcp_to_object_dist_end":0.44598,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```