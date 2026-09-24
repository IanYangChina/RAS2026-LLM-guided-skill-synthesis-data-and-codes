## Search State

- **Seed**: 9
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.2541 | 0.91 | ✅ accepted |
| 13 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.2544 | 0.91 | ✅ accepted |
| 12 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | 0.3867 | 0.73 | ❌ rejected |
| 11 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9  | 0.4961 | 0.73 | ❌ rejected |
| 10 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9  | 0.2652 | 0.91 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.910, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.265) — your mutation base

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

- **Composite score**: 0.265
- **task_score** (E): 0.910
- **fitness_score**: 0.755  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1670 |
| descend_1 | 1.00 | 1.00 | 0.1099 |
| contact_nudge | 1.00 | 1.00 | 0.0441 |
| push_1 | 1.00 | 1.00 | 0.1047 |
| retract_1 | 1.00 | 1.00 | 0.0500 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.014, 0.144) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.517, 0.014, 0.144)→(0.522, 0.015, 0.034) | (0.518, -0.020, 0.025)→(0.519, -0.023, 0.025) | 0.139→0.137 | 1.00 / 3.333 | 0.441 | 170.540 |
| contact_nudge | push | 1.00 / step_budget | (0.522, 0.015, 0.034)→(0.514, -0.025, 0.021) | (0.519, -0.023, 0.025)→(0.514, -0.060, 0.025) | 0.137→0.097 | 1.00 / 3.667 | 3.902 | 17.444 |
| push_1 | push | 1.00 / time_limit | (0.514, -0.025, 0.021)→(0.495, -0.121, 0.016) | (0.514, -0.060, 0.025)→(0.506, -0.151, 0.025) | 0.097→0.013 | 1.00 / 3.000 | 7.836 | 24.848 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.121, 0.016)→(0.492, -0.120, 0.066) | (0.506, -0.151, 0.025)→(0.506, -0.152, 0.025) | 0.013→0.013 | 1.00 / 4.000 | 0.245 | 9.734 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.698
- goal_progress: 0.961
- terminal_score: 0.961
- phase_score: 0.698
- phase_breakdown.pre_contact_score: 0.122
- phase_breakdown.push_to_goal_score: 0.945

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.803
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.961
- **Median Q (composite search score)**: 0.281
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.383


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44604,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09043,"approach_1.approach_offset":0.04099,"contact_nudge.nudge_distance":0.00488,"descend_1.descend_backoff":0.0373,"push_1.max_push_time":10.07438,"push_1.push_distance":0.2338,"push_1.push_speed":0.06224,"retract_1.lift_height":0.05474},"optimized_scores":{"best_composite_score":0.28146,"best_fitness_score":0.77146,"best_task_score":0.925},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.55386,-0.00097,0.04912],"force_p95":92.65594,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.91192,"mean_force":59.35216,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55106,0.01012,0.04941]},{"body_a":"world","body_b":"push_box","contact_count":1197.0,"contact_point_centroid":[0.54453,-0.02561,-1e-05],"force_p95":0.48713,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.40012,"mean_force":1.04532,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54878,0.01057,0.08287]},{"body_a":"attachment","body_b":"push_box","contact_count":886.0,"contact_point_centroid":[0.51682,-0.08721,0.02074],"force_p95":9.69238,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.60449,"mean_force":3.18701,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51649,-0.0753,0.01546]},{"body_a":"attachment","body_b":"push_box","contact_count":445.0,"contact_point_centroid":[0.54276,-0.02175,0.02461],"force_p95":11.80645,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.10871,"mean_force":4.72597,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.54376,-0.00984,0.02438]},{"body_a":"world","body_b":"push_box","contact_count":1969.0,"contact_point_centroid":[0.51672,-0.11354,-4e-05],"force_p95":4.60431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.4838,"mean_force":1.70798,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51826,-0.07103,0.01555]},{"body_a":"world","body_b":"push_box","contact_count":1282.0,"contact_point_centroid":[0.53781,-0.04838,-3e-05],"force_p95":4.72968,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.51347,"mean_force":1.8927,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.54412,-0.00875,0.02476]},{"body_a":"push_box","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.5255,-0.13099,0.05047],"force_p95":6.42908,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.01211,"mean_force":1.97548,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49934,-0.11841,0.01543]},{"body_a":"world","body_b":"push_box","contact_count":1861.0,"contact_point_centroid":[0.49887,-0.16004,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.20049,"mean_force":0.251,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49434,-0.12133,0.03857]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.50607,-0.13411,0.05006],"force_p95":1.54473,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.56345,"mean_force":0.68045,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49724,-0.12208,0.01593]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52432,-0.13779,0.05044],"force_p95":1.45439,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.52218,"mean_force":0.84433,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49794,-0.12207,0.01548]},{"body_a":"world","body_b":"push_box","contact_count":1400.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52298,0.00549,0.21728]}],"total_contact_groups":11},"final_pose_error":0.01005,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49886,-0.15984,0.02499],"final_tcp_position":[0.49419,-0.12127,0.06095],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":94.91192,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1400.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.54831,0.01133,0.13224],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":690.0,"object_pos_end":[0.5447,-0.02701,0.02497],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13086,"object_to_goal_dist_start":0.13211,"object_z_max":0.02501,"peak_contact_force":0.24563,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1213.0,"raw_peak_contact_force":94.91192,"subtask_id":"pre_contact","tcp_end":[0.55215,0.01004,0.03365],"tcp_start":[0.54831,0.01133,0.13224],"tcp_to_object_dist_end":0.03878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":510.0,"n_steps_budget":600.0,"object_pos_end":[0.53376,-0.06425,0.02499],"object_pos_start":[0.5447,-0.02701,0.02497],"object_to_goal_dist_end":0.09216,"object_to_goal_dist_start":0.13086,"object_z_max":0.02507,"peak_contact_force":5.66589,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1727.0,"raw_peak_contact_force":18.10871,"subtask_id":"pre_contact","tcp_end":[0.53952,-0.02773,0.02031],"tcp_start":[0.55215,0.01004,0.03365],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50008,-0.15892,0.02526],"object_pos_start":[0.53376,-0.06425,0.02499],"object_to_goal_dist_end":0.00892,"object_to_goal_dist_start":0.09216,"object_z_max":0.02532,"peak_contact_force":1.64412,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2879.0,"raw_peak_contact_force":18.60449,"subtask_id":"push_to_goal","tcp_end":[0.49796,-0.12204,0.01549],"tcp_start":[0.53952,-0.02773,0.02031],"tcp_to_object_dist_end":0.03821,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.49886,-0.15984,0.02499],"object_pos_start":[0.50008,-0.15892,0.02526],"object_to_goal_dist_end":0.00991,"object_to_goal_dist_start":0.00892,"object_z_max":0.02526,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1875.0,"raw_peak_contact_force":3.20049,"tcp_end":[0.49419,-0.12127,0.06095],"tcp_start":[0.49796,-0.12204,0.01549],"tcp_to_object_dist_end":0.05294,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43262,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11149,"approach_1.approach_offset":0.03014,"contact_nudge.nudge_distance":0.00804,"descend_1.descend_backoff":0.03923,"push_1.max_push_time":10.33665,"push_1.push_distance":0.17995,"push_1.push_speed":0.05153,"retract_1.lift_height":0.06065},"optimized_scores":{"best_composite_score":0.31295,"best_fitness_score":0.80295,"best_task_score":0.96058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":54.0,"contact_point_centroid":[0.57442,-0.00952,0.04776],"force_p95":163.15665,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.69279,"mean_force":120.91704,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5676,-0.00032,0.04784]},{"body_a":"world","body_b":"push_box","contact_count":1454.0,"contact_point_centroid":[0.55597,-0.0353,-6e-05],"force_p95":12.14623,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":178.77256,"mean_force":4.78107,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55991,-0.00372,0.09323]},{"body_a":"attachment","body_b":"push_box","contact_count":824.0,"contact_point_centroid":[0.52264,-0.09103,0.01557],"force_p95":8.67533,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.39815,"mean_force":3.30128,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52533,-0.07937,0.01498]},{"body_a":"attachment","body_b":"push_box","contact_count":403.0,"contact_point_centroid":[0.55613,-0.0329,0.0249],"force_p95":12.4186,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.91477,"mean_force":4.8185,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.55785,-0.02109,0.02453]},{"body_a":"world","body_b":"push_box","contact_count":1279.0,"contact_point_centroid":[0.54785,-0.05897,-4e-05],"force_p95":4.77337,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.58513,"mean_force":1.78417,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.55833,-0.02017,0.02495]},{"body_a":"world","body_b":"push_box","contact_count":2317.0,"contact_point_centroid":[0.51622,-0.1176,-4e-05],"force_p95":3.55777,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20572,"mean_force":1.41142,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5259,-0.07842,0.01504]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50228,-0.1279,0.01558],"force_p95":1.32751,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.32751,"mean_force":1.32751,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50492,-0.11621,0.01501]},{"body_a":"world","body_b":"push_box","contact_count":1921.0,"contact_point_centroid":[0.49572,-0.15251,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10033,"mean_force":0.24717,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50133,-0.11557,0.04059]},{"body_a":"world","body_b":"push_box","contact_count":1284.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52672,-0.00332,0.2273]}],"total_contact_groups":9},"final_pose_error":0.0103,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49567,-0.15254,0.02499],"final_tcp_position":[0.50117,-0.1155,0.06608],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":184.69279,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.55606,-0.00686,0.15253],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":394.0,"n_steps_budget":810.0,"object_pos_end":[0.5574,-0.03842,0.02471],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12548,"object_to_goal_dist_start":0.12728,"object_z_max":0.02563,"peak_contact_force":0.48011,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":184.69279,"subtask_id":"pre_contact","tcp_end":[0.56945,0.00051,0.03465],"tcp_start":[0.55606,-0.00686,0.15253],"tcp_to_object_dist_end":0.04195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.54017,-0.07668,0.02494],"object_pos_start":[0.5574,-0.03842,0.02471],"object_to_goal_dist_end":0.0836,"object_to_goal_dist_start":0.12548,"object_z_max":0.02513,"peak_contact_force":3.31573,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1682.0,"raw_peak_contact_force":15.91477,"subtask_id":"pre_contact","tcp_end":[0.55071,-0.04122,0.01995],"tcp_start":[0.56945,0.00051,0.03465],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49587,-0.15207,0.02499],"object_pos_start":[0.54017,-0.07668,0.02494],"object_to_goal_dist_end":0.00462,"object_to_goal_dist_start":0.0836,"object_z_max":0.02514,"peak_contact_force":0.69203,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3141.0,"raw_peak_contact_force":17.39815,"subtask_id":"push_to_goal","tcp_end":[0.50492,-0.11621,0.01501],"tcp_start":[0.55071,-0.04122,0.01995],"tcp_to_object_dist_end":0.03831,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.49567,-0.15254,0.02499],"object_pos_start":[0.49587,-0.15207,0.02499],"object_to_goal_dist_end":0.00502,"object_to_goal_dist_start":0.00462,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1922.0,"raw_peak_contact_force":1.32751,"tcp_end":[0.50117,-0.1155,0.06608],"tcp_start":[0.50492,-0.11621,0.01501],"tcp_to_object_dist_end":0.0556,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68085,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10344,"approach_1.approach_offset":0.04462,"contact_nudge.nudge_distance":0.00629,"descend_1.descend_backoff":0.03494,"push_1.max_push_time":7.51627,"push_1.push_distance":0.19428,"push_1.push_speed":0.07631,"retract_1.lift_height":0.06249},"optimized_scores":{"best_composite_score":0.20112,"best_fitness_score":0.69112,"best_task_score":0.84456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.44872,0.02444,0.04888],"force_p95":202.82172,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":232.01483,"mean_force":104.2915,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44403,0.03465,0.04703]},{"body_a":"world","body_b":"push_box","contact_count":1482.0,"contact_point_centroid":[0.45566,-0.001,-3e-05],"force_p95":15.6422,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.82537,"mean_force":3.01002,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44424,0.03541,0.09072]},{"body_a":"push_box","body_b":"link7","contact_count":603.0,"contact_point_centroid":[0.51027,-0.08794,0.04998],"force_p95":24.22563,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.54033,"mean_force":11.96274,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47166,-0.08389,0.0175]},{"body_a":"world","body_b":"push_box","contact_count":2101.0,"contact_point_centroid":[0.50359,-0.10097,-7e-05],"force_p95":15.82527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.24697,"mean_force":6.10463,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46708,-0.06755,0.01773]},{"body_a":"attachment","body_b":"push_box","contact_count":766.0,"contact_point_centroid":[0.48197,-0.0772,0.04998],"force_p95":16.09639,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.43185,"mean_force":7.25847,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46739,-0.06839,0.01779]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52161,-0.12789,0.04983],"force_p95":24.17927,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.67525,"mean_force":9.17474,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48298,-0.12387,0.01731]},{"body_a":"attachment","body_b":"push_box","contact_count":421.0,"contact_point_centroid":[0.45287,0.00211,0.04778],"force_p95":12.89271,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.30852,"mean_force":5.60475,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.44701,0.01397,0.02649]},{"body_a":"world","body_b":"push_box","contact_count":1890.0,"contact_point_centroid":[0.52296,-0.14281,-2e-05],"force_p95":0.24602,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.22403,"mean_force":0.27665,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47973,-0.12297,0.04447]},{"body_a":"world","body_b":"push_box","contact_count":816.0,"contact_point_centroid":[0.46432,-0.04051,-4e-05],"force_p95":6.90605,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.00281,"mean_force":3.30646,"phase_index":2.0,"phase_name":"contact_nudge","phase_type":"push","tcp_position_centroid":[0.44651,0.01614,0.02718]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.50146,-0.12811,0.04972],"force_p95":6.62356,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.90436,"mean_force":2.11903,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48276,-0.12388,0.01759]},{"body_a":"world","body_b":"push_box","contact_count":1272.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47423,0.01786,0.2245]}],"total_contact_groups":11},"final_pose_error":0.01004,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52327,-0.14296,0.02499],"final_tcp_position":[0.47959,-0.12289,0.07035],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":232.01483,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.44773,0.037,0.14649],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":384.0,"n_steps_budget":780.0,"object_pos_end":[0.45561,-0.00256,0.02486],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15398,"object_to_goal_dist_start":0.1564,"object_z_max":0.02525,"peak_contact_force":0.59792,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1521.0,"raw_peak_contact_force":232.01483,"subtask_id":"pre_contact","tcp_end":[0.44362,0.03461,0.03456],"tcp_start":[0.44773,0.037,0.14649],"tcp_to_object_dist_end":0.04024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.46938,-0.03969,0.02577],"object_pos_start":[0.45561,-0.00256,0.02486],"object_to_goal_dist_end":0.11448,"object_to_goal_dist_start":0.15398,"object_z_max":0.02585,"peak_contact_force":2.7254,"phase_name":"contact_nudge","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1237.0,"raw_peak_contact_force":18.30852,"subtask_id":"pre_contact","tcp_end":[0.45267,-0.00481,0.0219],"tcp_start":[0.44362,0.03461,0.03456],"tcp_to_object_dist_end":0.03887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52309,-0.14211,0.02503],"object_pos_start":[0.46938,-0.03969,0.02577],"object_to_goal_dist_end":0.02441,"object_to_goal_dist_start":0.11448,"object_z_max":0.0261,"peak_contact_force":21.17048,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3470.0,"raw_peak_contact_force":38.54033,"subtask_id":"push_to_goal","tcp_end":[0.48318,-0.12366,0.01721],"tcp_start":[0.45267,-0.00481,0.0219],"tcp_to_object_dist_end":0.04466,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.52327,-0.14296,0.02499],"object_pos_start":[0.52309,-0.14211,0.02503],"object_to_goal_dist_end":0.02431,"object_to_goal_dist_start":0.02441,"object_z_max":0.02521,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1911.0,"raw_peak_contact_force":24.67525,"tcp_end":[0.47959,-0.12289,0.07035],"tcp_start":[0.48318,-0.12366,0.01721],"tcp_to_object_dist_end":0.06609,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```