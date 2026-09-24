## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.6264 | 0.91 | ✅ accepted |
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1901 | 0.47 | ❌ rejected |
| 2 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1918 | 0.47 | ✅ accepted |
| 1 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |
| 0 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen initial hinge angle: 0.524 rad
- target_hinge_angle: -0.083 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
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
  target_hinge_angle_rad: -0.083
  realized_scene_sha256: 6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.906, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.626) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_handle
  anchor: fixture
  weight: 0.3
- id: push_door
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
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
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
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_detected
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: reach_handle
- id: push_door_closed
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
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.15
  parameters:
    max_push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
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
  guards:
  - id: force_below_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_detected, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed
- **push_door_closed** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.15
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_below_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.626
- **task_score** (E): 0.906
- **fitness_score**: 0.906  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.33 | 0.67 | 0.1713 |
| descend_to_handle | 1.00 | 1.00 | 0.0905 |
| push_door_closed | 0.00 | 0.67 | 0.0740 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.260, 0.449) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 21.331 |
| descend_to_handle | descend | 1.00 / step_budget | (0.102, 0.173, 0.362)→(0.120, 0.092, 0.397) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 9.506 | 36.945 |
| push_door_closed | push | 0.00 / guard_failure | (0.120, 0.092, 0.397)→(0.106, 0.108, 0.468) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 1.603 | 97.295 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.615
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.458


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
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.08321},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.05512,"average_mean_iterations":14.48031,"average_solve_count":127.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.07072,"descend_to_handle.descend_speed":0.04488,"push_door_closed.max_push_time":2.15706,"push_door_closed.push_distance":0.30919,"push_door_closed.push_speed":0.07898},"optimized_scores":{"best_composite_score":0.54435,"best_fitness_score":0.82435,"best_task_score":0.82435},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.12424,0.0635,0.54566],"force_p95":105.56833,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.56833,"mean_force":105.56833,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.09304,0.1472,0.42041]},{"body_a":"door_panel","body_b":"link6","contact_count":24.0,"contact_point_centroid":[0.10114,0.22998,0.53888],"force_p95":25.34421,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.19391,"mean_force":20.05473,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09948,0.31084,0.42964]},{"body_a":"door_panel","body_b":"link7","contact_count":524.0,"contact_point_centroid":[0.16805,0.11408,0.38001],"force_p95":17.63408,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.44694,"mean_force":13.23849,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10268,0.17118,0.35567]},{"body_a":"door_panel","body_b":"link6","contact_count":483.0,"contact_point_centroid":[0.10088,0.18641,0.49864],"force_p95":22.16229,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.47869,"mean_force":15.55432,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09899,0.25934,0.39121]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.17169,0.08106,0.39869],"force_p95":10.82927,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.82927,"mean_force":10.82927,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.10643,0.13822,0.37407]},{"body_a":"world","body_b":"door_panel","contact_count":676.0,"contact_point_centroid":[0.29985,0.20642,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09964,0.35911,0.39021]},{"body_a":"world","body_b":"door_panel","contact_count":1552.0,"contact_point_centroid":[0.30469,0.16375,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10071,0.21926,0.37552]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.31539,0.12242,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.10198,0.14022,0.39023]}],"total_contact_groups":8},"final_pose_error":0.22205,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09254,0.14777,0.42251],"hinge_angle":0.34875,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":105.56833,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":35.19391,"subtask_id":"reach_handle","tcp_end":[0.09937,0.30767,0.43148],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53918,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1570.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.33512,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2559.0,"raw_peak_contact_force":34.44694,"subtask_id":"reach_handle","tcp_end":[0.10643,0.13822,0.37407],"tcp_start":[0.09922,0.21146,0.35266],"tcp_to_object_dist_end":0.41275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":33.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.39612,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":105.56833,"subtask_id":"push_door","tcp_end":[0.09254,0.14777,0.42251],"tcp_start":[0.10643,0.13822,0.37407],"tcp_to_object_dist_end":0.45707,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.14464},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":22.0,"average_failure_rate":0.088,"average_mean_iterations":20.9,"average_solve_count":250.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.03643,"descend_to_handle.descend_speed":0.029,"push_door_closed.max_push_time":1.72623,"push_door_closed.push_distance":0.2898,"push_door_closed.push_speed":0.04776},"optimized_scores":{"best_composite_score":0.72,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.14294,0.01981,0.5606],"force_p95":148.7642,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.7642,"mean_force":148.7642,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.09126,0.13313,0.56327]},{"body_a":"door_panel","body_b":"link7","contact_count":893.0,"contact_point_centroid":[0.1724,0.09382,0.40166],"force_p95":16.65814,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.00529,"mean_force":13.45379,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10692,0.15099,0.37622]},{"body_a":"door_panel","body_b":"link6","contact_count":229.0,"contact_point_centroid":[0.10054,0.21387,0.55396],"force_p95":23.74616,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.799,"mean_force":18.09873,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10032,0.29311,0.44507]},{"body_a":"door_panel","body_b":"link6","contact_count":264.0,"contact_point_centroid":[0.10154,0.16708,0.53522],"force_p95":20.21431,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.09032,"mean_force":14.58505,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10026,0.23714,0.42872]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.18328,0.03953,0.42848],"force_p95":14.88793,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.89549,"mean_force":14.81988,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.11776,0.09673,0.39903]},{"body_a":"world","body_b":"door_panel","contact_count":856.0,"contact_point_centroid":[0.29997,0.20584,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10009,0.34072,0.40815]},{"body_a":"world","body_b":"door_panel","contact_count":1788.0,"contact_point_centroid":[0.30948,0.14439,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10458,0.18027,0.39343]},{"body_a":"world","body_b":"door_panel","contact_count":124.0,"contact_point_centroid":[0.32611,0.10069,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.09693,0.13065,0.48637]}],"total_contact_groups":8},"final_pose_error":0.27262,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09139,0.13296,0.56348],"hinge_angle":0.46736,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":148.7642,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1085.0,"raw_peak_contact_force":28.799,"subtask_id":"reach_handle","tcp_end":[0.10061,0.26287,0.45923],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1842.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.62381,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2945.0,"raw_peak_contact_force":35.00529,"subtask_id":"reach_handle","tcp_end":[0.11777,0.09675,0.39897],"tcp_start":[0.10054,0.17367,0.3563],"tcp_to_object_dist_end":0.42709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.41421,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":127.0,"raw_peak_contact_force":148.7642,"subtask_id":"push_door","tcp_end":[0.09139,0.13296,0.56348],"tcp_start":[0.11777,0.09675,0.39897],"tcp_to_object_dist_end":0.58612,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.15466},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.032,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.09876,"descend_to_handle.descend_speed":0.04829,"push_door_closed.max_push_time":1.35738,"push_door_closed.push_distance":0.14036,"push_door_closed.push_speed":0.08145},"optimized_scores":{"best_composite_score":0.61473,"best_fitness_score":0.89473,"best_task_score":0.89473},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":1311.0,"contact_point_centroid":[0.1799,0.06586,0.4288],"force_p95":16.87768,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.38298,"mean_force":13.30607,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.11483,0.12345,0.4019]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.1978,-0.01699,0.45078],"force_p95":37.55314,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.55314,"mean_force":37.55314,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.13525,0.04221,0.41887]},{"body_a":"door_panel","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.10443,0.1407,0.55884],"force_p95":19.86544,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.85302,"mean_force":10.20539,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10505,0.20825,0.45334]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.30379,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10222,0.311,0.40886]},{"body_a":"world","body_b":"door_panel","contact_count":1636.0,"contact_point_centroid":[0.3179,0.12074,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.11251,0.13476,0.4027]}],"total_contact_groups":5},"final_pose_error":0.09889,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13532,0.04201,0.41894],"hinge_angle":0.62349,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":41.38298,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10516,0.21016,0.45584],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51285,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1908.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.56026,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2956.0,"raw_peak_contact_force":41.38298,"subtask_id":"reach_handle","tcp_end":[0.13525,0.04221,0.41887],"tcp_start":[0.10757,0.13392,0.37568],"tcp_to_object_dist_end":0.44218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":37.55314,"subtask_id":"push_door","tcp_end":[0.13532,0.04201,0.41894],"tcp_start":[0.13525,0.04221,0.41887],"tcp_to_object_dist_end":0.44225,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```