## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4588 | 0.97 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4080 | 0.94 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4102 | 0.94 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.3788 | 0.90 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.3984 | 0.91 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.968, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.398) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_push_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.08
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: descend_to_contact
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
    - 0.025
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.005
    orientation:
      mode: none
  parameters:
    descend_distance:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: pre_push_contact
- id: push_toward_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal
- id: retract_after_push
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.005
  - orientation: mode=none
  - parameter_bindings:
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_toward_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.398
- **task_score** (E): 0.907
- **fitness_score**: 0.808  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2253 |
| descend_to_contact | 1.00 | 1.00 | 0.0722 |
| push_toward_goal | 1.00 | 1.00 | 0.3224 |
| retract_after_push | 0.67 | 1.00 | 0.1247 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.523, 0.114, 0.110) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.523, 0.114, 0.110)→(0.519, 0.076, 0.049) | (0.519, 0.022, 0.025)→(0.519, 0.021, 0.025) | 0.173→0.172 | 1.00 / 3.667 | 1.994 | 5.793 |
| push_toward_goal | push | 1.00 / step_budget | (0.519, 0.076, 0.049)→(0.488, -0.244, 0.044) | (0.519, 0.021, 0.025)→(0.513, -0.147, 0.025) | 0.172→0.016 | 1.00 / 4.000 | 0.288 | 46.969 |
| retract_after_push | retract | 0.67 / step_budget | (0.488, -0.244, 0.044)→(0.485, -0.243, 0.169) | (0.513, -0.147, 0.025)→(0.513, -0.147, 0.025) | 0.016→0.016 | 1.00 / 4.000 | 0.245 | 0.281 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.899
- goal_progress: 0.916
- terminal_score: 0.916
- phase_score: 0.796
- phase_breakdown.pre_push_contact_score: 0.514
- phase_breakdown.push_to_goal_score: 0.917

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.844
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.916
- **Median Q (composite search score)**: 0.385
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.274


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04348,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.09035,"approach_behind.speed":0.05915,"descend_to_contact.descend_distance":0.03215,"descend_to_contact.speed":0.02393,"push_toward_goal.push_distance":0.26804,"push_toward_goal.speed":0.06921,"retract_after_push.speed":0.06037},"optimized_scores":{"best_composite_score":0.43392,"best_fitness_score":0.84392,"best_task_score":0.9162},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":348.0,"contact_point_centroid":[0.52085,-0.06375,0.05135],"force_p95":37.79107,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.65134,"mean_force":10.40859,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51274,-0.05404,0.04318]},{"body_a":"world","body_b":"push_box","contact_count":898.0,"contact_point_centroid":[0.53263,-0.11397,-0.00019],"force_p95":19.7177,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.47525,"mean_force":4.65981,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50633,-0.08846,0.04343]},{"body_a":"attachment","body_b":"push_box","contact_count":165.0,"contact_point_centroid":[0.53965,0.06017,0.04883],"force_p95":12.03676,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.88834,"mean_force":6.86452,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5391,0.07206,0.04878]},{"body_a":"world","body_b":"push_box","contact_count":3324.0,"contact_point_centroid":[0.53663,0.03489,-1e-05],"force_p95":3.44923,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.32888,"mean_force":0.59284,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54101,0.08874,0.0688]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5126,-0.1598,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35318,"mean_force":0.24505,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48028,-0.20972,0.09386]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52295,0.05938,0.20257]}],"total_contact_groups":6},"final_pose_error":0.05067,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5126,-0.1598,0.02499],"final_tcp_position":[0.48045,-0.20969,0.14388],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":48.65134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54776,0.11877,0.10855],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":901.0,"n_steps_budget":1000.0,"object_pos_end":[0.53649,0.03308,0.02503],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18668,"object_to_goal_dist_start":0.1905,"object_z_max":0.02519,"peak_contact_force":5.49291,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3489.0,"raw_peak_contact_force":16.88834,"subtask_id":"pre_push_contact","tcp_end":[0.53887,0.06997,0.04622],"tcp_start":[0.54776,0.11877,0.10855],"tcp_to_object_dist_end":0.04261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.51205,-0.1598,0.0239],"object_pos_start":[0.53649,0.03308,0.02503],"object_to_goal_dist_end":0.01557,"object_to_goal_dist_start":0.18668,"object_z_max":0.03311,"peak_contact_force":0.37458,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1246.0,"raw_peak_contact_force":48.65134,"subtask_id":"push_to_goal","tcp_end":[0.48365,-0.21081,0.04444],"tcp_start":[0.53887,0.06997,0.04622],"tcp_to_object_dist_end":0.06189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5126,-0.1598,0.02499],"object_pos_start":[0.51205,-0.1598,0.0239],"object_to_goal_dist_end":0.01596,"object_to_goal_dist_start":0.01557,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.35318,"tcp_end":[0.48045,-0.20969,0.14388],"tcp_start":[0.48365,-0.21081,0.04444],"tcp_to_object_dist_end":0.13289,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42023,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.10937,"approach_behind.speed":0.06619,"descend_to_contact.descend_distance":0.07754,"descend_to_contact.speed":0.0317,"push_toward_goal.push_distance":0.29494,"push_toward_goal.speed":0.03989,"retract_after_push.speed":0.12429},"optimized_scores":{"best_composite_score":0.37627,"best_fitness_score":0.78627,"best_task_score":0.91421},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":336.0,"contact_point_centroid":[0.50638,-0.08925,0.05283],"force_p95":35.95254,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.33598,"mean_force":9.30307,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49608,-0.08227,0.04597]},{"body_a":"world","body_b":"push_box","contact_count":2231.0,"contact_point_centroid":[0.51618,-0.11228,-6e-05],"force_p95":12.82946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.32273,"mean_force":1.7772,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49478,-0.14444,0.04563]},{"body_a":"world","body_b":"push_box","contact_count":2892.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50129,0.04171,0.20533]},{"body_a":"world","body_b":"push_box","contact_count":1648.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50231,0.07259,0.07982]},{"body_a":"world","body_b":"push_box","contact_count":2888.0,"contact_point_centroid":[0.51097,-0.14747,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48799,-0.29344,0.10859]}],"total_contact_groups":5},"final_pose_error":0.01419,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51097,-0.14747,0.02499],"final_tcp_position":[0.48846,-0.29352,0.18012],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":45.33598,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50447,0.08449,0.1117],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push_contact","tcp_end":[0.50293,0.06078,0.05124],"tcp_start":[0.50447,0.08449,0.1117],"tcp_to_object_dist_end":0.08382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.51097,-0.14747,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.01126,"object_to_goal_dist_start":0.13127,"object_z_max":0.03311,"peak_contact_force":0.24525,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2567.0,"raw_peak_contact_force":45.33598,"subtask_id":"push_to_goal","tcp_end":[0.49105,-0.29489,0.044],"tcp_start":[0.50293,0.06078,0.05124],"tcp_to_object_dist_end":0.14997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.51097,-0.14747,0.02499],"object_pos_start":[0.51097,-0.14747,0.02499],"object_to_goal_dist_end":0.01126,"object_to_goal_dist_start":0.01126,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48846,-0.29352,0.18012],"tcp_start":[0.49105,-0.29489,0.044],"tcp_to_object_dist_end":0.21425,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97708,"average_solve_count":349.0,"average_success_count":349.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.09976,"approach_behind.speed":0.02357,"descend_to_contact.descend_distance":0.04853,"descend_to_contact.speed":0.0173,"push_toward_goal.push_distance":0.29297,"push_toward_goal.speed":0.06382,"retract_after_push.speed":0.09275},"optimized_scores":{"best_composite_score":0.38494,"best_fitness_score":0.79494,"best_task_score":0.89036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":334.0,"contact_point_centroid":[0.51196,-0.04475,0.05111],"force_p95":37.87,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.9184,"mean_force":10.08295,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50246,-0.03617,0.0449]},{"body_a":"world","body_b":"push_box","contact_count":1397.0,"contact_point_centroid":[0.52427,-0.08819,-0.00015],"force_p95":18.55081,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.67296,"mean_force":2.91281,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49908,-0.09189,0.04508]},{"body_a":"world","body_b":"push_box","contact_count":3748.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50805,0.06958,0.20274]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51478,0.11834,0.07639]},{"body_a":"world","body_b":"push_box","contact_count":3732.0,"contact_point_centroid":[0.51508,-0.13435,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.487,-0.22432,0.11248]}],"total_contact_groups":5},"final_pose_error":0.01185,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51508,-0.13435,0.02499],"final_tcp_position":[0.48747,-0.22439,0.18297],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":46.9184,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3748.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51802,0.13929,0.10878],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push_contact","tcp_end":[0.51451,0.09871,0.04935],"tcp_start":[0.51802,0.13929,0.10878],"tcp_to_object_dist_end":0.05656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.51508,-0.13435,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.02173,"object_to_goal_dist_start":0.19823,"object_z_max":0.0332,"peak_contact_force":0.24522,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1731.0,"raw_peak_contact_force":46.9184,"subtask_id":"push_to_goal","tcp_end":[0.49023,-0.22545,0.04444],"tcp_start":[0.51451,0.09871,0.04935],"tcp_to_object_dist_end":0.09642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.51508,-0.13435,0.02499],"object_pos_start":[0.51508,-0.13435,0.02499],"object_to_goal_dist_end":0.02174,"object_to_goal_dist_start":0.02173,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3732.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48747,-0.22439,0.18297],"tcp_start":[0.49023,-0.22545,0.04444],"tcp_to_object_dist_end":0.18392,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```