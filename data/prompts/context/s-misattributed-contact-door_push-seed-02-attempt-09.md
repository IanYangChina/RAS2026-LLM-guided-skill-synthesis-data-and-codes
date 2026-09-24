## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9300 | 0.98 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.5632 | 0.78 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.0644 | 1.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`
- Frozen initial hinge angle: -0.083 rad
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
  frozen_initial_hinge_angle_rad: -0.0832
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d

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

## Parent Skill (Best Known, Q=1.258)

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
- id: approach_clearance
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_handle
- id: contact_handle
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
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
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
        mode: add
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
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
    tolerance: 0.05
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 45.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: open_door

```

## Last Evaluated Skill (Q=1.120)

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
- id: approach_clearance
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_handle
- id: contact_handle
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
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
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
        mode: add
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
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
    tolerance: 0.05
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 60.0
      default: 50.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_clearance** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.02, 0.0]
- **push_door** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}, tolerance=0.05
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_limit.threshold (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (add)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.02, 0.0]

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
| approach_clearance | 1.00 | 1.00 | 0.2134 |
| contact_handle | 1.00 | 0.67 | 0.0155 |
| push_door | 1.00 | 0.33 | 0.1560 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_clearance | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.103, 0.207, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 17.242 | 17.852 |
| contact_handle | descend | 1.00 / force_exceeded | (0.103, 0.207, 0.440)→(0.105, 0.196, 0.429) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 4.095 | 32.515 |
| push_door | push | 1.00 / time_limit | (0.105, 0.196, 0.429)→(0.110, 0.045, 0.391) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 5.054 | 44.764 |

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
- **Stop reason**: tolflatfitness
- **Mean generations**: 3.0
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7dec7b9d265217827596e50fcdf4f13e307fabe21fe4cab198e2a5d141ff1ba8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2703841599a88ffb6fe3c9276875d1c87ae4a75b7467b1c48183ebe23e97d755`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67442,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clearance.approach_speed":0.11477,"contact_handle.contact_force":14.14048,"contact_handle.descend_speed":0.05492,"push_door.force_guard_threshold":31.78727,"push_door.max_time":1.66768,"push_door.push_distance":0.27077,"push_door.push_speed":0.06951},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":110.0,"contact_point_centroid":[0.14617,0.19563,0.46343],"force_p95":38.19807,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.17243,"mean_force":20.0285,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.09996,0.26037,0.42219]},{"body_a":"door_panel","body_b":"link7","contact_count":774.0,"contact_point_centroid":[0.13767,0.09363,0.46324],"force_p95":17.20442,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.22587,"mean_force":12.24307,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10065,0.16176,0.41794]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10134,0.23235,0.51624],"force_p95":25.66561,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.14326,"mean_force":12.27555,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.09996,0.29016,0.40612]},{"body_a":"door_panel","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.1418,0.15942,0.47873],"force_p95":13.43627,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.79481,"mean_force":12.49643,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09986,0.22695,0.43616]},{"body_a":"world","body_b":"door_panel","contact_count":496.0,"contact_point_centroid":[0.30004,0.20027,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.09991,0.3136,0.39369]},{"body_a":"world","body_b":"door_panel","contact_count":48.0,"contact_point_centroid":[0.30236,0.16777,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09985,0.22749,0.4368]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.31233,0.13279,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10071,0.15725,0.41689]}],"total_contact_groups":7},"final_pose_error":0.23653,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1016,0.0932,0.40202],"hinge_angle":0.4489,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":46.17243,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.79481,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":71.0,"raw_peak_contact_force":18.79481,"subtask_id":"reach_handle","tcp_end":[0.1,0.22957,0.43891],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":49.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1622.0,"raw_peak_contact_force":27.22587,"subtask_id":"reach_handle","tcp_end":[0.09992,0.22517,0.43417],"tcp_start":[0.1,0.22957,0.43891],"tcp_to_object_dist_end":0.49918,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":610.0,"raw_peak_contact_force":46.17243,"subtask_id":"open_door","tcp_end":[0.1016,0.0932,0.40202],"tcp_start":[0.09992,0.22517,0.43417],"tcp_to_object_dist_end":0.42501,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84706,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clearance.approach_speed":0.09131,"contact_handle.contact_force":13.75986,"contact_handle.descend_speed":0.06067,"push_door.force_guard_threshold":36.48061,"push_door.max_time":1.99866,"push_door.push_distance":0.16049,"push_door.push_speed":0.08709},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":16.0,"contact_point_centroid":[0.10174,0.23631,0.51995],"force_p95":46.14088,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.6302,"mean_force":28.4497,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10085,0.29648,0.41089]},{"body_a":"door_panel","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.148,0.20784,0.4656],"force_p95":34.61793,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.2089,"mean_force":19.25053,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10106,0.27267,0.42565]},{"body_a":"door_panel","body_b":"link7","contact_count":821.0,"contact_point_centroid":[0.13956,0.11478,0.45575],"force_p95":16.73441,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.47478,"mean_force":11.76482,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10088,0.18188,0.41001]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.14568,0.18443,0.47664],"force_p95":14.62047,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.2389,"mean_force":12.71326,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10103,0.25108,0.43549]},{"body_a":"world","body_b":"door_panel","contact_count":356.0,"contact_point_centroid":[0.29999,0.20583,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10058,0.32563,0.39293]},{"body_a":"world","body_b":"door_panel","contact_count":52.0,"contact_point_centroid":[0.30061,0.18147,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10104,0.2519,0.43652]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30891,0.14418,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10088,0.17957,0.40924]}],"total_contact_groups":7},"final_pose_error":0.1139,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.101,0.10934,0.38534],"hinge_angle":0.40713,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":53.6302,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.11449,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":64.0,"raw_peak_contact_force":15.2389,"subtask_id":"reach_handle","tcp_end":[0.10128,0.25324,0.4378],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.28433,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1797.0,"raw_peak_contact_force":26.47478,"subtask_id":"reach_handle","tcp_end":[0.10101,0.25022,0.43447],"tcp_start":[0.10128,0.25324,0.4378],"tcp_to_object_dist_end":0.51144,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":445.0,"raw_peak_contact_force":53.6302,"subtask_id":"open_door","tcp_end":[0.101,0.10934,0.38534],"tcp_start":[0.10101,0.25022,0.43447],"tcp_to_object_dist_end":0.41309,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84848,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clearance.approach_speed":0.07538,"contact_handle.contact_force":17.90086,"contact_handle.descend_speed":0.06171,"push_door.force_guard_threshold":46.3891,"push_door.max_time":2.1593,"push_door.push_distance":0.32902,"push_door.push_speed":0.11266},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.19724,-0.05259,0.46484],"force_p95":15.444,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.84483,"mean_force":14.47306,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12509,-0.05654,0.38854]},{"body_a":"door_panel","body_b":"link7","contact_count":425.0,"contact_point_centroid":[0.1759,-0.00087,0.43853],"force_p95":18.8903,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.60105,"mean_force":14.02435,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11757,0.05364,0.40641]},{"body_a":"door_panel","body_b":"link7","contact_count":132.0,"contact_point_centroid":[0.14178,0.10683,0.47275],"force_p95":30.28247,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.48789,"mean_force":18.04878,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.1066,0.17628,0.42763]},{"body_a":"door_panel","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.14209,0.05285,0.47392],"force_p95":16.24031,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.52272,"mean_force":12.64255,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.11075,0.12396,0.42888]},{"body_a":"world","body_b":"door_panel","contact_count":656.0,"contact_point_centroid":[0.30554,0.15364,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10356,0.27487,0.39226]},{"body_a":"world","body_b":"door_panel","contact_count":300.0,"contact_point_centroid":[0.31884,0.11475,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.11072,0.1241,0.42904]},{"body_a":"world","body_b":"door_panel","contact_count":812.0,"contact_point_centroid":[0.34113,0.0793,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11974,0.02155,0.40119]}],"total_contact_groups":7},"final_pose_error":0.24624,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12593,-0.06788,0.38673],"hinge_angle":0.72341,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":43.84483,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.81627,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":455.0,"raw_peak_contact_force":19.52272,"subtask_id":"reach_handle","tcp_end":[0.10783,0.1368,0.44201],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1322.0,"raw_peak_contact_force":43.84483,"subtask_id":"reach_handle","tcp_end":[0.11377,0.11201,0.41723],"tcp_start":[0.10783,0.1368,0.44201],"tcp_to_object_dist_end":0.44673,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.16224,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":788.0,"raw_peak_contact_force":34.48789,"subtask_id":"open_door","tcp_end":[0.12593,-0.06788,0.38673],"tcp_start":[0.11377,0.11201,0.41723],"tcp_to_object_dist_end":0.41234,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```