## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.8233 | 1.00 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.7900 | 1.00 | ✅ accepted |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.7462 | 0.96 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2280 | 0.39 | ✅ accepted |

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

## Current Skill (Q=0.823) — your mutation base

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
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
- id: contact_handle
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.04
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
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
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
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
    push_time:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: open_door
- id: retract_after_push
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.45
    tolerance: 0.02
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **contact_handle** (`contact`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.04, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.45], tolerance=0.02
  - parameter_bindings:
    - retract_height: status=consumed; consumers=generator.arc_height (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.823
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 0.33 | 0.2142 |
| contact_handle | 1.00 | 1.00 | 0.0014 |
| push_door | 1.00 | 0.67 | 0.1885 |
| retract_after_push | 1.00 | 0.67 | 0.1732 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.186, 0.369) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 41.617 |
| contact_handle | contact | 1.00 / force_exceeded | (0.100, 0.186, 0.369)→(0.100, 0.185, 0.368) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 16.819 | 14.173 |
| push_door | push | 1.00 / time_limit | (0.100, 0.185, 0.368)→(0.101, 0.002, 0.412) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 42.970 |
| retract_after_push | retract | 1.00 / step_budget | (0.101, 0.002, 0.412)→(0.101, 0.167, 0.465) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.823
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.256


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07407,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.05801,"approach_handle.arc_height":0.11561,"contact_handle.contact_force":8.15369,"contact_handle.contact_speed":0.02854,"push_door.push_distance":0.28508,"push_door.push_speed":0.10374,"push_door.push_time":1.87173,"retract_after_push.retract_height":0.1196,"retract_after_push.retract_speed":0.04792},"optimized_scores":{"best_composite_score":0.82333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":759.0,"contact_point_centroid":[0.165,0.04834,0.4175],"force_p95":21.31385,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.85414,"mean_force":13.47943,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0987,0.10443,0.39124]},{"body_a":"door_panel","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.10111,0.17429,0.5458],"force_p95":35.85605,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.70402,"mean_force":21.26612,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09978,0.2454,0.43958]},{"body_a":"door_panel","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.16494,0.14192,0.42402],"force_p95":28.51525,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.72143,"mean_force":21.36366,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09969,0.19941,0.40014]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.30124,0.17923,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09995,0.29896,0.41867]},{"body_a":"world","body_b":"door_panel","contact_count":988.0,"contact_point_centroid":[0.32398,0.10751,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09856,0.09812,0.39357]},{"body_a":"world","body_b":"door_panel","contact_count":448.0,"contact_point_centroid":[0.34298,0.07572,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.10083,0.07849,0.47293]}],"total_contact_groups":6},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10065,0.16574,0.46385],"hinge_angle":0.6124,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":41.85414,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":858.0,"raw_peak_contact_force":40.70402,"subtask_id":"reach_handle","tcp_end":[0.09972,0.18493,0.36916],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.95261,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09973,0.18479,0.36887],"tcp_start":[0.09972,0.18493,0.36916],"tcp_to_object_dist_end":0.42445,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1747.0,"raw_peak_contact_force":41.85414,"subtask_id":"open_door","tcp_end":[0.10048,0.00797,0.41327],"tcp_start":[0.09973,0.18479,0.36887],"tcp_to_object_dist_end":0.42539,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":448.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10065,0.16574,0.46385],"tcp_start":[0.10048,0.00797,0.41327],"tcp_to_object_dist_end":0.50274,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1875,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.05634,"approach_handle.arc_height":0.1308,"contact_handle.contact_force":14.78032,"contact_handle.contact_speed":0.01957,"push_door.push_distance":0.36216,"push_door.push_speed":0.11028,"push_door.push_time":3.12704,"retract_after_push.retract_height":0.10404,"retract_after_push.retract_speed":0.05622},"optimized_scores":{"best_composite_score":0.82333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":732.0,"contact_point_centroid":[0.16543,0.04504,0.41791],"force_p95":21.75386,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.74116,"mean_force":13.66708,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09865,0.10033,0.39172]},{"body_a":"door_panel","body_b":"link6","contact_count":60.0,"contact_point_centroid":[0.10152,0.16717,0.53009],"force_p95":34.06886,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.55265,"mean_force":22.33489,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0998,0.23701,0.4243]},{"body_a":"door_panel","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.16494,0.14269,0.41517],"force_p95":28.79881,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.3475,"mean_force":22.0335,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0997,0.20016,0.39129]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.16492,0.12867,0.39109],"force_p95":16.21425,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.52995,"mean_force":14.05581,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.09965,0.18608,0.3672]},{"body_a":"world","body_b":"door_panel","contact_count":644.0,"contact_point_centroid":[0.30146,0.17576,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09997,0.29739,0.40937]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30642,0.14874,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.09967,0.18647,0.3676]},{"body_a":"world","body_b":"door_panel","contact_count":904.0,"contact_point_centroid":[0.32258,0.11065,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09858,0.10465,0.39011]},{"body_a":"world","body_b":"door_panel","contact_count":460.0,"contact_point_centroid":[0.34526,0.0729,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.10161,0.07402,0.48279]}],"total_contact_groups":8},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1007,0.16881,0.46632],"hinge_angle":0.62929,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":43.74116,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":753.0,"raw_peak_contact_force":38.55265,"subtask_id":"reach_handle","tcp_end":[0.09971,0.18723,0.36851],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.95145,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":21.0,"raw_peak_contact_force":16.52995,"tcp_end":[0.09964,0.18579,0.36699],"tcp_start":[0.09971,0.18723,0.36851],"tcp_to_object_dist_end":0.42324,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1636.0,"raw_peak_contact_force":43.74116,"subtask_id":"open_door","tcp_end":[0.10184,-0.00191,0.41134],"tcp_start":[0.09964,0.18579,0.36699],"tcp_to_object_dist_end":0.42376,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":460.0,"raw_peak_contact_force":0.0,"tcp_end":[0.1007,0.16881,0.46632],"tcp_start":[0.10184,-0.00191,0.41134],"tcp_to_object_dist_end":0.50606,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07558,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.07561,"approach_handle.arc_height":0.11855,"contact_handle.contact_force":9.85609,"contact_handle.contact_speed":0.00768,"push_door.push_distance":0.28683,"push_door.push_speed":0.10831,"push_door.push_time":2.21378,"retract_after_push.retract_height":0.1271,"retract_after_push.retract_speed":0.06432},"optimized_scores":{"best_composite_score":0.82333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":142.0,"contact_point_centroid":[0.10085,0.1891,0.54763],"force_p95":41.14442,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.59461,"mean_force":18.2124,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09982,0.2629,0.44049]},{"body_a":"door_panel","body_b":"link7","contact_count":740.0,"contact_point_centroid":[0.1654,0.04475,0.41807],"force_p95":22.37572,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.31562,"mean_force":13.60519,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09869,0.10016,0.39186]},{"body_a":"door_panel","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.16495,0.14206,0.42168],"force_p95":33.71688,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.1612,"mean_force":22.96537,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09971,0.19952,0.3978]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16499,0.12745,0.39192],"force_p95":25.41655,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.98827,"mean_force":20.27109,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.09971,0.18492,0.36809]},{"body_a":"world","body_b":"door_panel","contact_count":704.0,"contact_point_centroid":[0.3011,0.18711,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09994,0.30014,0.41378]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30669,0.14776,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.09969,0.185,0.36799]},{"body_a":"world","body_b":"door_panel","contact_count":952.0,"contact_point_centroid":[0.32305,0.10936,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09869,0.10235,0.39162]},{"body_a":"world","body_b":"door_panel","contact_count":404.0,"contact_point_centroid":[0.3451,0.0731,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.10155,0.07963,0.47327]}],"total_contact_groups":8},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10077,0.1658,0.4637],"hinge_angle":0.62925,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":45.59461,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":45.59461,"subtask_id":"reach_handle","tcp_end":[0.09975,0.18547,0.3688],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.55391,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":25.98827,"tcp_end":[0.09967,0.18428,0.36731],"tcp_start":[0.09975,0.18547,0.3688],"tcp_to_object_dist_end":0.42286,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1692.0,"raw_peak_contact_force":43.31562,"subtask_id":"open_door","tcp_end":[0.10171,-0.00075,0.41153],"tcp_start":[0.09967,0.18428,0.36731],"tcp_to_object_dist_end":0.42391,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":404.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10077,0.1658,0.4637],"tcp_start":[0.10171,-0.00075,0.41153],"tcp_to_object_dist_end":0.50265,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```