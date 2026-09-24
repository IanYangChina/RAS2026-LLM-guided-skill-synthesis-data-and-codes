## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.2544 | 0.91 | ✅ accepted |
| 12 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.3867 | 0.73 | ❌ rejected |
| 11 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9  | 0.4961 | 0.73 | ❌ rejected |
| 10 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9  | -0.2024 | 0.01 | ❌ rejected |
| 9 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 10  | 0.2541 | 0.91 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.907, which indicates the subtask decomposition is already effective.
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
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.907
- **fitness_score**: 0.744  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1676 |
| descend_1 | 1.00 | 1.00 | 0.1100 |
| contact_nudge | 1.00 | 1.00 | 0.0445 |
| push_1 | 1.00 | 1.00 | 0.0996 |
| retract_1 | 1.00 | 1.00 | 0.0478 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.018, 0.144) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.518, 0.018, 0.144)→(0.521, 0.015, 0.034) | (0.518, -0.020, 0.025)→(0.518, -0.022, 0.025) | 0.139→0.137 | 1.00 / 4.333 | 8.920 | 167.481 |
| contact_nudge | push | 1.00 / step_budget | (0.521, 0.015, 0.034)→(0.513, -0.025, 0.021) | (0.518, -0.022, 0.025)→(0.513, -0.061, 0.025) | 0.137→0.095 | 1.00 / 3.333 | 2.492 | 19.317 |
| push_1 | push | 1.00 / time_limit | (0.513, -0.025, 0.021)→(0.497, -0.117, 0.017) | (0.513, -0.061, 0.025)→(0.508, -0.149, 0.026) | 0.095→0.014 | 1.00 / 3.333 | 16.617 | 32.040 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.117, 0.017)→(0.493, -0.117, 0.064) | (0.508, -0.149, 0.026)→(0.507, -0.149, 0.025) | 0.014→0.013 | 1.00 / 4.000 | 0.245 | 23.119 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.698
- goal_progress: 0.934
- terminal_score: 0.934
- phase_score: 0.669
- phase_breakdown.pre_contact_score: 0.122
- phase_breakdown.push_to_goal_score: 0.904

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.775
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.934
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.387


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36691,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13861,"approach_1.approach_offset":0.04121,"contact_nudge.nudge_distance":0.0059,"descend_1.descend_backoff":0.03705,"push_1.max_push_time":12.85154,"push_1.push_distance":0.19428,"push_1.push_speed":0.05889,"retract_1.lift_height":0.04605},"optimized_scores":{"best_composite_score":0.25886,"best_fitness_score":0.74886,"best_task_score":0.92115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.55513,-0.00099,0.04896],"force_p95":114.99121,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.3378,"mean_force":70.19145,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55149,0.00975,0.04925]},{"body_a":"world","body_b":"push_box","contact_count":1756.0,"contact_point_centroid":[0.54428,-0.0257,-2e-05],"force_p95":0.26832,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.22727,"mean_force":0.93271,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54809,0.01024,0.10646]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.53045,-0.13931,0.05262],"force_p95":38.29068,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.66261,"mean_force":11.8318,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50192,-0.11741,0.01782]},{"body_a":"world","body_b":"push_box","contact_count":1046.0,"contact_point_centroid":[0.51626,-0.1655,-1e-05],"force_p95":0.5459,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.28074,"mean_force":0.47108,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49881,-0.11672,0.03923]},{"body_a":"world","body_b":"push_box","contact_count":1778.0,"contact_point_centroid":[0.52626,-0.11554,-7e-05],"force_p95":25.25429,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.20294,"mean_force":6.84494,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5198,-0.06897,0.0159]},{"body_a":"push_box","body_b":"link7","contact_count":433.0,"contact_point_centroid":[0.53486,-0.11853,0.05152],"force_p95":31.71321,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.95654,"mean_force":17.51135,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50852,-0.09885,0.01625]},{"body_a":"attachment","body_b":"push_box","contact_count":198.0,"contact_point_centroid":[0.51095,-0.12699,0.05221],"force_p95":2.14211,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.8566,"mean_force":1.12363,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49915,-0.11679,0.03044]},{"body_a":"attachment","body_b":"push_box","contact_count":927.0,"contact_point_centroid":[0.52265,-0.087,0.03451],"force_p95":19.75772,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.84941,"mean_force":6.69319,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5173,-0.07536,0.01586]},{"body_a":"attachment","body_b":"push_box","contact_count":438.0,"contact_point_centroid":[0.54221,-0.02248,0.02468],"force_p95":12.37493,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.87144,"mean_force":4.67299,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.54357,-0.01061,0.02437]},{"body_a":"world","body_b":"push_box","contact_count":1253.0,"contact_point_centroid":[0.53703,-0.04949,-4e-05],"force_p95":4.95709,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.1896,"mean_force":1.88889,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.54399,-0.00937,0.02479]},{"body_a":"world","body_b":"push_box","contact_count":1060.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52212,0.00531,0.24094]}],"total_contact_groups":11},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50943,-0.15443,0.02499],"final_tcp_position":[0.4986,-0.11668,0.05441],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":173.3378,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":930.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.54674,0.01105,0.17955],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":449.0,"n_steps_budget":960.0,"object_pos_end":[0.54441,-0.02745,0.0249],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13035,"object_to_goal_dist_start":0.13211,"object_z_max":0.02511,"peak_contact_force":0.24695,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1773.0,"raw_peak_contact_force":173.3378,"subtask_id":"pre_contact","tcp_end":[0.55237,0.00975,0.03368],"tcp_start":[0.54674,0.01105,0.17955],"tcp_to_object_dist_end":0.03904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":512.0,"n_steps_budget":600.0,"object_pos_end":[0.53228,-0.06537,0.02494],"object_pos_start":[0.54441,-0.02745,0.0249],"object_to_goal_dist_end":0.09058,"object_to_goal_dist_start":0.13035,"object_z_max":0.02515,"peak_contact_force":6.82051,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1691.0,"raw_peak_contact_force":17.87144,"subtask_id":"pre_contact","tcp_end":[0.53896,-0.02901,0.02026],"tcp_start":[0.55237,0.00975,0.03368],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51175,-0.15576,0.02735],"object_pos_start":[0.53228,-0.06537,0.02494],"object_to_goal_dist_end":0.0133,"object_to_goal_dist_start":0.09058,"object_z_max":0.02735,"peak_contact_force":32.21198,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3138.0,"raw_peak_contact_force":36.20294,"subtask_id":"push_to_goal","tcp_end":[0.50245,-0.11743,0.01749],"tcp_start":[0.53896,-0.02901,0.02026],"tcp_to_object_dist_end":0.04066,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":600.0,"object_pos_end":[0.50943,-0.15443,0.02499],"object_pos_start":[0.51175,-0.15576,0.02735],"object_to_goal_dist_end":0.01042,"object_to_goal_dist_start":0.0133,"object_z_max":0.02756,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1260.0,"raw_peak_contact_force":42.66261,"tcp_end":[0.4986,-0.11668,0.05441],"tcp_start":[0.50245,-0.11743,0.01749],"tcp_to_object_dist_end":0.04907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10425,"approach_1.approach_offset":0.04316,"contact_nudge.nudge_distance":0.00895,"descend_1.descend_backoff":0.03966,"push_1.max_push_time":9.90979,"push_1.push_distance":0.20217,"push_1.push_speed":0.05029,"retract_1.lift_height":0.06708},"optimized_scores":{"best_composite_score":0.285,"best_fitness_score":0.775,"best_task_score":0.93384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.56613,-0.01046,0.04609],"force_p95":54.9148,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.88287,"mean_force":31.46412,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56548,0.00135,0.04617]},{"body_a":"world","body_b":"push_box","contact_count":1324.0,"contact_point_centroid":[0.55424,-0.03588,-1e-05],"force_p95":0.48308,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.97384,"mean_force":0.51293,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56241,0.00219,0.08983]},{"body_a":"attachment","body_b":"push_box","contact_count":416.0,"contact_point_centroid":[0.55379,-0.03158,0.02455],"force_p95":12.99547,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.23955,"mean_force":5.12856,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.55507,-0.01971,0.02412]},{"body_a":"attachment","body_b":"push_box","contact_count":790.0,"contact_point_centroid":[0.52134,-0.08909,0.01588],"force_p95":8.78565,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.78803,"mean_force":3.46022,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52441,-0.07754,0.01516]},{"body_a":"world","body_b":"push_box","contact_count":1282.0,"contact_point_centroid":[0.54449,-0.05738,-5e-05],"force_p95":4.7422,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.23962,"mean_force":1.92612,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.55548,-0.01888,0.02443]},{"body_a":"world","body_b":"push_box","contact_count":2352.0,"contact_point_centroid":[0.51303,-0.11425,-4e-05],"force_p95":3.57163,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.56898,"mean_force":1.41016,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52503,-0.07643,0.01522]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50034,-0.12508,0.01907],"force_p95":2.80674,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.91168,"mean_force":1.86236,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50384,-0.11363,0.01825]},{"body_a":"world","body_b":"push_box","contact_count":1919.0,"contact_point_centroid":[0.49194,-0.14935,-1e-05],"force_p95":0.30733,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7537,"mean_force":0.25343,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50236,-0.11318,0.04431]},{"body_a":"world","body_b":"push_box","contact_count":1356.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52927,0.00161,0.22359]}],"total_contact_groups":9},"final_pose_error":0.01043,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49169,-0.14866,0.02499],"final_tcp_position":[0.50229,-0.11313,0.07256],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":57.88287,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.5613,0.00331,0.1451],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12627,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":342.0,"n_steps_budget":780.0,"object_pos_end":[0.55484,-0.03567,0.02495],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12681,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":26.25412,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1335.0,"raw_peak_contact_force":57.88287,"subtask_id":"pre_contact","tcp_end":[0.56649,0.00125,0.03342],"tcp_start":[0.5613,0.00331,0.1451],"tcp_to_object_dist_end":0.03963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.53758,-0.07513,0.02489],"object_pos_start":[0.55484,-0.03567,0.02495],"object_to_goal_dist_end":0.08377,"object_to_goal_dist_start":0.12681,"object_z_max":0.02517,"peak_contact_force":0.49499,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1698.0,"raw_peak_contact_force":22.23955,"subtask_id":"pre_contact","tcp_end":[0.54792,-0.03953,0.02009],"tcp_start":[0.56649,0.00125,0.03342],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49213,-0.1482,0.02504],"object_pos_start":[0.53758,-0.07513,0.02489],"object_to_goal_dist_end":0.00807,"object_to_goal_dist_start":0.08377,"object_z_max":0.02515,"peak_contact_force":1.6382,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3142.0,"raw_peak_contact_force":19.78803,"subtask_id":"push_to_goal","tcp_end":[0.506,-0.11382,0.0152],"tcp_start":[0.54792,-0.03953,0.02009],"tcp_to_object_dist_end":0.03836,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":494.0,"n_steps_budget":600.0,"object_pos_end":[0.49169,-0.14866,0.02499],"object_pos_start":[0.49213,-0.1482,0.02504],"object_to_goal_dist_end":0.00842,"object_to_goal_dist_start":0.00807,"object_z_max":0.02505,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1921.0,"raw_peak_contact_force":2.91168,"tcp_end":[0.50229,-0.11313,0.07256],"tcp_start":[0.506,-0.11382,0.0152],"tcp_to_object_dist_end":0.06031,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66197,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06253,"approach_1.approach_offset":0.0456,"contact_nudge.nudge_distance":0.00815,"descend_1.descend_backoff":0.03312,"push_1.max_push_time":12.07443,"push_1.push_distance":0.13492,"push_1.push_speed":0.07456,"retract_1.lift_height":0.05782},"optimized_scores":{"best_composite_score":0.21841,"best_fitness_score":0.70841,"best_task_score":0.86465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":44.0,"contact_point_centroid":[0.44901,0.02424,0.04851],"force_p95":175.78597,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":271.22316,"mean_force":105.00755,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4442,0.03438,0.04667]},{"body_a":"world","body_b":"push_box","contact_count":989.0,"contact_point_centroid":[0.45572,-0.00094,-5e-05],"force_p95":43.94596,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.27847,"mean_force":4.94633,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44373,0.03593,0.07024]},{"body_a":"world","body_b":"push_box","contact_count":2109.0,"contact_point_centroid":[0.50098,-0.10133,-9e-05],"force_p95":15.13605,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.13005,"mean_force":5.83556,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46665,-0.06608,0.01773]},{"body_a":"push_box","body_b":"link7","contact_count":540.0,"contact_point_centroid":[0.5104,-0.08908,0.04999],"force_p95":22.83231,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.65735,"mean_force":11.48452,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47191,-0.08471,0.01746]},{"body_a":"attachment","body_b":"push_box","contact_count":758.0,"contact_point_centroid":[0.48179,-0.07669,0.04989],"force_p95":17.93593,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.16631,"mean_force":8.08048,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4673,-0.06805,0.01779]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52094,-0.12493,0.04982],"force_p95":21.38276,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.78247,"mean_force":7.65288,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48231,-0.12087,0.01731]},{"body_a":"attachment","body_b":"push_box","contact_count":417.0,"contact_point_centroid":[0.45322,0.00085,0.04833],"force_p95":12.79007,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.84077,"mean_force":5.87757,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.44729,0.01271,0.02648]},{"body_a":"world","body_b":"push_box","contact_count":1803.0,"contact_point_centroid":[0.52025,-0.1446,-1e-05],"force_p95":0.24613,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.71293,"mean_force":0.27406,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47904,-0.12004,0.04192]},{"body_a":"world","body_b":"push_box","contact_count":805.0,"contact_point_centroid":[0.46479,-0.04222,-3e-05],"force_p95":7.2296,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.16144,"mean_force":3.46673,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.44686,0.01452,0.02701]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.50087,-0.12503,0.0498],"force_p95":6.45253,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.4102,"mean_force":1.78068,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4821,-0.12087,0.01754]},{"body_a":"world","body_b":"push_box","contact_count":1564.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47314,0.01882,0.20433]}],"total_contact_groups":11},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5205,-0.14471,0.02499],"final_tcp_position":[0.47886,-0.11997,0.06579],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":271.22316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.44602,0.0387,0.10644],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.45548,-0.00317,0.0248],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15343,"object_to_goal_dist_start":0.1564,"object_z_max":0.02537,"peak_contact_force":0.25842,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1033.0,"raw_peak_contact_force":271.22316,"subtask_id":"pre_contact","tcp_end":[0.44393,0.03358,0.03434],"tcp_start":[0.44602,0.0387,0.10644],"tcp_to_object_dist_end":0.03968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.4697,-0.04217,0.02568],"object_pos_start":[0.45548,-0.00317,0.0248],"object_to_goal_dist_end":0.11201,"object_to_goal_dist_start":0.15343,"object_z_max":0.0257,"peak_contact_force":0.15942,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1222.0,"raw_peak_contact_force":17.84077,"subtask_id":"pre_contact","tcp_end":[0.4531,-0.00702,0.02184],"tcp_start":[0.44393,0.03358,0.03434],"tcp_to_object_dist_end":0.03906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52054,-0.14403,0.02492],"object_pos_start":[0.4697,-0.04217,0.02568],"object_to_goal_dist_end":0.02139,"object_to_goal_dist_start":0.11201,"object_z_max":0.02606,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3407.0,"raw_peak_contact_force":40.13005,"subtask_id":"push_to_goal","tcp_end":[0.48248,-0.12073,0.01723],"tcp_start":[0.4531,-0.00702,0.02184],"tcp_to_object_dist_end":0.04529,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":600.0,"object_pos_end":[0.5205,-0.14471,0.02499],"object_pos_start":[0.52054,-0.14403,0.02492],"object_to_goal_dist_end":0.02117,"object_to_goal_dist_start":0.02139,"object_z_max":0.02514,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1824.0,"raw_peak_contact_force":23.78247,"tcp_end":[0.47886,-0.11997,0.06579],"tcp_start":[0.48248,-0.12073,0.01723],"tcp_to_object_dist_end":0.06332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```