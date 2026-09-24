## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.6700 | 1.00 | ❌ rejected |
| 11 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 4 | 0.2196 | 0.25 | ❌ rejected |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.7500 | 1.00 | ❌ rejected |
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | time_limit | 4 | 1.1333 | 1.00 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | time_limit | 4 | 1.1333 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.670) — your mutation base

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
  weight: 0.2
- id: push_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.8
phases:
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: push_door
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.6
      default: 0.4
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.4, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, -0.02, 0.0]

## Design Metrics

- **Composite score**: 0.670
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_clear | 1.00 | 1.00 | 0.2407 |
| align_handle | 0.33 | 1.00 | 0.1030 |
| push_door | 1.00 | 0.33 | 0.1551 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_clear | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.151, 0.168, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 13.466 | 53.232 |
| align_handle | align | 0.33 / step_budget | (0.151, 0.168, 0.394)→(0.132, 0.069, 0.400) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 9.325 | 42.840 |
| push_door | push | 1.00 / time_limit | (0.132, 0.069, 0.400)→(0.134, -0.085, 0.412) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 3.150 | 36.794 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.670
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.314


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.25581,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_handle.align_speed":0.08663,"approach_clear.approach_speed":0.21263,"push_door.hinge_target":0.40961,"push_door.push_distance":0.33861,"push_door.push_max_time":8.82235,"push_door.push_speed":0.11056},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":175.0,"contact_point_centroid":[0.10308,0.1811,0.50854],"force_p95":21.46353,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.77341,"mean_force":14.50472,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.13297,0.26907,0.38107]},{"body_a":"door_panel","body_b":"link7","contact_count":658.0,"contact_point_centroid":[0.17972,-0.00347,0.43588],"force_p95":21.36299,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.66593,"mean_force":13.76439,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1097,0.04594,0.40874]},{"body_a":"door_panel","body_b":"link7","contact_count":211.0,"contact_point_centroid":[0.18642,0.09927,0.39324],"force_p95":25.37671,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.95718,"mean_force":16.30663,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.12126,0.15668,0.36898]},{"body_a":"door_panel","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.10885,0.12416,0.50681],"force_p95":20.69615,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.34333,"mean_force":12.00001,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.13887,0.20516,0.38519]},{"body_a":"world","body_b":"door_panel","contact_count":380.0,"contact_point_centroid":[0.30048,0.19044,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.12267,0.3095,0.37081]},{"body_a":"world","body_b":"door_panel","contact_count":488.0,"contact_point_centroid":[0.31134,0.13433,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.12488,0.16689,0.37321]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.33648,0.08653,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10945,0.04833,0.40893]}],"total_contact_groups":7},"final_pose_error":0.14864,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11452,-0.06087,0.40623],"hinge_angle":0.74344,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":42.77341,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.53454,"phase_name":"approach_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":555.0,"raw_peak_contact_force":42.77341,"subtask_id":"reach_handle","tcp_end":[0.14495,0.22216,0.3932],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":502.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.41421,"phase_name":"align_handle","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":786.0,"raw_peak_contact_force":35.95718,"subtask_id":"reach_handle","tcp_end":[0.11002,0.13189,0.37794],"tcp_start":[0.14495,0.22216,0.3932],"tcp_to_object_dist_end":0.41514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1574.0,"raw_peak_contact_force":42.66593,"subtask_id":"push_door","tcp_end":[0.11452,-0.06087,0.40623],"tcp_start":[0.11002,0.13189,0.37794],"tcp_to_object_dist_end":0.42643,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.68889,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_handle.align_speed":0.11344,"approach_clear.approach_speed":0.20029,"push_door.hinge_target":0.44384,"push_door.push_distance":0.26011,"push_door.push_max_time":8.31724,"push_door.push_speed":0.05193},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.21285,0.11184,0.41468],"force_p95":38.73004,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.98169,"mean_force":20.71136,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.14765,0.16915,0.39083]},{"body_a":"door_panel","body_b":"link7","contact_count":331.0,"contact_point_centroid":[0.21084,0.03709,0.4178],"force_p95":33.84199,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.62387,"mean_force":17.03319,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.14486,0.09415,0.3899]},{"body_a":"door_panel","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.10715,0.13005,0.50723],"force_p95":28.18108,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.2727,"mean_force":13.27092,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.13865,0.21287,0.3827]},{"body_a":"door_panel","body_b":"link7","contact_count":623.0,"contact_point_centroid":[0.20512,-0.0542,0.44905],"force_p95":17.4536,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.53654,"mean_force":11.64361,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13893,-0.00039,0.41788]},{"body_a":"world","body_b":"door_panel","contact_count":580.0,"contact_point_centroid":[0.30492,0.15694,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.12517,0.27732,0.37066]},{"body_a":"world","body_b":"door_panel","contact_count":460.0,"contact_point_centroid":[0.33122,0.09319,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.14465,0.09214,0.3908]},{"body_a":"world","body_b":"door_panel","contact_count":780.0,"contact_point_centroid":[0.35512,0.06206,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13892,-0.00072,0.41797]}],"total_contact_groups":7},"final_pose_error":0.16983,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13872,-0.04431,0.41779],"hinge_angle":0.77938,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":51.98169,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.74138,"phase_name":"approach_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":51.98169,"subtask_id":"reach_handle","tcp_end":[0.15216,0.14723,0.3949],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":533.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.8423,"phase_name":"align_handle","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":791.0,"raw_peak_contact_force":43.62387,"subtask_id":"reach_handle","tcp_end":[0.13933,0.04611,0.41111],"tcp_start":[0.15216,0.14723,0.3949],"tcp_to_object_dist_end":0.43652,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.45128,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1403.0,"raw_peak_contact_force":27.53654,"subtask_id":"push_door","tcp_end":[0.13872,-0.04431,0.41779],"tcp_start":[0.13933,0.04611,0.41111],"tcp_to_object_dist_end":0.44244,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.72727,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_handle.align_speed":0.12544,"approach_clear.approach_speed":0.30926,"push_door.hinge_target":0.42168,"push_door.push_distance":0.38527,"push_door.push_max_time":10.30208,"push_door.push_speed":0.11147},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":101.0,"contact_point_centroid":[0.21441,0.10586,0.41406],"force_p95":33.11237,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.94169,"mean_force":21.10322,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.1492,0.16319,0.39023]},{"body_a":"door_panel","body_b":"link7","contact_count":344.0,"contact_point_centroid":[0.21617,0.02375,0.41971],"force_p95":20.72969,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.94045,"mean_force":16.71128,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.15018,0.08087,0.39127]},{"body_a":"door_panel","body_b":"link7","contact_count":405.0,"contact_point_centroid":[0.21877,-0.07437,0.44425],"force_p95":17.10429,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.17879,"mean_force":13.10924,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1472,-0.03075,0.41472]},{"body_a":"door_panel","body_b":"link6","contact_count":59.0,"contact_point_centroid":[0.10778,0.12356,0.50692],"force_p95":20.08881,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.2122,"mean_force":12.23304,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.14053,0.20556,0.38281]},{"body_a":"world","body_b":"door_panel","contact_count":540.0,"contact_point_centroid":[0.3058,0.15287,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clear","phase_type":"approach","tcp_position_centroid":[0.12534,0.27822,0.36953]},{"body_a":"world","body_b":"door_panel","contact_count":456.0,"contact_point_centroid":[0.33553,0.08678,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_handle","phase_type":"align","tcp_position_centroid":[0.15023,0.0803,0.39259]},{"body_a":"world","body_b":"door_panel","contact_count":692.0,"contact_point_centroid":[0.36704,0.05072,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14724,-0.05689,0.41346]}],"total_contact_groups":7},"final_pose_error":0.2056,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.14737,-0.15032,0.41064],"hinge_angle":0.84191,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":64.94169,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.1218,"phase_name":"approach_clear","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":64.94169,"subtask_id":"reach_handle","tcp_end":[0.1549,0.13565,0.39534],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":508.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.71832,"phase_name":"align_handle","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":800.0,"raw_peak_contact_force":48.94045,"subtask_id":"reach_handle","tcp_end":[0.14732,0.02936,0.41203],"tcp_start":[0.1549,0.13565,0.39534],"tcp_to_object_dist_end":0.43856,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1097.0,"raw_peak_contact_force":40.17879,"subtask_id":"push_door","tcp_end":[0.14737,-0.15032,0.41064],"tcp_start":[0.14732,0.02936,0.41203],"tcp_to_object_dist_end":0.46145,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```