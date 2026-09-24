## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | 3 | 0.7900 | 1.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | 3 | 0.7900 | 1.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | 3 | 0.7900 | 1.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | 3 | 0.7900 | 1.00 | ✅ accepted |
| 0 | descend → insert → grasp → approach | linear_cartesian | impedance_motion | — | linear_cartesian | position_control | admittance_control | position_control | position_control | contact_detected | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2647 | 0.31 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`
- Frozen initial hinge angle: 0.044 rad
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
  frozen_initial_hinge_angle_rad: 0.0437
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57

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

## Parent Skill (Best Known, Q=0.790)

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
- id: approach_to_handle
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
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: contact_handle
  type: descend
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
  subtask_id: reach_handle
- id: push_door
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: hinge_progress_check
    when: during_phase
    predicate: hinge_delta_reached
    threshold: 0.45
    on_failure: continue
  subtask_id: open_door
- id: retract_from_handle
  type: retract
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Last Evaluated Skill (Q=0.790)

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
- id: approach_to_handle
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
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: contact_handle
  type: descend
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
  subtask_id: reach_handle
- id: push_door
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: open_door
- id: retract_from_handle
  type: retract
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_from_handle** (`retract`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.790
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_handle | 1.00 | 0.33 | 0.2218 |
| contact_handle | 0.33 | 0.33 | 0.0788 |
| push_door | 1.00 | 0.67 | 0.1553 |
| retract_from_handle | 1.00 | 1.00 | 0.1413 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.182, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 4.534 | 33.723 |
| contact_handle | descend | 0.33 / step_budget | (0.102, 0.182, 0.394)→(0.116, 0.106, 0.392) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 0.000 |
| push_door | push | 1.00 / time_limit | (0.116, 0.106, 0.392)→(0.154, 0.176, 0.525) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 6.082 | 37.861 |
| retract_from_handle | retract | 1.00 / step_budget | (0.154, 0.176, 0.525)→(0.146, 0.037, 0.502) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 8.626 | 35.314 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.790
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.249


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21774,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_handle.speed":0.14851,"push_door.push_distance":0.16426,"push_door.push_duration":1.59112},"optimized_scores":{"best_composite_score":0.79,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":150.0,"contact_point_centroid":[0.10181,0.16381,0.48863],"force_p95":23.23148,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.92846,"mean_force":13.85765,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.10062,0.23418,0.38255]},{"body_a":"door_panel","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.21826,0.01815,0.54211],"force_p95":35.3362,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.66138,"mean_force":23.54831,"phase_index":3.0,"phase_name":"retract_from_handle","phase_type":"retract","tcp_position_centroid":[0.15261,0.07524,0.51294]},{"body_a":"door_panel","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.16621,0.1342,0.4156],"force_p95":18.49549,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.87661,"mean_force":13.41898,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.10093,0.1916,0.39175]},{"body_a":"door_panel","body_b":"link7","contact_count":432.0,"contact_point_centroid":[0.17452,0.07524,0.4108],"force_p95":21.95328,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.52486,"mean_force":14.17888,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10893,0.13251,0.38534]},{"body_a":"world","body_b":"door_panel","contact_count":864.0,"contact_point_centroid":[0.30175,0.17438,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.10036,0.28259,0.37237]},{"body_a":"world","body_b":"door_panel","contact_count":560.0,"contact_point_centroid":[0.31701,0.11958,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10877,0.133,0.38472]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.18382,0.03795,0.42828],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11837,0.09543,0.39921]},{"body_a":"world","body_b":"door_panel","contact_count":836.0,"contact_point_centroid":[0.32562,0.10156,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13781,0.13055,0.46653]},{"body_a":"world","body_b":"door_panel","contact_count":240.0,"contact_point_centroid":[0.33377,0.08963,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_from_handle","phase_type":"retract","tcp_position_centroid":[0.15367,0.09726,0.51771]}],"total_contact_groups":9},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15031,0.02642,0.50276],"hinge_angle":0.68198,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.92846,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.6026,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":32.52486,"subtask_id":"reach_handle","tcp_end":[0.10109,0.1716,0.39614],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":838.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.11835,0.09542,0.3992],"tcp_start":[0.10109,0.1716,0.39614],"tcp_to_object_dist_end":0.42717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":378.0,"raw_peak_contact_force":36.66138,"subtask_id":"open_door","tcp_end":[0.15681,0.16491,0.53287],"tcp_start":[0.11835,0.09542,0.3992],"tcp_to_object_dist_end":0.57943,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.36899,"phase_name":"retract_from_handle","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1166.0,"raw_peak_contact_force":36.92846,"tcp_end":[0.15031,0.02642,0.50276],"tcp_start":[0.15681,0.16491,0.53287],"tcp_to_object_dist_end":0.52541,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95161,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_handle.speed":0.11422,"push_door.push_distance":0.1595,"push_door.push_duration":1.77101},"optimized_scores":{"best_composite_score":0.79,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":136.0,"contact_point_centroid":[0.20047,0.06019,0.52568],"force_p95":34.69155,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.3438,"mean_force":22.0451,"phase_index":3.0,"phase_name":"retract_from_handle","phase_type":"retract","tcp_position_centroid":[0.13418,0.1168,0.49922]},{"body_a":"door_panel","body_b":"link6","contact_count":313.0,"contact_point_centroid":[0.10087,0.186,0.49026],"force_p95":21.62058,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.10211,"mean_force":16.04737,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.0992,0.25968,0.38321]},{"body_a":"door_panel","body_b":"link7","contact_count":412.0,"contact_point_centroid":[0.16737,0.11822,0.39982],"force_p95":19.75153,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.09322,"mean_force":14.05061,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10207,0.17554,0.37574]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.16458,0.15612,0.419],"force_p95":13.80221,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.81146,"mean_force":13.66186,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09927,0.21351,0.39511]},{"body_a":"world","body_b":"door_panel","contact_count":852.0,"contact_point_centroid":[0.30037,0.19132,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09937,0.30137,0.37265]},{"body_a":"world","body_b":"door_panel","contact_count":596.0,"contact_point_centroid":[0.30863,0.14235,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10215,0.1748,0.37551]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.31441,0.1248,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12331,0.17168,0.43192]},{"body_a":"world","body_b":"door_panel","contact_count":308.0,"contact_point_centroid":[0.31875,0.1161,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_from_handle","phase_type":"retract","tcp_position_centroid":[0.13727,0.1477,0.4997]}],"total_contact_groups":8},"final_pose_error":0.01962,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1297,0.07191,0.49888],"hinge_angle":0.54635,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":40.3438,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":34.09322,"subtask_id":"reach_handle","tcp_end":[0.09927,0.21294,0.39526],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10595,0.14056,0.37198],"tcp_start":[0.09927,0.21294,0.39526],"tcp_to_object_dist_end":0.41152,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.24619,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":444.0,"raw_peak_contact_force":40.3438,"subtask_id":"open_door","tcp_end":[0.1432,0.20778,0.50142],"tcp_start":[0.10595,0.14056,0.37198],"tcp_to_object_dist_end":0.56134,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":312.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.5104,"phase_name":"retract_from_handle","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1170.0,"raw_peak_contact_force":39.10211,"tcp_end":[0.1297,0.07191,0.49888],"tcp_start":[0.1432,0.20778,0.50142],"tcp_to_object_dist_end":0.52046,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09396,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_handle.speed":0.09093,"push_door.push_distance":0.21126,"push_door.push_duration":1.80329},"optimized_scores":{"best_composite_score":0.79,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.22419,0.00748,0.54653],"force_p95":33.32323,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.57818,"mean_force":22.34634,"phase_index":3.0,"phase_name":"retract_from_handle","phase_type":"retract","tcp_position_centroid":[0.159,0.06489,0.51688]},{"body_a":"door_panel","body_b":"link7","contact_count":444.0,"contact_point_centroid":[0.1788,0.06474,0.41252],"force_p95":20.83199,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.55049,"mean_force":14.35386,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.11312,0.12199,0.38651]},{"body_a":"door_panel","body_b":"link6","contact_count":40.0,"contact_point_centroid":[0.10378,0.14579,0.48758],"force_p95":28.49177,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.91029,"mean_force":12.50187,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.10386,0.21423,0.38198]},{"body_a":"door_panel","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.16979,0.12721,0.41136],"force_p95":25.49174,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.62328,"mean_force":15.21056,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.10452,0.18466,0.38755]},{"body_a":"world","body_b":"door_panel","contact_count":1084.0,"contact_point_centroid":[0.30364,0.16151,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.10226,0.28358,0.36908]},{"body_a":"world","body_b":"door_panel","contact_count":572.0,"contact_point_centroid":[0.32015,0.11296,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.11337,0.12097,0.38697]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.32931,0.0953,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1432,0.11957,0.47465]},{"body_a":"world","body_b":"door_panel","contact_count":308.0,"contact_point_centroid":[0.33766,0.0838,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_from_handle","phase_type":"retract","tcp_position_centroid":[0.15976,0.08507,0.52224]}],"total_contact_groups":8},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15712,0.01372,0.50359],"hinge_angle":0.72062,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.57818,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1016.0,"raw_peak_contact_force":34.55049,"subtask_id":"reach_handle","tcp_end":[0.10506,0.16169,0.39192],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":868.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.12272,0.08253,0.4037],"tcp_start":[0.10506,0.16169,0.39192],"tcp_to_object_dist_end":0.42993,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":460.0,"raw_peak_contact_force":36.57818,"subtask_id":"open_door","tcp_end":[0.16227,0.15402,0.54122],"tcp_start":[0.12272,0.08253,0.4037],"tcp_to_object_dist_end":0.58564,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_from_handle","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1279.0,"raw_peak_contact_force":29.91029,"tcp_end":[0.15712,0.01372,0.50359],"tcp_start":[0.16227,0.15402,0.54122],"tcp_to_object_dist_end":0.52771,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```