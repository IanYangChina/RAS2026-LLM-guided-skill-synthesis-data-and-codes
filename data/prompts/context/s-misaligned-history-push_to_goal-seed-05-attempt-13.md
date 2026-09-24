## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4262 | 0.94 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.3984 | 0.91 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4588 | 0.97 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4080 | 0.94 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.4522 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.452) — your mutation base

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

- **Composite score**: 0.452
- **task_score** (E): 0.947
- **fitness_score**: 0.862  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2180 |
| descend_to_contact | 1.00 | 1.00 | 0.0729 |
| push_toward_goal | 0.67 | 1.00 | 0.2865 |
| retract_after_push | 0.67 | 1.00 | 0.1082 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.098, 0.110) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.522, 0.098, 0.110)→(0.519, 0.059, 0.049) | (0.519, 0.022, 0.025)→(0.519, 0.021, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 14.449 | 16.972 |
| push_toward_goal | push | 0.67 / step_budget | (0.519, 0.059, 0.049)→(0.487, -0.225, 0.045) | (0.519, 0.021, 0.025)→(0.505, -0.142, 0.025) | 0.173→0.010 | 1.00 / 4.000 | 0.284 | 104.594 |
| retract_after_push | retract | 0.67 / step_budget | (0.487, -0.225, 0.045)→(0.484, -0.224, 0.153) | (0.505, -0.142, 0.025)→(0.505, -0.142, 0.025) | 0.010→0.010 | 1.00 / 4.000 | 0.245 | 0.278 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.992
- lateral_force_integral: None
- approach_alignment: 0.904
- goal_progress: 0.992
- terminal_score: 0.992
- phase_score: 0.826
- phase_breakdown.pre_push_contact_score: 0.438
- phase_breakdown.push_to_goal_score: 0.992

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.892
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.992
- **Median Q (composite search score)**: 0.480
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18293,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.07811,"approach_behind.speed":0.13827,"descend_to_contact.descend_distance":0.0391,"descend_to_contact.speed":0.04246,"push_toward_goal.push_distance":0.34926,"push_toward_goal.speed":0.03079,"retract_after_push.speed":0.01897},"optimized_scores":{"best_composite_score":0.48206,"best_fitness_score":0.89206,"best_task_score":0.99171},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":662.0,"contact_point_centroid":[0.52425,-0.05778,0.04829],"force_p95":121.8344,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.80203,"mean_force":82.96458,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51671,-0.05397,0.05075]},{"body_a":"world","body_b":"push_box","contact_count":2005.0,"contact_point_centroid":[0.51703,-0.09765,-0.0003],"force_p95":104.11302,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.61905,"mean_force":27.89096,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50524,-0.10662,0.0486]},{"body_a":"world","body_b":"push_box","contact_count":3048.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52174,0.0533,0.20336]},{"body_a":"world","body_b":"push_box","contact_count":1524.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54135,0.09259,0.07817]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5004,-0.14847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.47239,-0.24915,0.08175]}],"total_contact_groups":5},"final_pose_error":0.07471,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5004,-0.14847,0.02499],"final_tcp_position":[0.47254,-0.24912,0.12],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":128.80203,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":762.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3048.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54539,0.10707,0.10924],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":990.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push_contact","tcp_end":[0.54003,0.07807,0.05062],"tcp_start":[0.54539,0.10707,0.10924],"tcp_to_object_dist_end":0.04857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5004,-0.14847,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.00158,"object_to_goal_dist_start":0.1905,"object_z_max":0.03535,"peak_contact_force":0.24525,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2667.0,"raw_peak_contact_force":128.80203,"subtask_id":"push_to_goal","tcp_end":[0.47579,-0.2505,0.04463],"tcp_start":[0.54003,0.07807,0.05062],"tcp_to_object_dist_end":0.10678,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5004,-0.14847,0.02499],"object_pos_start":[0.5004,-0.14847,0.02499],"object_to_goal_dist_end":0.00158,"object_to_goal_dist_start":0.00158,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47254,-0.24912,0.12],"tcp_start":[0.47579,-0.2505,0.04463],"tcp_to_object_dist_end":0.14119,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17899,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.07255,"approach_behind.speed":0.08736,"descend_to_contact.descend_distance":0.03255,"descend_to_contact.speed":0.02761,"push_toward_goal.push_distance":0.24276,"push_toward_goal.speed":0.03575,"retract_after_push.speed":0.09029},"optimized_scores":{"best_composite_score":0.48042,"best_fitness_score":0.89042,"best_task_score":0.97871},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":606.0,"contact_point_centroid":[0.50918,-0.07301,0.04932],"force_p95":129.44473,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.6359,"mean_force":93.5317,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50242,-0.07081,0.05162]},{"body_a":"world","body_b":"push_box","contact_count":2071.0,"contact_point_centroid":[0.50498,-0.10848,-0.00027],"force_p95":78.10246,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.42865,"mean_force":27.73714,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49961,-0.11755,0.04955]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.50476,0.00582,0.04974],"force_p95":39.55479,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.28752,"mean_force":34.46713,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50159,0.01704,0.05099]},{"body_a":"world","body_b":"push_box","contact_count":2196.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.97285,"mean_force":0.57435,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50086,0.03245,0.07876]},{"body_a":"world","body_b":"push_box","contact_count":2516.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50071,0.02435,0.2068]},{"body_a":"world","body_b":"push_box","contact_count":3852.0,"contact_point_centroid":[0.50271,-0.15067,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48942,-0.24178,0.11246]}],"total_contact_groups":6},"final_pose_error":0.01184,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50271,-0.15067,0.02499],"final_tcp_position":[0.4899,-0.24186,0.18307],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":135.6359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2516.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50322,0.04971,0.11323],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,-0.01914,0.0248],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13095,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":36.50794,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2217.0,"raw_peak_contact_force":40.28752,"subtask_id":"pre_push_contact","tcp_end":[0.50191,0.01693,0.05036],"tcp_start":[0.50322,0.04971,0.11323],"tcp_to_object_dist_end":0.0443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.50271,-0.15067,0.02499],"object_pos_start":[0.50473,-0.01914,0.0248],"object_to_goal_dist_end":0.00279,"object_to_goal_dist_start":0.13095,"object_z_max":0.03521,"peak_contact_force":0.24525,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2677.0,"raw_peak_contact_force":135.6359,"subtask_id":"push_to_goal","tcp_end":[0.49265,-0.24301,0.04453],"tcp_start":[0.50191,0.01693,0.05036],"tcp_to_object_dist_end":0.09492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.50271,-0.15067,0.02499],"object_pos_start":[0.50271,-0.15067,0.02499],"object_to_goal_dist_end":0.00279,"object_to_goal_dist_start":0.00279,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4899,-0.24186,0.18307],"tcp_start":[0.49265,-0.24301,0.04453],"tcp_to_object_dist_end":0.18294,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24701,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.09677,"approach_behind.speed":0.09346,"descend_to_contact.descend_distance":0.03323,"descend_to_contact.speed":0.03337,"push_toward_goal.push_distance":0.24631,"push_toward_goal.speed":0.05246,"retract_after_push.speed":0.06791},"optimized_scores":{"best_composite_score":0.39425,"best_fitness_score":0.80425,"best_task_score":0.87129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":383.0,"contact_point_centroid":[0.51314,-0.04776,0.05329],"force_p95":37.65279,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.34277,"mean_force":9.92527,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50264,-0.03953,0.04374]},{"body_a":"world","body_b":"push_box","contact_count":837.0,"contact_point_centroid":[0.53063,-0.08919,-0.00018],"force_p95":21.3663,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.80219,"mean_force":5.21853,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50076,-0.06861,0.04391]},{"body_a":"attachment","body_b":"push_box","contact_count":76.0,"contact_point_centroid":[0.5136,0.07168,0.0483],"force_p95":9.74293,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.38179,"mean_force":7.17382,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51351,0.08365,0.04824]},{"body_a":"world","body_b":"push_box","contact_count":3508.0,"contact_point_centroid":[0.51502,0.04664,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.19942,"mean_force":0.40442,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5139,0.10431,0.07067]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51257,-0.1278,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34481,"mean_force":0.24517,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49008,-0.18011,0.09947]},{"body_a":"world","body_b":"push_box","contact_count":3368.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50798,0.0681,0.20288]}],"total_contact_groups":6},"final_pose_error":0.03957,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51257,-0.1278,0.02499],"final_tcp_position":[0.49033,-0.1801,0.15503],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":49.34277,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":842.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3368.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51778,0.13633,0.10898],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.51515,0.04576,0.02511],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19635,"object_to_goal_dist_start":0.19823,"object_z_max":0.02511,"peak_contact_force":6.59388,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3584.0,"raw_peak_contact_force":10.38179,"subtask_id":"pre_push_contact","tcp_end":[0.51357,0.08256,0.0469],"tcp_start":[0.51778,0.13633,0.10898],"tcp_to_object_dist_end":0.04279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.51185,-0.12798,0.02393],"object_pos_start":[0.51515,0.04576,0.02511],"object_to_goal_dist_end":0.02503,"object_to_goal_dist_start":0.19635,"object_z_max":0.03339,"peak_contact_force":0.36033,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1220.0,"raw_peak_contact_force":49.34277,"subtask_id":"push_to_goal","tcp_end":[0.49347,-0.18102,0.04447],"tcp_start":[0.51357,0.08256,0.0469],"tcp_to_object_dist_end":0.05977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51257,-0.1278,0.02499],"object_pos_start":[0.51185,-0.12798,0.02393],"object_to_goal_dist_end":0.02552,"object_to_goal_dist_start":0.02503,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.34481,"tcp_end":[0.49033,-0.1801,0.15503],"tcp_start":[0.49347,-0.18102,0.04447],"tcp_to_object_dist_end":0.14192,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```