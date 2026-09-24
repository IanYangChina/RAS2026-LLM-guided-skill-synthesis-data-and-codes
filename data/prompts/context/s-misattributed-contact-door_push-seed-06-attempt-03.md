## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.8734 | 0.71 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.5020 | 0.40 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.6133 | 0.79 | ✅ accepted |
| 0 | rotate → align → lift → push → approach → approach → descend → grasp | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | position_control | position_control | position_control | force_threshold_switch | position_control | admittance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.0354 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.793, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.873) — your mutation base

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
- id: push_goal
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none
  subtask_id: reach_handle
- id: descend_to_handle
  type: descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
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
      distance: 0.25
      axis: world_x
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    hinge_angle_threshold:
      type: scalar
      range:
      - 0.4
      - 0.55
      default: 0.5
      binds_to:
      - path: guards.hinge_check.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: hinge_check
    when: during_phase
    predicate: hinge_delta_reached
    threshold: 0.5
    on_failure: continue
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_door** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - hinge_angle_threshold: status=consumed; consumers=guards.hinge_check.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=hinge_check, when=during_phase, predicate=hinge_delta_reached, on_failure=continue, threshold=0.5
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=25.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.873
- **task_score** (E): 0.714
- **fitness_score**: 0.714  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.389
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2487 |
| contact_handle | 1.00 | 0.33 | 0.0019 |
| push_door | 0.33 | 1.00 | 0.1177 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.151, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 15.105 | 14.549 |
| contact_handle | contact | 1.00 / force_exceeded | (0.100, 0.151, 0.349)→(0.101, 0.149, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 27.757 |
| push_door | push | 0.33 / guard_failure | (0.101, 0.149, 0.348)→(0.149, 0.137, 0.455) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 4.263 | 29.993 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.688
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.769
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.769
- **Median Q (composite search score)**: 0.872
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.406


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86316,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_handle.contact_force_threshold":12.96719,"push_door.push_duration":0.61654,"push_door.push_speed":0.07611,"push_door.push_stroke":0.17662},"optimized_scores":{"best_composite_score":0.958,"best_fitness_score":0.688,"best_task_score":0.688},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":374.0,"contact_point_centroid":[0.14774,0.14343,0.39808],"force_p95":25.56783,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.33531,"mean_force":13.64789,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10004,0.20125,0.34845]},{"body_a":"door_panel","body_b":"link7","contact_count":226.0,"contact_point_centroid":[0.16766,0.08159,0.45768],"force_p95":25.60856,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.92258,"mean_force":12.7832,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1256,0.13981,0.40402]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.14216,0.08534,0.40198],"force_p95":20.2351,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.51022,"mean_force":9.86021,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10021,0.14377,0.34851]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.30255,0.17306,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09986,0.26535,0.34818]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.31263,0.12934,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10026,0.14359,0.34846]},{"body_a":"world","body_b":"door_panel","contact_count":980.0,"contact_point_centroid":[0.31502,0.12339,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12515,0.13984,0.40301]}],"total_contact_groups":6},"final_pose_error":0.04708,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15011,0.13772,0.45909],"hinge_angle":0.37383,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.33531,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.00944,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":21.51022,"subtask_id":"reach_handle","tcp_end":[0.10016,0.14409,0.3486],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.39028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1206.0,"raw_peak_contact_force":26.92258,"tcp_end":[0.1005,0.1431,0.34835],"tcp_start":[0.10016,0.14409,0.3486],"tcp_to_object_dist_end":0.38977,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1402.0,"raw_peak_contact_force":29.33531,"subtask_id":"push_goal","tcp_end":[0.15011,0.13772,0.45909],"tcp_start":[0.1005,0.1431,0.34835],"tcp_to_object_dist_end":0.50226,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86316,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_handle.contact_force_threshold":3.81803,"push_door.push_duration":3.70796,"push_door.push_speed":0.07731,"push_door.push_stroke":0.15426},"optimized_scores":{"best_composite_score":0.7902,"best_fitness_score":0.68686,"best_task_score":0.68686},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":338.0,"contact_point_centroid":[0.14778,0.13784,0.39849],"force_p95":25.50224,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.80607,"mean_force":13.84714,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10072,0.19586,0.34848]},{"body_a":"door_panel","body_b":"link7","contact_count":265.0,"contact_point_centroid":[0.1705,0.07611,0.46028],"force_p95":25.87993,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.27494,"mean_force":13.46731,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12867,0.13455,0.4067]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.30249,0.1712,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10027,0.26904,0.34815]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14276,0.08492,0.40199],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10102,0.14362,0.34861]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.31617,0.12075,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12648,0.13514,0.40199]}],"total_contact_groups":5},"final_pose_error":0.02621,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15299,0.12823,0.4591],"hinge_angle":0.40358,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.80607,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.16981,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10102,0.14362,0.34861],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.39033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1189.0,"raw_peak_contact_force":28.27494,"tcp_end":[0.10129,0.14289,0.3484],"tcp_start":[0.10102,0.14362,0.34861],"tcp_to_object_dist_end":0.38994,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1322.0,"raw_peak_contact_force":28.80607,"subtask_id":"push_goal","tcp_end":[0.15299,0.12823,0.4591],"tcp_start":[0.10129,0.14289,0.3484],"tcp_to_object_dist_end":0.50063,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83146,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_handle.contact_force_threshold":12.88154,"push_door.push_duration":1.56947,"push_door.push_speed":0.0787,"push_door.push_stroke":0.15287},"optimized_scores":{"best_composite_score":0.87189,"best_fitness_score":0.76855,"best_task_score":0.76855},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":407.0,"contact_point_centroid":[0.14863,0.16448,0.39613],"force_p95":25.33668,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.83868,"mean_force":13.28916,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09938,0.22202,0.34828]},{"body_a":"door_panel","body_b":"link7","contact_count":238.0,"contact_point_centroid":[0.16505,0.09548,0.44643],"force_p95":25.89965,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.07356,"mean_force":13.02503,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12061,0.15324,0.39421]},{"body_a":"door_panel","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.14451,0.10415,0.40023],"force_p95":20.69782,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.13579,"mean_force":10.92412,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10016,0.1621,0.34823]},{"body_a":"door_panel","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.10075,0.22252,0.47139],"force_p95":13.24701,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.89872,"mean_force":8.9277,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09939,0.27742,0.34795]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.30135,0.18627,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09943,0.27983,0.34809]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30945,0.13844,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10004,0.16239,0.34827]},{"body_a":"world","body_b":"door_panel","contact_count":816.0,"contact_point_centroid":[0.31245,0.12995,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12302,0.15247,0.39991]}],"total_contact_groups":7},"final_pose_error":0.03781,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.14287,0.14641,0.44697],"hinge_angle":0.34232,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":31.83868,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.13579,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":53.0,"raw_peak_contact_force":22.13579,"subtask_id":"reach_handle","tcp_end":[0.09944,0.16402,0.34864],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.39792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":33.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1054.0,"raw_peak_contact_force":28.07356,"tcp_end":[0.10082,0.16056,0.34803],"tcp_start":[0.09944,0.16402,0.34864],"tcp_to_object_dist_end":0.39632,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.78903,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1417.0,"raw_peak_contact_force":31.83868,"subtask_id":"push_goal","tcp_end":[0.14287,0.14641,0.44697],"tcp_start":[0.10082,0.16056,0.34803],"tcp_to_object_dist_end":0.49156,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```