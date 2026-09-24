## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.0062 | 0.89 | ✅ accepted |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9765 | 0.86 | ✅ accepted |
| 8 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.2415 | 0.29 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.4488 | 0.40 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`
- Frozen initial hinge angle: 0.524 rad
- target_hinge_angle: 0.129 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
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
  target_hinge_angle_rad: 0.129
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

## Current Skill (Q=1.120) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_handle
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
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
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
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_handle
- id: descend_to_handle
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: approach_handle
- id: push_door
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
      distance: 0.15
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 0.5
      - 15.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.0
      - 0.5
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_y_offset:
      type: scalar
      range:
      - -0.1
      - 0.1
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    push_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_handle** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **push_door** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_y_offset: status=consumed; consumers=target.offset.y (add)
    - push_z_offset: status=consumed; consumers=target.offset.z (add)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, -0.02, 0.0]

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
| approach_handle | 1.00 | 1.00 | 0.2385 |
| descend_to_handle | 1.00 | 1.00 | 0.0362 |
| push_door | 1.00 | 0.67 | 0.1049 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.105, 0.177, 0.435) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 7.717 | 41.685 |
| descend_to_handle | contact | 1.00 / force_exceeded | (0.105, 0.177, 0.435)→(0.108, 0.150, 0.411) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 29.804 | 31.599 |
| push_door | push | 1.00 / time_limit | (0.108, 0.150, 0.411)→(0.187, 0.088, 0.381) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 5.105 | 34.219 |

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
- **Mean generations**: 7.7
- **Final σ (mean)**: 0.334


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
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.12924},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54128,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.09418,"descend_to_handle.contact_force_threshold":26.27437,"push_door.max_push_time":3.70621,"push_door.push_distance":0.13257,"push_door.push_speed":0.05634,"push_door.push_y_offset":-0.03571,"push_door.push_z_offset":0.0037},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":120.0,"contact_point_centroid":[0.17036,0.12032,0.44902],"force_p95":33.31891,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.98282,"mean_force":18.52917,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10508,0.1777,0.42512]},{"body_a":"door_panel","body_b":"link6","contact_count":21.0,"contact_point_centroid":[0.10382,0.14553,0.51825],"force_p95":32.87345,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.51459,"mean_force":16.23451,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10432,0.21378,0.41257]},{"body_a":"door_panel","body_b":"link7","contact_count":715.0,"contact_point_centroid":[0.21674,0.03849,0.42729],"force_p95":27.05614,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.22322,"mean_force":14.69147,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14994,0.09504,0.40053]},{"body_a":"door_panel","body_b":"link7","contact_count":95.0,"contact_point_centroid":[0.17292,0.08007,0.45104],"force_p95":16.1081,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.22667,"mean_force":14.44475,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.10757,0.13741,0.4271]},{"body_a":"world","body_b":"door_panel","contact_count":708.0,"contact_point_centroid":[0.30435,0.15876,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10291,0.27182,0.39222]},{"body_a":"world","body_b":"door_panel","contact_count":148.0,"contact_point_centroid":[0.31559,0.122,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.10748,0.13785,0.42758]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.33099,0.0939,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14715,0.09734,0.4017]}],"total_contact_groups":7},"final_pose_error":0.10798,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18753,0.06417,0.38492],"hinge_angle":0.66429,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":35.98282,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":849.0,"raw_peak_contact_force":35.98282,"subtask_id":"approach_handle","tcp_end":[0.10578,0.14656,0.43614],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":153.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":30.52478,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":243.0,"raw_peak_contact_force":30.22667,"subtask_id":"approach_handle","tcp_end":[0.10945,0.12911,0.41914],"tcp_start":[0.10578,0.14656,0.43614],"tcp_to_object_dist_end":0.45202,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.3141,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1635.0,"raw_peak_contact_force":34.22322,"subtask_id":"open_door","tcp_end":[0.18753,0.06417,0.38492],"tcp_start":[0.10945,0.12911,0.41914],"tcp_to_object_dist_end":0.43295,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.15917},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55752,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.10755,"descend_to_handle.contact_force_threshold":28.34914,"push_door.max_push_time":7.46098,"push_door.push_distance":0.18771,"push_door.push_speed":0.05228,"push_door.push_y_offset":-0.05464,"push_door.push_z_offset":0.02129},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":144.0,"contact_point_centroid":[0.17221,0.11259,0.45916],"force_p95":32.78102,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.64446,"mean_force":18.57299,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10691,0.16992,0.43532]},{"body_a":"door_panel","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.2209,0.02901,0.44134],"force_p95":19.24576,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.75114,"mean_force":14.00308,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.15381,0.08549,0.41424]},{"body_a":"door_panel","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.17574,0.06702,0.46136],"force_p95":20.84843,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.64214,"mean_force":14.6848,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.11026,0.12432,0.4373]},{"body_a":"door_panel","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.10506,0.13697,0.52772],"force_p95":0.06075,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08679,"mean_force":0.0124,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10597,0.20414,0.42236]},{"body_a":"world","body_b":"door_panel","contact_count":712.0,"contact_point_centroid":[0.30534,0.15405,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10375,0.2748,0.39522]},{"body_a":"world","body_b":"door_panel","contact_count":180.0,"contact_point_centroid":[0.31865,0.11513,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.11014,0.12484,0.4379]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.33493,0.08765,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.15247,0.08641,0.41457]}],"total_contact_groups":7},"final_pose_error":0.17018,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19244,0.05894,0.40432],"hinge_angle":0.68812,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.64446,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.60686,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":863.0,"raw_peak_contact_force":37.64446,"subtask_id":"approach_handle","tcp_end":[0.10789,0.13461,0.44876],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":187.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":30.64214,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":289.0,"raw_peak_contact_force":30.64214,"subtask_id":"approach_handle","tcp_end":[0.11282,0.11439,0.42661],"tcp_start":[0.10789,0.13461,0.44876],"tcp_to_object_dist_end":0.45587,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1663.0,"raw_peak_contact_force":33.75114,"subtask_id":"open_door","tcp_end":[0.19244,0.05894,0.40432],"tcp_start":[0.11282,0.11439,0.42661],"tcp_to_object_dist_end":0.45164,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.12965},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42453,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.08033,"descend_to_handle.contact_force_threshold":26.7878,"push_door.max_push_time":3.34827,"push_door.push_distance":0.14529,"push_door.push_speed":0.04389,"push_door.push_y_offset":-0.03568,"push_door.push_z_offset":-0.02199},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":120.0,"contact_point_centroid":[0.10056,0.2082,0.51005],"force_p95":39.61065,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.42826,"mean_force":23.51916,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10042,0.28682,0.40112]},{"body_a":"door_panel","body_b":"link7","contact_count":698.0,"contact_point_centroid":[0.20714,0.1148,0.39325],"force_p95":24.51136,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.68361,"mean_force":14.36691,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1418,0.17198,0.36887]},{"body_a":"door_panel","body_b":"link6","contact_count":164.0,"contact_point_centroid":[0.10206,0.16045,0.51034],"force_p95":20.23517,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.92857,"mean_force":14.17809,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.10051,0.22927,0.4042]},{"body_a":"door_panel","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.16609,0.15216,0.41348],"force_p95":18.71686,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.2456,"mean_force":14.13569,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.10081,0.20945,0.38923]},{"body_a":"world","body_b":"door_panel","contact_count":388.0,"contact_point_centroid":[0.30003,0.20264,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1003,0.3252,0.38292]},{"body_a":"world","body_b":"door_panel","contact_count":336.0,"contact_point_centroid":[0.302,0.17055,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"contact","tcp_position_centroid":[0.10052,0.23015,0.40498]},{"body_a":"world","body_b":"door_panel","contact_count":980.0,"contact_point_centroid":[0.31199,0.13288,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14339,0.17068,0.36822]}],"total_contact_groups":7},"final_pose_error":0.09574,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18034,0.1409,0.35382],"hinge_angle":0.42902,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":51.42826,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.54304,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":508.0,"raw_peak_contact_force":51.42826,"subtask_id":"approach_handle","tcp_end":[0.10063,0.24861,0.41966],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":28.2456,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":534.0,"raw_peak_contact_force":33.92857,"subtask_id":"approach_handle","tcp_end":[0.10087,0.2062,0.38683],"tcp_start":[0.10063,0.24861,0.41966],"tcp_to_object_dist_end":0.44981,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1678.0,"raw_peak_contact_force":34.68361,"subtask_id":"open_door","tcp_end":[0.18034,0.1409,0.35382],"tcp_start":[0.10087,0.2062,0.38683],"tcp_to_object_dist_end":0.42139,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```