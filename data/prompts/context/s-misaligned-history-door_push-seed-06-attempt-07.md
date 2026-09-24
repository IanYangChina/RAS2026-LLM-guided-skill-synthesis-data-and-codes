## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.0913 | 0.98 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1468 | 0.98 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.0779 | 0.91 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.0953 | 0.93 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6  | 1.1577 | 0.99 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`
- Frozen initial hinge angle: 0.013 rad
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
  frozen_initial_hinge_angle_rad: 0.0133
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.988, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=1.158) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: contact_handle
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_force
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
- id: push_door
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.35
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    max_time:
      type: scalar
      range:
      - 1.0
      - 6.0
      default: 3.5
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.45
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 28.0
    on_failure: abort
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_handle** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **push_door** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.35, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=28.0

## Design Metrics

- **Composite score**: 1.158
- **task_score** (E): 0.988
- **fitness_score**: 0.988  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2213 |
| contact_handle | 1.00 | 1.00 | 0.0060 |
| push_door | 1.00 | 0.67 | 0.1388 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.197, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 16.103 | 68.148 |
| contact_handle | descend | 1.00 / force_exceeded | (0.100, 0.197, 0.440)→(0.100, 0.196, 0.434) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 11.845 | 8.792 |
| push_door | push | 1.00 / time_limit | (0.100, 0.196, 0.434)→(0.100, 0.060, 0.404) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 7.860 | 26.889 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.170
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.420


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60c29f30561fee2ce06b067ae52309dfc2791a8d10a0f8247d4f057dc1f7bbf4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `34da519aca1008b6dc2cb922623d951e3d277879157a381e988a54565a8fccc4`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24638,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.17954,"contact_handle.force_threshold":8.08099,"contact_handle.speed":0.07328,"push_door.max_time":3.92841,"push_door.push_distance":0.44923,"push_door.push_speed":0.08531},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":92.0,"contact_point_centroid":[0.10132,0.17106,0.52588],"force_p95":41.32547,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.64036,"mean_force":20.27765,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10017,0.24203,0.41951]},{"body_a":"door_panel","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.16546,0.14811,0.46024],"force_p95":35.52616,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.19615,"mean_force":19.67948,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10014,0.20545,0.43629]},{"body_a":"door_panel","body_b":"link7","contact_count":800.0,"contact_point_centroid":[0.16569,0.07151,0.44486],"force_p95":17.64376,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.44717,"mean_force":13.2199,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.1285,0.41961]},{"body_a":"world","body_b":"door_panel","contact_count":416.0,"contact_point_centroid":[0.30086,0.18122,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10016,0.29572,0.39498]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16545,0.13992,0.46396],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10014,0.19727,0.44006]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.30512,0.15393,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09994,0.19638,0.43679]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.31837,0.11815,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.12455,0.4189]}],"total_contact_groups":7},"final_pose_error":0.33065,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09983,0.05653,0.40663],"hinge_angle":0.54024,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":51.64036,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":470.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.33573,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":539.0,"raw_peak_contact_force":51.64036,"subtask_id":"reach_handle","tcp_end":[0.10014,0.19727,0.44006],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":46.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.15823,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09992,0.19567,0.43327],"tcp_start":[0.10014,0.19727,0.44006],"tcp_to_object_dist_end":0.48579,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.84327,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1716.0,"raw_peak_contact_force":27.44717,"subtask_id":"push_door","tcp_end":[0.09983,0.05653,0.40663],"tcp_start":[0.09992,0.19567,0.43327],"tcp_to_object_dist_end":0.4225,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8ddc65539fcda71658f49649be9748aaabe492bbd016f1d18cf00d6d19f91cef`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16667,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.25568,"contact_handle.force_threshold":6.08028,"contact_handle.speed":0.08907,"push_door.max_time":4.20042,"push_door.push_distance":0.42707,"push_door.push_speed":0.08821},"optimized_scores":{"best_composite_score":1.13308,"best_fitness_score":0.96308,"best_task_score":0.96308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":66.0,"contact_point_centroid":[0.10163,0.16598,0.52841],"force_p95":31.10323,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.62216,"mean_force":20.82876,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10043,0.23607,0.42233]},{"body_a":"door_panel","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.16563,0.14803,0.46026],"force_p95":28.69056,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.60827,"mean_force":18.36563,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10042,0.20549,0.43634]},{"body_a":"door_panel","body_b":"link7","contact_count":795.0,"contact_point_centroid":[0.16579,0.07012,0.44447],"force_p95":17.86995,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.81469,"mean_force":13.26231,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09991,0.12721,0.41921]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16548,0.13889,0.46097],"force_p95":12.34475,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.99447,"mean_force":6.49724,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10024,0.19637,0.43705]},{"body_a":"world","body_b":"door_panel","contact_count":404.0,"contact_point_centroid":[0.30114,0.17754,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10036,0.29721,0.3943]},{"body_a":"world","body_b":"door_panel","contact_count":60.0,"contact_point_centroid":[0.30514,0.15385,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10013,0.19625,0.43703]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.3175,0.12018,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0999,0.12889,0.41951]}],"total_contact_groups":7},"final_pose_error":0.30523,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09996,0.05315,0.40511],"hinge_angle":0.54832,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":74.62216,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.3127,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":502.0,"raw_peak_contact_force":74.62216,"subtask_id":"reach_handle","tcp_end":[0.10037,0.19713,0.44019],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":41.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.99447,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":62.0,"raw_peak_contact_force":12.99447,"tcp_end":[0.10011,0.19559,0.43375],"tcp_start":[0.10037,0.19713,0.44019],"tcp_to_object_dist_end":0.48623,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.73754,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1711.0,"raw_peak_contact_force":27.81469,"subtask_id":"push_door","tcp_end":[0.09996,0.05315,0.40511],"tcp_start":[0.10011,0.19559,0.43375],"tcp_to_object_dist_end":0.42063,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ff14b28c151409e7d588c8444930f7538b4d5212a336dd723b958144baa5103b`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9359,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.16762,"contact_handle.force_threshold":9.53112,"contact_handle.speed":0.05163,"push_door.max_time":2.91883,"push_door.push_distance":0.31253,"push_door.push_speed":0.06461},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":142.0,"contact_point_centroid":[0.10094,0.18538,0.51883],"force_p95":45.11368,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.18263,"mean_force":22.40522,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10003,0.25908,0.41157]},{"body_a":"door_panel","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.16541,0.14832,0.46015],"force_p95":24.00416,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.59756,"mean_force":18.63498,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1001,0.20561,0.4362]},{"body_a":"door_panel","body_b":"link7","contact_count":810.0,"contact_point_centroid":[0.16552,0.07818,0.44359],"force_p95":16.95899,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.40634,"mean_force":12.77095,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09972,0.13525,0.41855]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.16528,0.13916,0.46216],"force_p95":13.28193,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.38251,"mean_force":6.52362,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09999,0.19653,0.4382]},{"body_a":"world","body_b":"door_panel","contact_count":456.0,"contact_point_centroid":[0.30055,0.19038,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10008,0.29933,0.39329]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.30507,0.15414,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09991,0.19636,0.43766]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.3166,0.12178,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09972,0.1326,0.41784]}],"total_contact_groups":7},"final_pose_error":0.21014,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09978,0.07118,0.4016],"hinge_angle":0.50785,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":78.18263,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":477.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.65942,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":630.0,"raw_peak_contact_force":78.18263,"subtask_id":"reach_handle","tcp_end":[0.10011,0.19709,0.44014],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.38251,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28.0,"raw_peak_contact_force":13.38251,"tcp_end":[0.0999,0.19601,0.43599],"tcp_start":[0.10011,0.19709,0.44014],"tcp_to_object_dist_end":0.48835,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1690.0,"raw_peak_contact_force":25.40634,"subtask_id":"push_door","tcp_end":[0.09978,0.07118,0.4016],"tcp_start":[0.0999,0.19601,0.43599],"tcp_to_object_dist_end":0.41988,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```