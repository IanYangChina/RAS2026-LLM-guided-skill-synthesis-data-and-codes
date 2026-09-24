## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → retract → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 11  | 0.0505 | 0.00 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 7  | 0.0484 | 0.00 | ✅ accepted |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | time_limit | 7  | -0.3700 | 0.00 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5  | 0.0248 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.025) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  weight: 0.3
- id: push_to_goal
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
  control: impedance_control
  termination: force_exceeded
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
    contact_offset:
      type: scalar
      range:
      - 0.015
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_force_threshold:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 1.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: pre_contact
- id: retract_contact
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
    - 0.0
    offset_along_axis:
      distance: 0.01
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_distance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_guard_force_threshold:
      type: scalar
      range:
      - 30.0
      - 80.0
      default: 50.0
      binds_to:
      - path: guards.force_limit_guard.threshold
        mode: replace
    push_retry_lateral:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal

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
    - contact_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **retract_contact** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.01, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_guard_force_threshold: status=consumed; consumers=guards.force_limit_guard.threshold (replace)
    - push_retry_lateral: status=consumed; consumers=retry.offset.y (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.025
- **task_score** (E): 0.302
- **fitness_score**: 0.329  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.306
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1874 |
| descend_1 | 1.00 | 1.00 | 0.0692 |
| retract_contact | 1.00 | 1.00 | 0.0170 |
| push_1 | 0.67 | 1.00 | 0.0633 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.001, 0.121) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / force_exceeded | (0.520, 0.001, 0.121)→(0.516, -0.003, 0.052) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 50611.365 | 0.245 |
| retract_contact | retract | 1.00 / step_budget | (0.516, -0.003, 0.052)→(0.513, -0.019, 0.052) | (0.518, -0.020, 0.025)→(0.517, -0.025, 0.025) | 0.139→0.133 | 1.00 / 3.333 | 16.194 | 58.076 |
| push_1 | push | 0.67 / time_limit | (0.513, -0.019, 0.052)→(0.487, -0.077, 0.049) | (0.517, -0.025, 0.025)→(0.509, -0.059, 0.031) | 0.133→0.099 | 1.00 / 2.667 | 15.143 | 64.313 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.451
- lateral_force_integral: None
- approach_alignment: 0.690
- goal_progress: 0.440
- terminal_score: 0.440
- phase_score: 0.453
- phase_breakdown.pre_contact_score: 0.538
- phase_breakdown.push_to_goal_score: 0.416

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.447
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.440
- **Median Q (composite search score)**: 0.151
- **K-run variance**: 0.0372
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.447


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59804,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07148,"approach_1.approach_offset":0.0111,"descend_1.contact_offset":0.01638,"descend_1.descend_force_threshold":2.79947,"push_1.max_push_time":2.81112,"push_1.push_distance":0.09849,"push_1.push_guard_force_threshold":79.72212,"push_1.push_retry_lateral":0.00337,"push_1.push_speed":0.09348,"retract_contact.retract_distance":0.02587,"retract_contact.retract_speed":0.06349},"optimized_scores":{"best_composite_score":0.17073,"best_fitness_score":0.44739,"best_task_score":0.43956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":524.0,"contact_point_centroid":[0.53338,-0.05301,0.05055],"force_p95":73.86624,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.29121,"mean_force":55.00444,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5247,-0.05948,0.0519]},{"body_a":"world","body_b":"push_box","contact_count":1259.0,"contact_point_centroid":[0.5356,-0.05976,-0.00026],"force_p95":58.44792,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.52811,"mean_force":23.41693,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52262,-0.0633,0.05113]},{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.5505,-0.01798,0.0495],"force_p95":51.10511,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.48477,"mean_force":47.73387,"phase_index":2.0,"phase_name":"retract_contact","phase_type":"retract","tcp_position_centroid":[0.53878,-0.0184,0.05166]},{"body_a":"world","body_b":"push_box","contact_count":429.0,"contact_point_centroid":[0.53692,-0.034,-0.00016],"force_p95":27.35682,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.03183,"mean_force":15.8745,"phase_index":2.0,"phase_name":"retract_contact","phase_type":"retract","tcp_position_centroid":[0.53891,-0.01805,0.05165]},{"body_a":"world","body_b":"push_box","contact_count":1508.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5188,-0.00651,0.20835]},{"body_a":"world","body_b":"push_box","contact_count":1320.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53952,-0.01241,0.08099]}],"total_contact_groups":6},"final_pose_error":0.00808,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52942,-0.08258,0.03342],"final_tcp_position":[0.50145,-0.11288,0.04693],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.53972,-0.01342,0.11416],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.54212,-0.01138,0.05246],"tcp_start":[0.53972,-0.01342,0.11416],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":140.0,"n_steps_budget":600.0,"object_pos_end":[0.54193,-0.03033,0.02476],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.1268,"object_to_goal_dist_start":0.13211,"object_z_max":0.02506,"peak_contact_force":0.00217,"phase_name":"retract_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":569.0,"raw_peak_contact_force":55.48477,"tcp_end":[0.53583,-0.02614,0.05158],"tcp_start":[0.54212,-0.01138,0.05246],"tcp_to_object_dist_end":0.02783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.52942,-0.08258,0.03342],"object_pos_start":[0.54193,-0.03033,0.02476],"object_to_goal_dist_end":0.07404,"object_to_goal_dist_start":0.1268,"object_z_max":0.03533,"peak_contact_force":0.44763,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1783.0,"raw_peak_contact_force":75.29121,"subtask_id":"push_to_goal","tcp_end":[0.50145,-0.11288,0.04693],"tcp_start":[0.53583,-0.02614,0.05158],"tcp_to_object_dist_end":0.0434,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63889,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08459,"approach_1.approach_offset":0.04792,"descend_1.contact_offset":0.01517,"descend_1.descend_force_threshold":4.46829,"push_1.max_push_time":7.03992,"push_1.push_distance":0.10037,"push_1.push_guard_force_threshold":74.51013,"push_1.push_retry_lateral":-0.00258,"push_1.push_speed":0.07704,"retract_contact.retract_distance":0.02725,"retract_contact.retract_speed":0.04469},"optimized_scores":{"best_composite_score":0.15126,"best_fitness_score":0.42793,"best_task_score":0.42797},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":768.0,"contact_point_centroid":[0.54093,-0.06199,0.05001],"force_p95":66.81147,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.94594,"mean_force":52.99462,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53085,-0.0667,0.05169]},{"body_a":"world","body_b":"push_box","contact_count":1702.0,"contact_point_centroid":[0.54342,-0.06717,-0.00027],"force_p95":58.51851,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.90808,"mean_force":24.38056,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53386,-0.05995,0.05158]},{"body_a":"attachment","body_b":"push_box","contact_count":150.0,"contact_point_centroid":[0.56522,-0.01896,0.04953],"force_p95":51.11887,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.53266,"mean_force":48.47395,"phase_index":2.0,"phase_name":"retract_contact","phase_type":"retract","tcp_position_centroid":[0.55349,-0.01918,0.05168]},{"body_a":"world","body_b":"push_box","contact_count":557.0,"contact_point_centroid":[0.55131,-0.03848,-0.00013],"force_p95":22.71199,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.95939,"mean_force":13.28179,"phase_index":2.0,"phase_name":"retract_contact","phase_type":"retract","tcp_position_centroid":[0.5536,-0.01897,0.05168]},{"body_a":"world","body_b":"push_box","contact_count":1504.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53057,0.00347,0.21377]},{"body_a":"world","body_b":"push_box","contact_count":1396.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55953,-0.0023,0.08704]}],"total_contact_groups":6},"final_pose_error":0.0061,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53965,-0.08977,0.03504],"final_tcp_position":[0.50608,-0.11333,0.04801],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.56387,0.00715,0.12541],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":349.0,"n_steps_budget":660.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.55791,-0.01196,0.05236],"tcp_start":[0.56387,0.00715,0.12541],"tcp_to_object_dist_end":0.03597,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":600.0,"object_pos_end":[0.55177,-0.03968,0.02474],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12186,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":48.5767,"phase_name":"retract_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":707.0,"raw_peak_contact_force":51.53266,"tcp_end":[0.54944,-0.02715,0.05164],"tcp_start":[0.55791,-0.01196,0.05236],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":772.0,"n_steps_budget":840.0,"object_pos_end":[0.53965,-0.08977,0.03504],"object_pos_start":[0.55177,-0.03968,0.02474],"object_to_goal_dist_end":0.07281,"object_to_goal_dist_start":0.12186,"object_z_max":0.03503,"peak_contact_force":0.50573,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2470.0,"raw_peak_contact_force":67.94594,"subtask_id":"push_to_goal","tcp_end":[0.50608,-0.11333,0.04801],"tcp_start":[0.54944,-0.02715,0.05164],"tcp_to_object_dist_end":0.04302,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45783,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07761,"approach_1.approach_offset":0.01174,"descend_1.contact_offset":0.01545,"descend_1.descend_force_threshold":2.10142,"push_1.max_push_time":1.36062,"push_1.push_distance":0.13777,"push_1.push_guard_force_threshold":39.42936,"push_1.push_retry_lateral":0.0034,"push_1.push_speed":0.06129,"retract_contact.retract_distance":0.02748,"retract_contact.retract_speed":0.07677},"optimized_scores":{"best_composite_score":-0.24772,"best_fitness_score":0.11228,"best_task_score":0.03856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":150.0,"contact_point_centroid":[0.46296,0.00565,0.04938],"force_p95":66.36138,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.2093,"mean_force":58.60445,"phase_index":2.0,"phase_name":"retract_contact","phase_type":"retract","tcp_position_centroid":[0.45125,0.00488,0.05143]},{"body_a":"world","body_b":"push_box","contact_count":433.0,"contact_point_centroid":[0.46206,-0.01122,-0.00019],"force_p95":47.01461,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.94816,"mean_force":20.67276,"phase_index":2.0,"phase_name":"retract_contact","phase_type":"retract","tcp_position_centroid":[0.45116,0.00513,0.05143]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.46596,-0.00305,0.04933],"force_p95":48.91889,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.70274,"mean_force":43.10125,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45425,-0.00393,0.05137]},{"body_a":"world","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.46397,-0.01683,-0.00021],"force_p95":20.4418,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.9026,"mean_force":16.03036,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45426,-0.00394,0.05137]},{"body_a":"world","body_b":"push_box","contact_count":1396.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47777,0.00471,0.21245]},{"body_a":"world","body_b":"push_box","contact_count":1448.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45091,0.0113,0.08628]}],"total_contact_groups":6},"final_pose_error":0.13756,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4577,-0.00571,0.02479],"final_tcp_position":[0.45427,-0.00404,0.05134],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":67.2093,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.45526,0.00975,0.12215],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":362.0,"n_steps_budget":630.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":47.02255,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.44896,0.01297,0.05242],"tcp_start":[0.45526,0.00975,0.12215],"tcp_to_object_dist_end":0.03107,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":150.0,"n_steps_budget":600.0,"object_pos_end":[0.45768,-0.00565,0.02483],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15043,"object_to_goal_dist_start":0.1564,"object_z_max":0.0251,"peak_contact_force":0.00229,"phase_name":"retract_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":583.0,"raw_peak_contact_force":67.2093,"tcp_end":[0.45423,-0.00383,0.05138],"tcp_start":[0.44896,0.01297,0.05242],"tcp_to_object_dist_end":0.02684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.4577,-0.00569,0.02481],"object_pos_start":[0.45768,-0.00565,0.02483],"object_to_goal_dist_end":0.15038,"object_to_goal_dist_start":0.15043,"object_z_max":0.02483,"peak_contact_force":44.47712,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":49.70274,"subtask_id":"push_to_goal","tcp_end":[0.45427,-0.00404,0.05134],"tcp_start":[0.45427,-0.00401,0.05135],"tcp_to_object_dist_end":0.0268,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```