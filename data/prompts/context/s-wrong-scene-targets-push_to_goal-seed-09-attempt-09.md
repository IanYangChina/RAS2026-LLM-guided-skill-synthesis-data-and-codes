## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.3101 | 0.06 | ❌ rejected |
| 8 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.3984 | 0.00 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1278 | 0.40 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1881 | 0.41 | ✅ accepted |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1901 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5444299044764102, -0.025581934909493356, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5444299044764102, -0.025581934909493356, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.310) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: push
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
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
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=task_goal_direction, distance=0.0, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.2]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.310
- **task_score** (E): 0.056
- **fitness_score**: 0.050  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2000 |
| descend_to_contact | 1.00 | 1.00 | 0.0670 |
| push | 1.00 | 1.00 | 0.0894 |
| retract | 0.67 | 1.00 | 0.1606 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, 0.005, 0.106) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.515, 0.005, 0.106)→(0.508, -0.036, 0.055) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push | push | 1.00 / step_budget | (0.508, -0.036, 0.055)→(0.551, 0.017, 0.033) | (0.518, -0.020, 0.025)→(0.531, 0.003, 0.030) | 0.139→0.165 | 1.00 / 2.667 | 67.445 | 221.437 |
| retract | retract | 0.67 / step_budget | (0.551, 0.017, 0.033)→(0.531, -0.000, 0.189) | (0.531, 0.003, 0.030)→(0.537, -0.005, 0.025) | 0.165→0.159 | 1.00 / 4.000 | 0.245 | 38.024 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.175
- lateral_force_integral: None
- approach_alignment: 0.553
- goal_progress: 0.167
- terminal_score: 0.167
- phase_score: 0.087
- phase_breakdown.push_to_goal_score: 0.086
- phase_breakdown.approach_object_score: 0.089

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.119
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.167
- **Median Q (composite search score)**: -0.345
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: approach.approach_offset_z
- **Final σ (mean)**: 0.427


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16327,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.08,"approach.approach_speed":0.14756,"approach.arc_height":0.09648,"descend_to_contact.descend_force_threshold":7.58416,"descend_to_contact.descend_speed":0.16753,"push.push_contact_force_threshold":8.66455,"push.push_distance":0.20872,"push.push_speed":0.18681,"push.retry_offset_x":0.00847,"push.retry_offset_y":0.00259,"retract.retract_speed":0.11226},"optimized_scores":{"best_composite_score":-0.3447,"best_fitness_score":0.0153,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":526.0,"contact_point_centroid":[0.56451,-0.01247,0.04681],"force_p95":208.94463,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":226.01521,"mean_force":176.01072,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.55505,-0.00898,0.04828]},{"body_a":"world","body_b":"push_box","contact_count":1424.0,"contact_point_centroid":[0.55747,-0.0138,-0.00061],"force_p95":200.94334,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.0732,"mean_force":65.80879,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54934,-0.01773,0.04928]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.58312,0.02533,0.04643],"force_p95":73.98608,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.21674,"mean_force":27.56252,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58066,0.03674,0.04622]},{"body_a":"world","body_b":"push_box","contact_count":3795.0,"contact_point_centroid":[0.58096,-0.01322,-4e-05],"force_p95":0.24669,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.86881,"mean_force":0.61594,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56981,0.017,0.13283]},{"body_a":"world","body_b":"push_box","contact_count":3276.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51989,0.04933,0.19648]},{"body_a":"world","body_b":"push_box","contact_count":1228.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5337,-0.02838,0.07574]}],"total_contact_groups":6},"final_pose_error":0.01339,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.58112,-0.01378,0.02499],"final_tcp_position":[0.56306,-0.0005,0.21806],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":819.0,"n_steps_budget":870.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3276.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54046,-0.0121,0.1006],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":307.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.52936,-0.04471,0.05418],"tcp_start":[0.54046,-0.0121,0.1006],"tcp_to_object_dist_end":0.03802,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":526.0,"n_steps_budget":600.0,"object_pos_end":[0.56508,-0.00191,0.03123],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.16188,"object_to_goal_dist_start":0.13211,"object_z_max":0.03113,"peak_contact_force":189.02697,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1950.0,"raw_peak_contact_force":226.01521,"subtask_id":"push_to_goal","tcp_end":[0.5815,0.037,0.04239],"tcp_start":[0.52936,-0.04471,0.05418],"tcp_to_object_dist_end":0.04368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58112,-0.01378,0.02499],"object_pos_start":[0.56508,-0.00191,0.03123],"object_to_goal_dist_end":0.15854,"object_to_goal_dist_start":0.16188,"object_z_max":0.03145,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3844.0,"raw_peak_contact_force":107.21674,"tcp_end":[0.56306,-0.0005,0.21806],"tcp_start":[0.5815,0.037,0.04239],"tcp_to_object_dist_end":0.19437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55472,-0.03508,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97222,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.08661,"approach.approach_speed":0.05167,"approach.arc_height":0.09779,"descend_to_contact.descend_force_threshold":11.93456,"descend_to_contact.descend_speed":0.1018,"push.push_contact_force_threshold":1.34169,"push.push_distance":0.24955,"push.push_speed":0.16157,"push.retry_offset_x":-0.0174,"push.retry_offset_y":0.01744,"retract.retract_speed":0.11551},"optimized_scores":{"best_composite_score":-0.3445,"best_fitness_score":0.0155,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":440.0,"contact_point_centroid":[0.57427,-0.00891,0.04683],"force_p95":183.2809,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":227.6174,"mean_force":138.38831,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.56595,-0.0039,0.04787]},{"body_a":"world","body_b":"push_box","contact_count":1081.0,"contact_point_centroid":[0.57038,-0.00714,-0.00063],"force_p95":177.33344,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":214.19939,"mean_force":56.96966,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.56458,-0.00186,0.04482]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52315,0.05038,0.20627]},{"body_a":"world","body_b":"push_box","contact_count":1788.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54143,-0.01602,0.07992]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.57243,0.02496,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24514,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58335,0.04803,0.10541]}],"total_contact_groups":5},"final_pose_error":0.0281,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.57243,0.02496,0.02499],"final_tcp_position":[0.57232,0.02929,0.19696],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54984,0.01069,0.10983],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":447.0,"n_steps_budget":780.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.53585,-0.04287,0.0541],"tcp_start":[0.54984,0.01069,0.10983],"tcp_to_object_dist_end":0.03556,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.57245,0.02503,0.02474],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.18944,"object_to_goal_dist_start":0.12728,"object_z_max":0.03597,"peak_contact_force":0.24533,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1521.0,"raw_peak_contact_force":227.6174,"subtask_id":"push_to_goal","tcp_end":[0.59836,0.06689,0.02161],"tcp_start":[0.53585,-0.04287,0.0541],"tcp_to_object_dist_end":0.04933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57243,0.02496,0.02499],"object_pos_start":[0.57245,0.02503,0.02474],"object_to_goal_dist_end":0.18936,"object_to_goal_dist_start":0.18944,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.57232,0.02929,0.19696],"tcp_start":[0.59836,0.06689,0.02161],"tcp_to_object_dist_end":0.17202,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45543,-9e-05,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65686,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.08034,"approach.approach_speed":0.219,"approach.arc_height":0.12534,"descend_to_contact.descend_force_threshold":7.33648,"descend_to_contact.descend_speed":0.07762,"push.push_contact_force_threshold":10.70184,"push.push_distance":0.10107,"push.push_speed":0.12319,"push.retry_offset_x":0.00862,"push.retry_offset_y":0.00893,"retract.retract_speed":0.06187},"optimized_scores":{"best_composite_score":-0.24096,"best_fitness_score":0.11904,"best_task_score":0.16704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":552.0,"contact_point_centroid":[0.45735,-0.02155,-0.0007],"force_p95":179.85153,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":210.67854,"mean_force":75.58952,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46863,-0.03793,0.04717]},{"body_a":"attachment","body_b":"push_box","contact_count":281.0,"contact_point_centroid":[0.47645,-0.03239,0.04384],"force_p95":190.87989,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":209.29257,"mean_force":147.29326,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46896,-0.03881,0.04661]},{"body_a":"attachment","body_b":"push_box","contact_count":123.0,"contact_point_centroid":[0.46612,-0.03726,0.04984],"force_p95":2.32895,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.61074,"mean_force":0.71811,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46688,-0.04914,0.04926]},{"body_a":"world","body_b":"push_box","contact_count":3375.0,"contact_point_centroid":[0.45496,-0.02384,-3e-05],"force_p95":0.46986,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.83785,"mean_force":0.29618,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46254,-0.03949,0.09973]},{"body_a":"world","body_b":"push_box","contact_count":2248.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47797,0.05037,0.20966]},{"body_a":"world","body_b":"push_box","contact_count":1892.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.45535,-0.00311,0.08032]}],"total_contact_groups":6},"final_pose_error":0.08439,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45596,-0.0274,0.02499],"final_tcp_position":[0.45842,-0.02966,0.15164],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":562.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.45405,0.01574,0.10865],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":473.0,"n_steps_budget":870.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.45927,-0.02113,0.05594],"tcp_start":[0.45405,0.01574,0.10865],"tcp_to_object_dist_end":0.03763,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.45473,-0.01479,0.03463],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.14291,"object_to_goal_dist_start":0.1564,"object_z_max":0.03536,"peak_contact_force":13.06173,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":833.0,"raw_peak_contact_force":210.67854,"subtask_id":"push_to_goal","tcp_end":[0.47194,-0.05284,0.03478],"tcp_start":[0.45927,-0.02113,0.05594],"tcp_to_object_dist_end":0.04176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45596,-0.0274,0.02499],"object_pos_start":[0.45473,-0.01479,0.03463],"object_to_goal_dist_end":0.13027,"object_to_goal_dist_start":0.14291,"object_z_max":0.03463,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3498.0,"raw_peak_contact_force":6.61074,"tcp_end":[0.45842,-0.02966,0.15164],"tcp_start":[0.47194,-0.05284,0.03478],"tcp_to_object_dist_end":0.12669,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```