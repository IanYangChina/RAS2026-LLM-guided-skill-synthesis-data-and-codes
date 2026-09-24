## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

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
- Frozen realised-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`
- Frozen initial hinge angle: 0.106 rad
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
  frozen_initial_hinge_angle_rad: 0.1065
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618

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

## Current Skill (Q=-0.004) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: handle_approach
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.3
- id: door_push
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
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
    - 0.0
    tolerance: 0.01
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
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: handle_approach
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
      distance: 0.1
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 10.0
      - 28.0
      default: 25
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: door_push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.1, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=guards.force_limit.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.004
- **task_score** (E): 0.396
- **fitness_score**: 0.396  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2220 |
| push_door | 0.00 | 0.33 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.177, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 13.615 | 40.790 |
| push_door | push | 0.00 / guard_failure | (0.102, 0.169, 0.355)→(0.102, 0.169, 0.355) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 42.449 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.403
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.403
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.403
- **Median Q (composite search score)**: -0.007
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22727,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.14222,"approach_handle.approach_tolerance":0.02615,"approach_handle.retry_offset_x":-0.00426,"approach_handle.retry_offset_z":0.00715,"push_door.force_safe_threshold":24.9965,"push_door.push_distance":0.30206,"push_door.push_duration":8.84556,"push_door.push_speed":0.34522},"optimized_scores":{"best_composite_score":0.00328,"best_fitness_score":0.40328,"best_task_score":0.40328},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.16982,0.09503,0.38779],"force_p95":20.50714,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.90129,"mean_force":15.6753,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10457,0.15245,0.36375]},{"body_a":"door_panel","body_b":"link7","contact_count":113.0,"contact_point_centroid":[0.16928,0.12257,0.37655],"force_p95":25.19218,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.46929,"mean_force":17.42186,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10406,0.17997,0.35252]},{"body_a":"door_panel","body_b":"link6","contact_count":41.0,"contact_point_centroid":[0.10335,0.14939,0.45493],"force_p95":22.544,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.76391,"mean_force":11.19383,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10321,0.21821,0.34916]},{"body_a":"world","body_b":"door_panel","contact_count":596.0,"contact_point_centroid":[0.30372,0.16219,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10216,0.27242,0.34975]},{"body_a":"world","body_b":"door_panel","contact_count":36.0,"contact_point_centroid":[0.31245,0.12982,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10456,0.1524,0.3638]}],"total_contact_groups":5},"final_pose_error":0.2962,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10458,0.1495,0.36593],"hinge_angle":0.31778,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":47.90129,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.79885,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":750.0,"raw_peak_contact_force":40.46929,"subtask_id":"handle_approach","tcp_end":[0.10463,0.15539,0.3617],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":35.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":59.0,"raw_peak_contact_force":47.90129,"subtask_id":"door_push","tcp_end":[0.10458,0.1495,0.36593],"tcp_start":[0.10455,0.1495,0.36591],"tcp_to_object_dist_end":0.40889,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95876,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.0504,"approach_handle.approach_tolerance":0.03048,"approach_handle.retry_offset_x":0.00345,"approach_handle.retry_offset_z":-0.01596,"push_door.force_safe_threshold":29.20485,"push_door.push_distance":0.4069,"push_door.push_duration":1.67789,"push_door.push_speed":0.41613},"optimized_scores":{"best_composite_score":-0.00995,"best_fitness_score":0.39005,"best_task_score":0.39005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.1656,0.13153,0.37319],"force_p95":22.55605,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.38432,"mean_force":14.75347,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10045,0.18889,0.34906]},{"body_a":"door_panel","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.16561,0.14585,0.37305],"force_p95":23.83779,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.99496,"mean_force":17.91165,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10044,0.20324,0.34902]},{"body_a":"door_panel","body_b":"link6","contact_count":114.0,"contact_point_centroid":[0.10136,0.17105,0.45521],"force_p95":13.8091,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.33206,"mean_force":10.02479,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10021,0.24294,0.34861]},{"body_a":"world","body_b":"door_panel","contact_count":432.0,"contact_point_centroid":[0.30093,0.1807,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10004,0.29424,0.34841]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.3061,0.15001,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10047,0.18874,0.34903]}],"total_contact_groups":5},"final_pose_error":0.39665,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10049,0.18424,0.34889],"hinge_angle":0.21771,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":42.38432,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.17262,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":580.0,"raw_peak_contact_force":23.99496,"subtask_id":"handle_approach","tcp_end":[0.1005,0.19449,0.34914],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":35.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":63.0,"raw_peak_contact_force":42.38432,"subtask_id":"door_push","tcp_end":[0.10049,0.18424,0.34889],"tcp_start":[0.10049,0.18425,0.3489],"tcp_to_object_dist_end":0.40714,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30769,"average_solve_count":26.0,"average_success_count":26.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.34029,"approach_handle.approach_tolerance":0.02717,"approach_handle.retry_offset_x":-0.00577,"approach_handle.retry_offset_z":0.00676,"push_door.force_safe_threshold":22.7444,"push_door.push_distance":0.34331,"push_door.push_duration":3.14368,"push_door.push_speed":0.41593},"optimized_scores":{"best_composite_score":-0.00683,"best_fitness_score":0.39317,"best_task_score":0.39317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":78.0,"contact_point_centroid":[0.10196,0.16325,0.45536],"force_p95":28.50257,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.90701,"mean_force":11.86508,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10111,0.2337,0.34908]},{"body_a":"door_panel","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.16658,0.1402,0.3739],"force_p95":36.36018,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.53527,"mean_force":18.59248,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10149,0.19765,0.34972]},{"body_a":"door_panel","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.16664,0.11976,0.3741],"force_p95":17.15714,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.05995,"mean_force":14.41568,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10157,0.17711,0.34987]},{"body_a":"world","body_b":"door_panel","contact_count":356.0,"contact_point_centroid":[0.30154,0.17527,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1006,0.29168,0.34846]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.30801,0.14311,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10156,0.17658,0.34988]}],"total_contact_groups":5},"final_pose_error":0.3342,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10155,0.17317,0.34979],"hinge_angle":0.24969,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":57.90701,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.87333,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":486.0,"raw_peak_contact_force":57.90701,"subtask_id":"handle_approach","tcp_end":[0.10163,0.18228,0.35008],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":35.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":54.0,"raw_peak_contact_force":37.05995,"subtask_id":"door_push","tcp_end":[0.10155,0.17317,0.34979],"tcp_start":[0.10155,0.17317,0.3498],"tcp_to_object_dist_end":0.4033,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```