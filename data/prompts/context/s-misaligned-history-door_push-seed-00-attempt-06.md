## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | time_limit | time_limit | 8  | 0.5627 | 0.99 | ✅ accepted |
| 5 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | time_limit | time_limit | 8  | 0.6354 | 0.97 | ❌ rejected |
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6  | 0.6929 | 0.97 | ❌ rejected |
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5  | 0.6954 | 0.98 | ❌ rejected |
| 2 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5  | 0.5629 | 0.99 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.99). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`
- Frozen initial hinge angle: 0.048 rad
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
  frozen_initial_hinge_angle_rad: 0.0478
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.993, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.563) — your mutation base

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
- id: approach_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.55
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_time:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_handle
- id: descend_to_handle
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_time:
      type: scalar
      range:
      - 1.0
      - 6.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_handle
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
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
      distance: 0.3
      axis: world_y
      mode: replace_offset_projection
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
    push_time:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.55], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat
- **push_door** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], offset_along_axis={axis=world_y, distance=0.3, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.563
- **task_score** (E): 0.993
- **fitness_score**: 0.993  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2653 |
| descend_to_handle | 1.00 | 1.00 | 0.1662 |
| push_door | 1.00 | 1.00 | 0.1369 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.099, 0.243, 0.560) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 14.455 | 161.619 |
| descend_to_handle | descend | 1.00 / time_limit | (0.099, 0.243, 0.560)→(0.100, 0.198, 0.404) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 4.116 | 36.504 |
| push_door | push | 1.00 / time_limit | (0.100, 0.198, 0.404)→(0.098, 0.062, 0.407) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 11.844 | 28.708 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.570
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.380


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `275c70960dc683bb9d0f514db4e615bd3a6644bf8e38d8dd2bfa731bf179f097`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `35996939e2e1630dea7cedb55906290b2cb0393492844f540c2c9d9496e5416e`; realized-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04781,"panel":{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39474,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.12955,"approach_handle.approach_time":5.97905,"approach_handle.speed":0.19787,"descend_to_handle.descend_time":3.475,"descend_to_handle.speed":0.0745,"push_door.push_distance":0.4999,"push_door.push_time":8.60647,"push_door.speed":0.06895},"optimized_scores":{"best_composite_score":0.54857,"best_fitness_score":0.97857,"best_task_score":0.97857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":79.0,"contact_point_centroid":[0.10002,0.22498,0.75005],"force_p95":257.86107,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.45805,"mean_force":190.08746,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09821,0.24756,0.57376]},{"body_a":"door_panel","body_b":"link6","contact_count":50.0,"contact_point_centroid":[0.10117,0.17133,0.67604],"force_p95":58.9257,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.0542,"mean_force":21.12454,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09758,0.23632,0.56992]},{"body_a":"door_panel","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.16411,0.1525,0.58615],"force_p95":23.35039,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.4709,"mean_force":17.66214,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09855,0.20936,0.56171]},{"body_a":"door_panel","body_b":"link7","contact_count":783.0,"contact_point_centroid":[0.16502,0.06015,0.41947],"force_p95":17.76661,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.51724,"mean_force":13.062,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09925,0.11707,0.39343]},{"body_a":"door_panel","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.16466,0.13084,0.48356],"force_p95":19.92595,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.96604,"mean_force":13.60925,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09926,0.18799,0.45923]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.30097,0.17872,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09979,0.34864,0.50829]},{"body_a":"world","body_b":"door_panel","contact_count":1052.0,"contact_point_centroid":[0.30596,0.15058,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09918,0.18945,0.4772]},{"body_a":"world","body_b":"door_panel","contact_count":856.0,"contact_point_centroid":[0.3201,0.11415,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09925,0.11566,0.39337]}],"total_contact_groups":8},"final_pose_error":0.35153,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09791,0.04608,0.41216],"hinge_angle":0.56058,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":272.45805,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":901.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.46,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1029.0,"raw_peak_contact_force":272.45805,"subtask_id":"reach_handle","tcp_end":[0.09909,0.19593,0.5566],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59834,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1179.0,"raw_peak_contact_force":20.96604,"subtask_id":"reach_handle","tcp_end":[0.09958,0.18263,0.39332],"tcp_start":[0.09909,0.19593,0.5566],"tcp_to_object_dist_end":0.44493,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.00493,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1639.0,"raw_peak_contact_force":29.51724,"subtask_id":"open_door","tcp_end":[0.09791,0.04608,0.41216],"tcp_start":[0.09958,0.18263,0.39332],"tcp_to_object_dist_end":0.42612,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.00413,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42478,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.18792,"approach_handle.approach_time":5.65646,"approach_handle.speed":0.16609,"descend_to_handle.descend_time":3.55432,"descend_to_handle.speed":0.08464,"push_door.push_distance":0.3286,"push_door.push_time":8.2274,"push_door.speed":0.08272},"optimized_scores":{"best_composite_score":0.57,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":43.0,"contact_point_centroid":[0.10001,0.22499,0.75002],"force_p95":156.02848,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.36434,"mean_force":106.50297,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09909,0.23797,0.56926]},{"body_a":"door_panel","body_b":"link6","contact_count":116.0,"contact_point_centroid":[0.10089,0.17813,0.67689],"force_p95":35.08573,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.35621,"mean_force":13.97192,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09939,0.24809,0.57069]},{"body_a":"door_panel","body_b":"link7","contact_count":785.0,"contact_point_centroid":[0.16504,0.06509,0.42133],"force_p95":17.83834,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.87491,"mean_force":13.11999,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09924,0.12194,0.39535]},{"body_a":"door_panel","body_b":"link7","contact_count":249.0,"contact_point_centroid":[0.1646,0.1467,0.50049],"force_p95":21.54027,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.39203,"mean_force":13.94187,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09915,0.20376,0.47612]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10246,0.15623,0.66962],"force_p95":4.77548,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.02682,"mean_force":2.51341,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09904,0.22058,0.5647]},{"body_a":"world","body_b":"door_panel","contact_count":1088.0,"contact_point_centroid":[0.3002,0.1875,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09986,0.35973,0.48853]},{"body_a":"door_frame","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.1,0.225,0.75],"force_p95":0.0,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09898,0.22043,0.5647]},{"body_a":"world","body_b":"door_panel","contact_count":1068.0,"contact_point_centroid":[0.3039,0.15984,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09911,0.2057,0.48624]},{"body_a":"world","body_b":"door_panel","contact_count":964.0,"contact_point_centroid":[0.31943,0.11577,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09922,0.11894,0.39575]}],"total_contact_groups":9},"final_pose_error":0.19095,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09802,0.05228,0.41115],"hinge_angle":0.5471,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":188.36434,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.58715,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1247.0,"raw_peak_contact_force":188.36434,"subtask_id":"reach_handle","tcp_end":[0.09907,0.22068,0.56469],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.61432,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.34942,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1320.0,"raw_peak_contact_force":24.39203,"subtask_id":"reach_handle","tcp_end":[0.09951,0.18914,0.40064],"tcp_start":[0.09907,0.22068,0.56469],"tcp_to_object_dist_end":0.45408,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.2307,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1749.0,"raw_peak_contact_force":29.87491,"subtask_id":"open_door","tcp_end":[0.09802,0.05228,0.41115],"tcp_start":[0.09951,0.18914,0.40064],"tcp_to_object_dist_end":0.42589,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26549,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_height":0.10938,"approach_handle.approach_time":5.77059,"approach_handle.speed":0.12152,"descend_to_handle.descend_time":4.50447,"descend_to_handle.speed":0.09248,"push_door.push_distance":0.25571,"push_door.push_time":11.52955,"push_door.speed":0.07919},"optimized_scores":{"best_composite_score":0.57,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":375.0,"contact_point_centroid":[0.10066,0.19318,0.59454],"force_p95":26.87922,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.15277,"mean_force":16.96848,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09945,0.26659,0.48698]},{"body_a":"door_panel","body_b":"link7","contact_count":759.0,"contact_point_centroid":[0.1651,0.09557,0.42426],"force_p95":18.93613,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.73138,"mean_force":12.94107,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09948,0.1526,0.39959]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10136,0.23151,0.66785],"force_p95":23.92594,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.03333,"mean_force":23.26993,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0999,0.31166,0.55886]},{"body_a":"door_panel","body_b":"link6","contact_count":38.0,"contact_point_centroid":[0.10277,0.15314,0.52049],"force_p95":20.53998,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.89208,"mean_force":12.64454,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09943,0.21873,0.41532]},{"body_a":"world","body_b":"door_panel","contact_count":1116.0,"contact_point_centroid":[0.29985,0.20628,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09982,0.38708,0.45958]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.3005,0.18664,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09945,0.26681,0.48735]},{"body_a":"world","body_b":"door_panel","contact_count":964.0,"contact_point_centroid":[0.31236,0.13356,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09947,0.1557,0.40059]}],"total_contact_groups":7},"final_pose_error":0.15135,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09935,0.08818,0.39696],"hinge_angle":0.46718,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":64.15277,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":23.31739,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1120.0,"raw_peak_contact_force":24.03333,"subtask_id":"reach_handle","tcp_end":[0.09988,0.31095,0.5591],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.6475,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1243.0,"raw_peak_contact_force":64.15277,"subtask_id":"reach_handle","tcp_end":[0.09959,0.22229,0.41689],"tcp_start":[0.09988,0.31095,0.5591],"tcp_to_object_dist_end":0.48283,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.29759,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1761.0,"raw_peak_contact_force":26.73138,"subtask_id":"open_door","tcp_end":[0.09935,0.08818,0.39696],"tcp_start":[0.09959,0.22229,0.41689],"tcp_to_object_dist_end":0.41859,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```