## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.3867 | 0.73 | ❌ rejected |
| 11 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9  | 0.4961 | 0.73 | ❌ rejected |
| 10 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9  | -0.2024 | 0.01 | ❌ rejected |
| 9 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 10  | 0.0505 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 7  | 0.2544 | 0.91 | ✅ accepted |

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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

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
| `object` | offset from object initial position (0.5444299044764102, -0.025581934909493356, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.254) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: push_to_goal
  anchor: object
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.025
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.025
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_backoff:
      type: scalar
      range:
      - 0.015
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: pre_contact
- id: contact_nudge
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.005
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    nudge_distance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: contact_established
    when: after_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: pre_contact
- id: push_1
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
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 8.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.003
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.025, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.025, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_backoff: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **contact_nudge** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.005, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - nudge_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=contact_established, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.003, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.906
- **fitness_score**: 0.744  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1643 |
| descend_1 | 1.00 | 1.00 | 0.1127 |
| contact_nudge | 1.00 | 1.00 | 0.0429 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.0466 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.014, 0.146) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.014, 0.146)→(0.522, 0.015, 0.034) | (0.518, -0.020, 0.025)→(0.519, -0.022, 0.025) | 0.139→0.137 | 1.00 / 4.000 | 0.275 | 146.877 |
| contact_nudge | push | 1.00 / step_budget | (0.522, 0.015, 0.034)→(0.514, -0.024, 0.021) | (0.519, -0.022, 0.025)→(0.513, -0.059, 0.025) | 0.137→0.098 | 1.00 / 3.667 | 5.526 | 18.129 |
| push_1 | push | 0.00 / guard_failure | (0.495, -0.105, 0.016)→(0.495, -0.105, 0.016) | (0.513, -0.059, 0.025)→(0.502, -0.141, 0.025) | 0.098→0.015 | 1.00 / 2.667 | 19.666 | 35.861 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.105, 0.016)→(0.491, -0.104, 0.063) | (0.502, -0.141, 0.025)→(0.501, -0.142, 0.025) | 0.015→0.014 | 1.00 / 4.000 | 0.245 | 15.017 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.952
- lateral_force_integral: None
- approach_alignment: 0.680
- goal_progress: 0.952
- terminal_score: 0.952
- phase_score: 0.670
- phase_breakdown.pre_contact_score: 0.122
- phase_breakdown.push_to_goal_score: 0.905

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.783
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.952
- **Median Q (composite search score)**: 0.289
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.384


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62992,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09347,"approach_1.approach_offset":0.03716,"contact_nudge.nudge_distance":0.0062,"descend_1.descend_backoff":0.03811,"push_1.max_push_time":10.52869,"push_1.push_distance":0.14838,"push_1.push_speed":0.10897,"retract_1.lift_height":0.05943},"optimized_scores":{"best_composite_score":0.28916,"best_fitness_score":0.77916,"best_task_score":0.93711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.55504,-0.00092,0.0492],"force_p95":109.19369,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.30236,"mean_force":65.45085,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55131,0.00993,0.04814]},{"body_a":"world","body_b":"push_box","contact_count":1234.0,"contact_point_centroid":[0.54461,-0.02607,-2e-05],"force_p95":0.85526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.88551,"mean_force":1.37172,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54813,0.00901,0.08499]},{"body_a":"world","body_b":"push_box","contact_count":987.0,"contact_point_centroid":[0.51976,-0.11106,-7e-05],"force_p95":10.80131,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.2425,"mean_force":3.59665,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51947,-0.07009,0.01584]},{"body_a":"push_box","body_b":"link7","contact_count":97.0,"contact_point_centroid":[0.53065,-0.12738,0.05073],"force_p95":17.11414,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.37621,"mean_force":8.91695,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50414,-0.10913,0.01568]},{"body_a":"world","body_b":"push_box","contact_count":1794.0,"contact_point_centroid":[0.50346,-0.15927,-1e-05],"force_p95":0.40115,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.80702,"mean_force":0.27891,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49666,-0.11884,0.0426]},{"body_a":"attachment","body_b":"push_box","contact_count":489.0,"contact_point_centroid":[0.51935,-0.08538,0.02445],"force_p95":16.34027,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.15424,"mean_force":5.05363,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51803,-0.07351,0.01572]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52689,-0.14295,0.05102],"force_p95":19.43649,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.66683,"mean_force":5.90845,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50016,-0.11966,0.01598]},{"body_a":"attachment","body_b":"push_box","contact_count":436.0,"contact_point_centroid":[0.54277,-0.0216,0.02484],"force_p95":12.07098,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.81228,"mean_force":4.99161,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.54396,-0.00971,0.02452]},{"body_a":"world","body_b":"push_box","contact_count":1267.0,"contact_point_centroid":[0.53811,-0.04938,-5e-05],"force_p95":5.1724,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.28195,"mean_force":1.96933,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.54417,-0.0092,0.02474]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.5095,-0.13114,0.05074],"force_p95":2.65632,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.52392,"mean_force":0.92772,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49868,-0.11943,0.01837]},{"body_a":"world","body_b":"push_box","contact_count":1368.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52231,0.00394,0.21907]}],"total_contact_groups":11},"final_pose_error":0.01005,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5027,-0.15786,0.02499],"final_tcp_position":[0.49661,-0.1188,0.06613],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":112.30236,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.54697,0.00813,0.13573],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":720.0,"object_pos_end":[0.54499,-0.02671,0.02494],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13124,"object_to_goal_dist_start":0.13211,"object_z_max":0.02521,"peak_contact_force":0.24542,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1255.0,"raw_peak_contact_force":112.30236,"subtask_id":"pre_contact","tcp_end":[0.55251,0.01042,0.03378],"tcp_start":[0.54697,0.00813,0.13573],"tcp_to_object_dist_end":0.03891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.53281,-0.0648,0.02495],"object_pos_start":[0.54499,-0.02671,0.02494],"object_to_goal_dist_end":0.09129,"object_to_goal_dist_start":0.13124,"object_z_max":0.02512,"peak_contact_force":7.56949,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1703.0,"raw_peak_contact_force":18.81228,"subtask_id":"pre_contact","tcp_end":[0.53941,-0.02851,0.02031],"tcp_start":[0.55251,0.01042,0.03378],"tcp_to_object_dist_end":0.03718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":579.0,"n_steps_budget":870.0,"object_pos_end":[0.50428,-0.15691,0.02619],"object_pos_start":[0.53281,-0.0648,0.02495],"object_to_goal_dist_end":0.00821,"object_to_goal_dist_start":0.09129,"object_z_max":0.02629,"peak_contact_force":49.2425,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1573.0,"raw_peak_contact_force":49.2425,"subtask_id":"push_to_goal","tcp_end":[0.50035,-0.11954,0.01601],"tcp_start":[0.50039,-0.11942,0.01602],"tcp_to_object_dist_end":0.03894,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.5027,-0.15786,0.02499],"object_pos_start":[0.50426,-0.15705,0.02617],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.00832,"object_z_max":0.02617,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1836.0,"raw_peak_contact_force":26.80702,"tcp_end":[0.49661,-0.1188,0.06613],"tcp_start":[0.50035,-0.11954,0.01601],"tcp_to_object_dist_end":0.05706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58333,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09728,"approach_1.approach_offset":0.04368,"contact_nudge.nudge_distance":0.00485,"descend_1.descend_backoff":0.03976,"push_1.max_push_time":9.23342,"push_1.push_distance":0.20201,"push_1.push_speed":0.13524,"retract_1.lift_height":0.05852},"optimized_scores":{"best_composite_score":0.29279,"best_fitness_score":0.78279,"best_task_score":0.95152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.56581,-0.01025,0.04954],"force_p95":49.24283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.76224,"mean_force":29.00792,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56513,0.00157,0.04966]},{"body_a":"world","body_b":"push_box","contact_count":1262.0,"contact_point_centroid":[0.55467,-0.03527,-2e-05],"force_p95":0.25127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.63002,"mean_force":0.40755,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56276,0.00246,0.08523]},{"body_a":"attachment","body_b":"push_box","contact_count":298.0,"contact_point_centroid":[0.52639,-0.08242,0.01583],"force_p95":18.48452,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.05073,"mean_force":4.57395,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52824,-0.07062,0.0154]},{"body_a":"attachment","body_b":"push_box","contact_count":427.0,"contact_point_centroid":[0.55463,-0.0301,0.02441],"force_p95":12.20766,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.14486,"mean_force":4.68072,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.55599,-0.01823,0.02401]},{"body_a":"world","body_b":"push_box","contact_count":680.0,"contact_point_centroid":[0.52254,-0.10486,-5e-05],"force_p95":6.95138,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.75378,"mean_force":2.31435,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53022,-0.06714,0.01562]},{"body_a":"world","body_b":"push_box","contact_count":1295.0,"contact_point_centroid":[0.54577,-0.05615,-4e-05],"force_p95":4.62487,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.87206,"mean_force":1.80237,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.55631,-0.0176,0.02428]},{"body_a":"world","body_b":"push_box","contact_count":1908.0,"contact_point_centroid":[0.50327,-0.14471,-1e-05],"force_p95":0.24542,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27244,"mean_force":0.24771,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5056,-0.10594,0.03951]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50779,-0.11844,0.01527],"force_p95":0.92708,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97226,"mean_force":0.52046,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50925,-0.10656,0.01495]},{"body_a":"world","body_b":"push_box","contact_count":1412.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52962,0.00182,0.21987]}],"total_contact_groups":9},"final_pose_error":0.01026,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50333,-0.14481,0.02499],"final_tcp_position":[0.50547,-0.10585,0.06399],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":49.76224,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.56184,0.00375,0.13797],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":720.0,"object_pos_end":[0.55521,-0.03589,0.02496],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12677,"object_to_goal_dist_start":0.12728,"object_z_max":0.02501,"peak_contact_force":0.24447,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1269.0,"raw_peak_contact_force":49.76224,"subtask_id":"pre_contact","tcp_end":[0.5664,0.00121,0.03327],"tcp_start":[0.56184,0.00375,0.13797],"tcp_to_object_dist_end":0.03963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":510.0,"n_steps_budget":600.0,"object_pos_end":[0.54001,-0.07198,0.02499],"object_pos_start":[0.55521,-0.03589,0.02496],"object_to_goal_dist_end":0.08768,"object_to_goal_dist_start":0.12677,"object_z_max":0.02514,"peak_contact_force":0.00037,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1722.0,"raw_peak_contact_force":18.14486,"subtask_id":"pre_contact","tcp_end":[0.54984,-0.03636,0.02004],"tcp_start":[0.5664,0.00121,0.03327],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":930.0,"object_pos_end":[0.50424,-0.14285,0.02502],"object_pos_start":[0.54001,-0.07198,0.02499],"object_to_goal_dist_end":0.00831,"object_to_goal_dist_start":0.08768,"object_z_max":0.02558,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":978.0,"raw_peak_contact_force":26.05073,"subtask_id":"push_to_goal","tcp_end":[0.50928,-0.10649,0.01497],"tcp_start":[0.5094,-0.10634,0.015],"tcp_to_object_dist_end":0.03806,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.50333,-0.14481,0.02499],"object_pos_start":[0.50416,-0.14303,0.02509],"object_to_goal_dist_end":0.00617,"object_to_goal_dist_start":0.00811,"object_z_max":0.02515,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1910.0,"raw_peak_contact_force":1.27244,"tcp_end":[0.50547,-0.10585,0.06399],"tcp_start":[0.50928,-0.10649,0.01497],"tcp_to_object_dist_end":0.05517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56923,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12239,"approach_1.approach_offset":0.0378,"contact_nudge.nudge_distance":0.0068,"descend_1.descend_backoff":0.03413,"push_1.max_push_time":9.45771,"push_1.push_distance":0.26453,"push_1.push_speed":0.08586,"retract_1.lift_height":0.04942},"optimized_scores":{"best_composite_score":0.18117,"best_fitness_score":0.67117,"best_task_score":0.82814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":71.0,"contact_point_centroid":[0.45342,0.02479,0.04715],"force_p95":268.97787,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":278.56783,"mean_force":149.6316,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44661,0.03331,0.04595]},{"body_a":"world","body_b":"push_box","contact_count":1785.0,"contact_point_centroid":[0.45589,-0.00011,-6e-05],"force_p95":45.22125,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.98727,"mean_force":6.23572,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44612,0.03164,0.09851]},{"body_a":"world","body_b":"push_box","contact_count":998.0,"contact_point_centroid":[0.489,-0.09983,-7e-05],"force_p95":10.34723,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.28863,"mean_force":4.00728,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46374,-0.05148,0.01802]},{"body_a":"attachment","body_b":"push_box","contact_count":451.0,"contact_point_centroid":[0.47205,-0.05585,0.04942],"force_p95":16.40924,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.96505,"mean_force":6.86499,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46169,-0.04443,0.01817]},{"body_a":"attachment","body_b":"push_box","contact_count":425.0,"contact_point_centroid":[0.4538,0.0018,0.0463],"force_p95":13.74387,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.4312,"mean_force":5.63745,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.44845,0.01366,0.02667]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5124,-0.09528,0.0501],"force_p95":16.19426,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.97169,"mean_force":9.19739,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47479,-0.08935,0.01725]},{"body_a":"push_box","body_b":"link7","contact_count":117.0,"contact_point_centroid":[0.50097,-0.05935,0.05082],"force_p95":13.28448,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.42458,"mean_force":4.33141,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46388,-0.05246,0.01783]},{"body_a":"world","body_b":"push_box","contact_count":1491.0,"contact_point_centroid":[0.49826,-0.12314,-2e-05],"force_p95":0.25274,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.94774,"mean_force":0.26121,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47147,-0.08884,0.03755]},{"body_a":"world","body_b":"push_box","contact_count":838.0,"contact_point_centroid":[0.46305,-0.03978,-5e-05],"force_p95":7.03788,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.86747,"mean_force":3.26215,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.44812,0.01564,0.02731]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.48805,-0.09983,0.05015],"force_p95":0.78108,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86957,"mean_force":0.25934,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47471,-0.08939,0.01722]},{"body_a":"world","body_b":"push_box","contact_count":1120.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47572,0.01475,0.23415]}],"total_contact_groups":11},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49799,-0.1232,0.02499],"final_tcp_position":[0.47118,-0.08877,0.0574],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":278.56783,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.45051,0.03073,0.16562],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":900.0,"object_pos_end":[0.45574,-0.00315,0.02489],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15338,"object_to_goal_dist_start":0.1564,"object_z_max":0.02523,"peak_contact_force":0.33504,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1856.0,"raw_peak_contact_force":278.56783,"subtask_id":"pre_contact","tcp_end":[0.44632,0.03425,0.0347],"tcp_start":[0.45051,0.03073,0.16562],"tcp_to_object_dist_end":0.03979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.46748,-0.04084,0.02569],"object_pos_start":[0.45574,-0.00315,0.02489],"object_to_goal_dist_end":0.11391,"object_to_goal_dist_start":0.15338,"object_z_max":0.0258,"peak_contact_force":9.00887,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1263.0,"raw_peak_contact_force":17.4312,"subtask_id":"pre_contact","tcp_end":[0.45321,-0.00569,0.02199],"tcp_start":[0.44632,0.03425,0.0347],"tcp_to_object_dist_end":0.03811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.49868,-0.12211,0.02494],"object_pos_start":[0.46748,-0.04084,0.02569],"object_to_goal_dist_end":0.02792,"object_to_goal_dist_start":0.11391,"object_z_max":0.02622,"peak_contact_force":9.75526,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1566.0,"raw_peak_contact_force":32.28863,"subtask_id":"push_to_goal","tcp_end":[0.4748,-0.08932,0.01726],"tcp_start":[0.47475,-0.08924,0.01726],"tcp_to_object_dist_end":0.04128,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":600.0,"object_pos_end":[0.49799,-0.1232,0.02499],"object_pos_start":[0.49871,-0.12221,0.025],"object_to_goal_dist_end":0.02688,"object_to_goal_dist_start":0.02782,"object_z_max":0.02512,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1498.0,"raw_peak_contact_force":16.97169,"tcp_end":[0.47118,-0.08877,0.0574],"tcp_start":[0.4748,-0.08932,0.01726],"tcp_to_object_dist_end":0.05436,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```