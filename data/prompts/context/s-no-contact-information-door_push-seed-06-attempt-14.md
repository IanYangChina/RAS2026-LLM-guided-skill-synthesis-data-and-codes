## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9400 | 1.00 | ❌ rejected |
| 13 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.8771 | 0.90 | ❌ rejected |
| 12 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9400 | 1.00 | ❌ rejected |
| 11 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.9005 | 0.93 | ❌ rejected |
| 10 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.9400 | 1.00 | ❌ rejected |

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

## Parent Skill (Best Known, Q=0.940)

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
- id: push_progress
  anchor: fixture
  target_entity: hinge
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
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.05
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach_handle
- id: descend_contact
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
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: add
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: approach_handle
- id: push_handle
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
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
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: push_progress
- id: retract
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Last Evaluated Skill (Q=0.940)

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
- id: push_progress
  anchor: fixture
  target_entity: hinge
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
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.05
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach_handle
- id: descend_contact
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
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: add
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: approach_handle
- id: push_handle
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: push_progress
- id: retract
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.05, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (add)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_handle** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (add)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.940
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_handle | 1.00 | 0.1569 |
| descend_contact | 1.00 | 0.0026 |
| push_handle | 0.00 | 0.2792 |
| retract | 1.00 | 0.0808 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.250, 0.399) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| descend_contact | descend | 1.00 / force_exceeded | (0.100, 0.250, 0.399)→(0.100, 0.248, 0.397) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| push_handle | push | 0.00 / step_budget | (0.100, 0.248, 0.397)→(0.105, -0.031, 0.407) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| retract | retract | 1.00 / step_budget | (0.105, -0.031, 0.407)→(0.105, -0.027, 0.487) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.940
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47674,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.06515,"descend_contact.descend_speed":0.05733,"descend_contact.force_threshold":11.35255,"push_handle.push_distance":0.14516,"push_handle.push_speed":0.03962},"optimized_scores":{"best_composite_score":0.94,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":652.0,"contact_point_centroid":[0.1673,0.00403,0.44017],"force_p95":28.18164,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.79179,"mean_force":14.40579,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10031,0.05827,0.41214]},{"body_a":"door_panel","body_b":"link6","contact_count":32.0,"contact_point_centroid":[0.10191,0.16205,0.50093],"force_p95":22.39317,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.13102,"mean_force":15.1945,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.1003,0.23087,0.39497]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.17956,-0.03938,0.43664],"force_p95":20.47784,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.75316,"mean_force":7.58439,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.10445,0.00353,0.41269]},{"body_a":"door_panel","body_b":"link6","contact_count":52.0,"contact_point_centroid":[0.10048,0.18421,0.50612],"force_p95":20.29171,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.42113,"mean_force":11.35163,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10025,0.25809,0.39886]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.101,0.17197,0.5048],"force_p95":12.75723,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.42867,"mean_force":6.71433,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.10016,0.24343,0.39832]},{"body_a":"world","body_b":"door_panel","contact_count":352.0,"contact_point_centroid":[0.30023,0.18635,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10019,0.31909,0.38322]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30121,0.17585,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.10012,0.2432,0.39818]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.33144,0.09574,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10024,0.06797,0.41122]},{"body_a":"world","body_b":"door_panel","contact_count":164.0,"contact_point_centroid":[0.34555,0.07255,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.10419,0.009,0.45181]}],"total_contact_groups":9},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1041,0.00764,0.49341],"hinge_angle":0.6369,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":365.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_handle","tcp_end":[0.10025,0.24451,0.39916],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47871,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":21.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_handle","tcp_end":[0.10007,0.24225,0.39737],"tcp_start":[0.10025,0.24451,0.39916],"tcp_to_object_dist_end":0.47603,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push_handle","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_progress","tcp_end":[0.10445,0.00352,0.41269],"tcp_start":[0.10007,0.24225,0.39737],"tcp_to_object_dist_end":0.42571,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":208.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.1041,0.00764,0.49341],"tcp_start":[0.10445,0.00352,0.41269],"tcp_to_object_dist_end":0.50433,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.67347,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.05658,"descend_contact.descend_speed":0.05436,"descend_contact.force_threshold":14.15279,"push_handle.push_distance":0.18235,"push_handle.push_speed":0.06612},"optimized_scores":{"best_composite_score":0.94,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":581.0,"contact_point_centroid":[0.17745,-0.01191,0.43312],"force_p95":32.74958,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.39284,"mean_force":15.66701,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10395,0.03208,0.40883]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.1986,-0.06297,0.47916],"force_p95":24.20071,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.42844,"mean_force":21.90925,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.10673,-0.05257,0.47024]},{"body_a":"door_panel","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.10266,0.15462,0.50221],"force_p95":22.46818,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.21847,"mean_force":15.73325,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10121,0.22254,0.39652]},{"body_a":"door_panel","body_b":"link6","contact_count":47.0,"contact_point_centroid":[0.10105,0.17336,0.50642],"force_p95":19.72934,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.67511,"mean_force":10.92404,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10112,0.24576,0.3995]},{"body_a":"world","body_b":"door_panel","contact_count":372.0,"contact_point_centroid":[0.30073,0.18037,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10063,0.31688,0.38298]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10183,0.16217,0.50559],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.10119,0.23234,0.39947]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.33828,0.0874,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10443,0.03733,0.40711]},{"body_a":"world","body_b":"door_panel","contact_count":192.0,"contact_point_centroid":[0.35608,0.06076,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.10681,-0.0535,0.44112]}],"total_contact_groups":8},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10673,-0.05497,0.48354],"hinge_angle":0.71927,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_handle","tcp_end":[0.10119,0.23234,0.39947],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47307,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":18.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_handle","tcp_end":[0.10103,0.2304,0.39796],"tcp_start":[0.10119,0.23234,0.39947],"tcp_to_object_dist_end":0.47081,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push_handle","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_progress","tcp_end":[0.10709,-0.05912,0.40293],"tcp_start":[0.10103,0.2304,0.39796],"tcp_to_object_dist_end":0.42109,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":209.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.10673,-0.05497,0.48354],"tcp_start":[0.10709,-0.05912,0.40293],"tcp_to_object_dist_end":0.49822,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.40854,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.05268,"descend_contact.descend_speed":0.03281,"descend_contact.force_threshold":13.25436,"push_handle.push_distance":0.24337,"push_handle.push_speed":0.04804},"optimized_scores":{"best_composite_score":0.94,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":565.0,"contact_point_centroid":[0.17281,-0.00597,0.43382],"force_p95":31.47381,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.85426,"mean_force":16.01296,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10049,0.04047,0.40857]},{"body_a":"door_panel","body_b":"link6","contact_count":57.0,"contact_point_centroid":[0.10029,0.21117,0.50409],"force_p95":29.30243,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.26421,"mean_force":16.98512,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09955,0.28953,0.39535]},{"body_a":"door_panel","body_b":"link6","contact_count":49.0,"contact_point_centroid":[0.10103,0.17594,0.49959],"force_p95":21.74076,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.98288,"mean_force":16.00004,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.09968,0.24685,0.39258]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10004,0.19698,0.50433],"force_p95":13.99104,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.72741,"mean_force":7.3637,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09934,0.27269,0.39636]},{"body_a":"world","body_b":"door_panel","contact_count":340.0,"contact_point_centroid":[0.29978,0.20021,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09982,0.33458,0.38056]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30009,0.18829,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.09924,0.27265,0.39648]},{"body_a":"world","body_b":"door_panel","contact_count":756.0,"contact_point_centroid":[0.33602,0.08989,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.10075,0.0465,0.40788]},{"body_a":"world","body_b":"door_panel","contact_count":164.0,"contact_point_centroid":[0.35273,0.06431,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.10468,-0.03109,0.44253]}],"total_contact_groups":8},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10461,-0.03273,0.48527],"hinge_angle":0.6911,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":313.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_handle","tcp_end":[0.09946,0.27361,0.39701],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49231,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_handle","tcp_end":[0.09921,0.27166,0.39562],"tcp_start":[0.09946,0.27361,0.39701],"tcp_to_object_dist_end":0.49006,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"push_handle","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_progress","tcp_end":[0.10494,-0.03684,0.40454],"tcp_start":[0.09921,0.27166,0.39562],"tcp_to_object_dist_end":0.41955,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":208.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.10461,-0.03273,0.48527],"tcp_start":[0.10494,-0.03684,0.40454],"tcp_to_object_dist_end":0.4975,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```