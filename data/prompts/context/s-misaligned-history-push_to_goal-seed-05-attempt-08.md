## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.3788 | 0.90 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7  | 0.0990 | 0.54 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7  | 0.1257 | 0.00 | ❌ rejected |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.1863 | 0.58 | ✅ accepted |
| 4 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.4102 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.937, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.410) — your mutation base

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

- **Composite score**: 0.410
- **task_score** (E): 0.937
- **fitness_score**: 0.820  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2150 |
| descend_to_contact | 1.00 | 1.00 | 0.0609 |
| push_toward_goal | 1.00 | 1.00 | 0.2886 |
| retract_after_push | 1.00 | 1.00 | 0.1283 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.088, 0.111) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.522, 0.088, 0.111)→(0.520, 0.075, 0.052) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_toward_goal | push | 1.00 / step_budget | (0.520, 0.075, 0.052)→(0.495, -0.212, 0.048) | (0.519, 0.022, 0.025)→(0.501, -0.148, 0.031) | 0.173→0.017 | 1.00 / 2.333 | 34.438 | 128.106 |
| retract_after_push | retract | 1.00 / step_budget | (0.495, -0.212, 0.048)→(0.492, -0.211, 0.176) | (0.501, -0.148, 0.031)→(0.506, -0.151, 0.025) | 0.017→0.011 | 1.00 / 4.000 | 0.245 | 24.344 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.998
- lateral_force_integral: None
- approach_alignment: 0.954
- goal_progress: 0.973
- terminal_score: 0.973
- phase_score: 0.820
- phase_breakdown.pre_push_contact_score: 0.463
- phase_breakdown.push_to_goal_score: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.881
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.973
- **Median Q (composite search score)**: 0.388
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.231


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18359,"average_solve_count":256.0,"average_success_count":256.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.09114,"approach_behind.speed":0.10449,"descend_to_contact.descend_distance":0.05649,"descend_to_contact.speed":0.02555,"push_toward_goal.push_distance":0.24929,"push_toward_goal.speed":0.0306,"retract_after_push.speed":0.07559},"optimized_scores":{"best_composite_score":0.37122,"best_fitness_score":0.78122,"best_task_score":0.88022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":719.0,"contact_point_centroid":[0.5189,-0.08987,0.0482],"force_p95":118.29504,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.52326,"mean_force":78.62821,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51206,-0.08513,0.05037]},{"body_a":"world","body_b":"push_box","contact_count":1701.0,"contact_point_centroid":[0.52242,-0.09747,-0.00029],"force_p95":104.99113,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.91006,"mean_force":33.7507,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51528,-0.06683,0.05044]},{"body_a":"world","body_b":"push_box","contact_count":3799.0,"contact_point_centroid":[0.52191,-0.15565,-3e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.09464,"mean_force":0.33576,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49387,-0.18933,0.11848]},{"body_a":"attachment","body_b":"push_box","contact_count":24.0,"contact_point_centroid":[0.5039,-0.1825,0.05225],"force_p95":46.67071,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.88217,"mean_force":11.98206,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49627,-0.19095,0.05488]},{"body_a":"world","body_b":"push_box","contact_count":3312.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52305,0.05969,0.2027]},{"body_a":"world","body_b":"push_box","contact_count":1468.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54424,0.10726,0.07841]}],"total_contact_groups":6},"final_pose_error":0.02615,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52215,-0.15548,0.02499],"final_tcp_position":[0.49428,-0.1894,0.17794],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":124.52326,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54787,0.11947,0.1086],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push_contact","tcp_end":[0.54331,0.09486,0.05115],"tcp_start":[0.54787,0.11947,0.1086],"tcp_to_object_dist_end":0.06389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.51452,-0.16349,0.03279],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.0213,"object_to_goal_dist_start":0.1905,"object_z_max":0.03451,"peak_contact_force":102.34695,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2420.0,"raw_peak_contact_force":124.52326,"subtask_id":"push_to_goal","tcp_end":[0.49721,-0.19032,0.05391],"tcp_start":[0.54331,0.09486,0.05115],"tcp_to_object_dist_end":0.03829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52215,-0.15548,0.02499],"object_pos_start":[0.51452,-0.16349,0.03279],"object_to_goal_dist_end":0.02282,"object_to_goal_dist_start":0.0213,"object_z_max":0.03379,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3823.0,"raw_peak_contact_force":68.09464,"tcp_end":[0.49428,-0.1894,0.17794],"tcp_start":[0.49721,-0.19032,0.05391],"tcp_to_object_dist_end":0.15913,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54808,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.04603,"approach_behind.speed":0.08112,"descend_to_contact.descend_distance":0.0379,"descend_to_contact.speed":0.03977,"push_toward_goal.push_distance":0.26029,"push_toward_goal.speed":0.06369,"retract_after_push.speed":0.10912},"optimized_scores":{"best_composite_score":0.47111,"best_fitness_score":0.88111,"best_task_score":0.9729},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":572.0,"contact_point_centroid":[0.50825,-0.07299,0.05009],"force_p95":127.00036,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.48408,"mean_force":89.51647,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50164,-0.07083,0.05239]},{"body_a":"world","body_b":"push_box","contact_count":2164.0,"contact_point_centroid":[0.50527,-0.11139,-0.00024],"force_p95":72.32856,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.39292,"mean_force":24.02104,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49833,-0.12902,0.04956]},{"body_a":"world","body_b":"push_box","contact_count":2428.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50028,0.01224,0.20734]},{"body_a":"world","body_b":"push_box","contact_count":1500.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50055,0.02226,0.0815]},{"body_a":"world","body_b":"push_box","contact_count":3188.0,"contact_point_centroid":[0.50355,-0.14985,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48902,-0.25892,0.11073]}],"total_contact_groups":5},"final_pose_error":0.01315,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50355,-0.14985,0.02499],"final_tcp_position":[0.48948,-0.25899,0.18152],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":137.48408,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2428.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50234,0.02507,0.11378],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push_contact","tcp_end":[0.50144,0.01951,0.05215],"tcp_start":[0.50234,0.02507,0.11378],"tcp_to_object_dist_end":0.04707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.50355,-0.14985,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00356,"object_to_goal_dist_start":0.13127,"object_z_max":0.0352,"peak_contact_force":0.24525,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2736.0,"raw_peak_contact_force":137.48408,"subtask_id":"push_to_goal","tcp_end":[0.49216,-0.26021,0.04434],"tcp_start":[0.50144,0.01951,0.05215],"tcp_to_object_dist_end":0.11262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":797.0,"n_steps_budget":870.0,"object_pos_end":[0.50355,-0.14985,0.02499],"object_pos_start":[0.50355,-0.14985,0.02499],"object_to_goal_dist_end":0.00356,"object_to_goal_dist_start":0.00356,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3188.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48948,-0.25899,0.18152],"tcp_start":[0.49216,-0.26021,0.04434],"tcp_to_object_dist_end":0.19134,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13755,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_distance":0.07855,"approach_behind.speed":0.08968,"descend_to_contact.descend_distance":0.06427,"descend_to_contact.speed":0.02129,"push_toward_goal.push_distance":0.25198,"push_toward_goal.speed":0.01771,"retract_after_push.speed":0.07676},"optimized_scores":{"best_composite_score":0.38823,"best_fitness_score":0.79823,"best_task_score":0.95926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":695.0,"contact_point_centroid":[0.51406,-0.05235,0.04887],"force_p95":116.72387,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.31103,"mean_force":82.24545,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50694,-0.04994,0.05141]},{"body_a":"world","body_b":"push_box","contact_count":1667.0,"contact_point_centroid":[0.51881,-0.04953,-0.00032],"force_p95":112.08453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.01467,"mean_force":34.83857,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50781,-0.02354,0.0509]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.49469,-0.17319,0.0486],"force_p95":4.34889,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.69134,"mean_force":2.48665,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49176,-0.18429,0.04977]},{"body_a":"world","body_b":"push_box","contact_count":3856.0,"contact_point_centroid":[0.49213,-0.14745,-3e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.84265,"mean_force":0.25892,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49086,-0.18338,0.10905]},{"body_a":"world","body_b":"push_box","contact_count":3164.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50726,0.05904,0.20367]},{"body_a":"world","body_b":"push_box","contact_count":1440.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51453,0.11504,0.07975]}],"total_contact_groups":6},"final_pose_error":0.02664,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49233,-0.14749,0.02499],"final_tcp_position":[0.49125,-0.18343,0.16943],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":122.31103,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3164.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51639,0.11863,0.10988],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push_contact","tcp_end":[0.51539,0.11175,0.05211],"tcp_start":[0.51639,0.11863,0.10988],"tcp_to_object_dist_end":0.06959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.48412,-0.13215,0.03562],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.02615,"object_to_goal_dist_start":0.19823,"object_z_max":0.04185,"peak_contact_force":0.7231,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2362.0,"raw_peak_contact_force":122.31103,"subtask_id":"push_to_goal","tcp_end":[0.49427,-0.18434,0.04589],"tcp_start":[0.51539,0.11175,0.05211],"tcp_to_object_dist_end":0.05415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49233,-0.14749,0.02499],"object_pos_start":[0.48412,-0.13215,0.03562],"object_to_goal_dist_end":0.00808,"object_to_goal_dist_start":0.02615,"object_z_max":0.03562,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3861.0,"raw_peak_contact_force":4.69134,"tcp_end":[0.49125,-0.18343,0.16943],"tcp_start":[0.49427,-0.18434,0.04589],"tcp_to_object_dist_end":0.14885,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```