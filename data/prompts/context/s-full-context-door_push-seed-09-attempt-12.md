## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |

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
  - 0.45
  weight: 0.3
- id: push_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_above_handle
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

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
| approach_above_handle | 1.00 | 1.00 | 0.2415 |
| descend_to_handle | 1.00 | 1.00 | 0.0022 |
| push_door | 1.00 | 0.33 | 0.1449 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.105, 0.176, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.333 | 6.690 | 42.493 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.105, 0.176, 0.440)→(0.105, 0.175, 0.439) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 12.849 | 14.863 |
| push_door | push | 1.00 / time_limit | (0.105, 0.175, 0.439)→(0.111, 0.033, 0.407) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 3.689 | 29.711 |

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
- **Stop reason**: tolflatfitness
- **Mean generations**: 3.0
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95413,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_handle.approach_speed":0.08427,"descend_to_handle.descend_force_threshold":8.16642,"descend_to_handle.descend_speed":0.07505,"push_door.push_distance":0.23834,"push_door.push_duration":2.67912,"push_door.push_speed":0.09493},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":21.0,"contact_point_centroid":[0.10381,0.14566,0.52213],"force_p95":30.45905,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.73121,"mean_force":17.34917,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.10426,0.21384,0.41646]},{"body_a":"door_panel","body_b":"link7","contact_count":121.0,"contact_point_centroid":[0.1703,0.11943,0.45399],"force_p95":31.95581,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.57524,"mean_force":18.53182,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.10504,0.17685,0.4301]},{"body_a":"door_panel","body_b":"link7","contact_count":727.0,"contact_point_centroid":[0.1775,0.01582,0.44619],"force_p95":20.52868,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.96417,"mean_force":13.55395,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11045,0.07196,0.41989]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17107,0.0883,0.46481],"force_p95":12.40431,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.05717,"mean_force":6.52858,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10578,0.14575,0.44096]},{"body_a":"world","body_b":"door_panel","contact_count":696.0,"contact_point_centroid":[0.30408,0.15982,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.10277,0.27646,0.39318]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.31387,0.12614,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.1057,0.14582,0.44124]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.332,0.09318,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11053,0.07072,0.41989]}],"total_contact_groups":7},"final_pose_error":0.18932,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11552,-0.00737,0.40982],"hinge_angle":0.68269,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":33.73121,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.75044,"phase_name":"approach_above_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":838.0,"raw_peak_contact_force":33.73121,"subtask_id":"reach_handle","tcp_end":[0.10574,0.14636,0.44149],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.05717,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":13.05717,"subtask_id":"reach_handle","tcp_end":[0.10583,0.14506,0.44031],"tcp_start":[0.10574,0.14636,0.44149],"tcp_to_object_dist_end":0.47552,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1547.0,"raw_peak_contact_force":32.96417,"subtask_id":"push_door","tcp_end":[0.11552,-0.00737,0.40982],"tcp_start":[0.10583,0.14506,0.44031],"tcp_to_object_dist_end":0.42586,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87736,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_handle.approach_speed":0.0949,"descend_to_handle.descend_force_threshold":9.61521,"descend_to_handle.descend_speed":0.04434,"push_door.push_distance":0.30166,"push_door.push_duration":3.43403,"push_door.push_speed":0.09036},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.17218,0.1134,0.45285],"force_p95":32.52122,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.88807,"mean_force":18.58327,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.1069,0.17077,0.42897]},{"body_a":"door_panel","body_b":"link7","contact_count":719.0,"contact_point_centroid":[0.17955,0.00909,0.44968],"force_p95":19.82713,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.95297,"mean_force":13.55621,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11219,0.06498,0.42321]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17338,0.07681,0.46506],"force_p95":15.8359,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.66936,"mean_force":8.33468,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10801,0.13419,0.44125]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.10499,0.13731,0.52241],"force_p95":8.62703,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.78378,"mean_force":2.15676,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.10595,0.20469,0.41698]},{"body_a":"world","body_b":"door_panel","contact_count":692.0,"contact_point_centroid":[0.30524,0.15453,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.10366,0.27743,0.391]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.31642,0.12002,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10794,0.13435,0.44158]},{"body_a":"world","body_b":"door_panel","contact_count":876.0,"contact_point_centroid":[0.33453,0.08892,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11242,0.06133,0.42238]}],"total_contact_groups":7},"final_pose_error":0.25881,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11699,-0.01043,0.40762],"hinge_angle":0.69058,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.88807,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.31837,"phase_name":"approach_above_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":835.0,"raw_peak_contact_force":37.88807,"subtask_id":"reach_handle","tcp_end":[0.10795,0.13485,0.44187],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.62757,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26.0,"raw_peak_contact_force":16.66936,"subtask_id":"reach_handle","tcp_end":[0.10809,0.13345,0.44052],"tcp_start":[0.10795,0.13485,0.44187],"tcp_to_object_dist_end":0.47281,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.06593,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1595.0,"raw_peak_contact_force":30.95297,"subtask_id":"push_door","tcp_end":[0.11699,-0.01043,0.40762],"tcp_start":[0.10809,0.13345,0.44052],"tcp_to_object_dist_end":0.4242,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60674,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_handle.approach_speed":0.10028,"descend_to_handle.descend_force_threshold":8.71584,"descend_to_handle.descend_speed":0.04799,"push_door.push_distance":0.28226,"push_door.push_duration":3.47622,"push_door.push_speed":0.05741},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":115.0,"contact_point_centroid":[0.10057,0.20746,0.52365],"force_p95":42.78281,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.85851,"mean_force":24.99032,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.1004,0.28576,0.41483]},{"body_a":"door_panel","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.16582,0.10953,0.44052],"force_p95":18.00019,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.21651,"mean_force":12.71773,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10053,0.16677,0.41628]},{"body_a":"door_panel","body_b":"link6","contact_count":205.0,"contact_point_centroid":[0.10201,0.16088,0.53685],"force_p95":18.49879,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.93015,"mean_force":11.63527,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10011,0.22903,0.43083]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10088,0.17383,0.54293],"force_p95":14.86333,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.86333,"mean_force":14.86333,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.1004,0.24562,0.4361]},{"body_a":"world","body_b":"door_panel","contact_count":408.0,"contact_point_centroid":[0.30006,0.2017,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.10032,0.32298,0.3928]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30106,0.1771,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10044,0.24651,0.43714]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.30802,0.14646,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10043,0.18213,0.41988]}],"total_contact_groups":7},"final_pose_error":0.25247,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10083,0.11802,0.40499],"hinge_angle":0.39534,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":55.85851,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_above_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":523.0,"raw_peak_contact_force":55.85851,"subtask_id":"reach_handle","tcp_end":[0.1006,0.24748,0.43796],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.86333,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":29.0,"raw_peak_contact_force":14.86333,"subtask_id":"reach_handle","tcp_end":[0.1004,0.24551,0.43597],"tcp_start":[0.1006,0.24748,0.43796],"tcp_to_object_dist_end":0.51032,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1782.0,"raw_peak_contact_force":25.21651,"subtask_id":"push_door","tcp_end":[0.10083,0.11802,0.40499],"tcp_start":[0.1004,0.24551,0.43597],"tcp_to_object_dist_end":0.43372,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```