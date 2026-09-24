## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1278 | 0.40 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1881 | 0.41 | ✅ accepted |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1901 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.0007 | 0.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1783 | 0.40 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.128) — your mutation base

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

- **Composite score**: 0.128
- **task_score** (E): 0.404
- **fitness_score**: 0.488  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1388 |
| descend | 1.00 | 1.00 | 0.1242 |
| push | 1.00 | 1.00 | 0.2735 |
| retract | 0.00 | 1.00 | 0.1636 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.018, 0.171) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.514, -0.018, 0.171)→(0.528, -0.020, 0.047) | (0.518, -0.020, 0.025)→(0.522, -0.020, 0.024) | 0.139→0.139 | 1.00 / 5.000 | 252.679 | 275.121 |
| push | push | 1.00 / time_limit | (0.528, -0.020, 0.047)→(0.470, -0.272, 0.022) | (0.522, -0.020, 0.024)→(0.525, -0.073, 0.025) | 0.139→0.083 | 1.00 / 4.000 | 0.245 | 167.013 |
| retract | retract | 0.00 / step_budget | (0.470, -0.272, 0.022)→(0.498, -0.159, 0.131) | (0.525, -0.073, 0.025)→(0.525, -0.073, 0.025) | 0.083→0.083 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.452
- lateral_force_integral: None
- approach_alignment: 0.837
- goal_progress: 0.441
- terminal_score: 0.441
- phase_score: 0.556
- phase_breakdown.push_to_goal_score: 0.448
- phase_breakdown.approach_object_score: 0.808

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.510
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.441
- **Median Q (composite search score)**: 0.118
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11538,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.13982,"approach.approach_speed":0.07539,"descend.descend_speed":0.12884,"push.lateral_offset_x":0.01488,"push.push_distance":0.25775,"push.push_speed":0.18737},"optimized_scores":{"best_composite_score":0.11541,"best_fitness_score":0.47541,"best_task_score":0.39036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":94.0,"contact_point_centroid":[0.55717,-0.02524,0.04692],"force_p95":253.85169,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":263.45755,"mean_force":217.71272,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54577,-0.02538,0.04897]},{"body_a":"attachment","body_b":"push_box","contact_count":294.0,"contact_point_centroid":[0.55412,-0.05135,0.04828],"force_p95":152.13811,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.03646,"mean_force":110.44725,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54503,-0.05694,0.04893]},{"body_a":"world","body_b":"push_box","contact_count":1772.0,"contact_point_centroid":[0.54484,-0.02566,-0.0001],"force_p95":109.17392,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.31581,"mean_force":11.8663,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53885,-0.02434,0.09941]},{"body_a":"world","body_b":"push_box","contact_count":2738.0,"contact_point_centroid":[0.53702,-0.06899,-0.00014],"force_p95":81.03661,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.68678,"mean_force":12.17691,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50058,-0.14899,0.03347]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51743,-0.01132,0.23584]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53345,-0.07673,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47519,-0.19949,0.07781]}],"total_contact_groups":6},"final_pose_error":0.1187,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53345,-0.07673,0.02499],"final_tcp_position":[0.49828,-0.14808,0.13689],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":263.45755,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.53744,-0.02323,0.17152],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":445.0,"n_steps_budget":720.0,"object_pos_end":[0.54859,-0.0258,0.02378],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13337,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":241.33837,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1866.0,"raw_peak_contact_force":263.45755,"tcp_end":[0.5534,-0.02581,0.0469],"tcp_start":[0.53744,-0.02323,0.17152],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.53345,-0.07673,0.02499],"object_pos_start":[0.54859,-0.0258,0.02378],"object_to_goal_dist_end":0.08054,"object_to_goal_dist_start":0.13337,"object_z_max":0.03537,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3032.0,"raw_peak_contact_force":157.03646,"subtask_id":"push_to_goal","tcp_end":[0.45522,-0.25349,0.02189],"tcp_start":[0.5534,-0.02581,0.0469],"tcp_to_object_dist_end":0.19332,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53345,-0.07673,0.02499],"object_pos_start":[0.53345,-0.07673,0.02499],"object_to_goal_dist_end":0.08054,"object_to_goal_dist_start":0.08054,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49828,-0.14808,0.13689],"tcp_start":[0.45522,-0.25349,0.02189],"tcp_to_object_dist_end":0.13729,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7651,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.13748,"approach.approach_speed":0.05647,"descend.descend_speed":0.13542,"push.lateral_offset_x":0.00576,"push.push_distance":0.29699,"push.push_speed":0.19175},"optimized_scores":{"best_composite_score":0.15022,"best_fitness_score":0.51022,"best_task_score":0.44123},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.56727,-0.03455,0.04701],"force_p95":251.14342,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":258.35134,"mean_force":213.6541,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.55577,-0.03479,0.04883]},{"body_a":"attachment","body_b":"push_box","contact_count":313.0,"contact_point_centroid":[0.55959,-0.06188,0.04843],"force_p95":145.48829,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.70848,"mean_force":104.90343,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.55049,-0.06773,0.04906]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.55521,-0.03514,-0.0001],"force_p95":105.63927,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.50649,"mean_force":11.79594,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54878,-0.03347,0.09794]},{"body_a":"world","body_b":"push_box","contact_count":3157.0,"contact_point_centroid":[0.5425,-0.08269,-0.00013],"force_p95":74.57077,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.83778,"mean_force":10.71249,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48806,-0.1724,0.03331]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52225,-0.01573,0.23378]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5386,-0.09026,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.45328,-0.23113,0.07412]}],"total_contact_groups":6},"final_pose_error":0.14052,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5386,-0.09026,0.02499],"final_tcp_position":[0.48448,-0.17758,0.12911],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":258.35134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54716,-0.03211,0.16814],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":431.0,"n_steps_budget":690.0,"object_pos_end":[0.5589,-0.03537,0.02377],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12888,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":238.45167,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1804.0,"raw_peak_contact_force":258.35134,"tcp_end":[0.56329,-0.03536,0.04675],"tcp_start":[0.54716,-0.03211,0.16814],"tcp_to_object_dist_end":0.02339,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.5386,-0.09026,0.02499],"object_pos_start":[0.5589,-0.03537,0.02377],"object_to_goal_dist_end":0.07112,"object_to_goal_dist_start":0.12888,"object_z_max":0.03503,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3470.0,"raw_peak_contact_force":149.70848,"subtask_id":"push_to_goal","tcp_end":[0.42497,-0.28735,0.0224],"tcp_start":[0.56329,-0.03536,0.04675],"tcp_to_object_dist_end":0.22751,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5386,-0.09026,0.02499],"object_pos_start":[0.5386,-0.09026,0.02499],"object_to_goal_dist_end":0.07112,"object_to_goal_dist_start":0.07112,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48448,-0.17758,0.12911],"tcp_start":[0.42497,-0.28735,0.0224],"tcp_to_object_dist_end":0.14627,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.43243,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.13738,"approach.approach_speed":0.28246,"descend.descend_speed":0.15426,"push.lateral_offset_x":-0.00959,"push.push_distance":0.29741,"push.push_speed":0.18723},"optimized_scores":{"best_composite_score":0.11784,"best_fitness_score":0.47784,"best_task_score":0.37997},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.46876,-0.00014,0.04638],"force_p95":294.73663,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":303.55451,"mean_force":256.04601,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45835,-0.00017,0.05031]},{"body_a":"attachment","body_b":"push_box","contact_count":285.0,"contact_point_centroid":[0.48731,-0.0266,0.04581],"force_p95":180.33143,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":194.29495,"mean_force":112.42632,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47863,-0.03149,0.04884]},{"body_a":"world","body_b":"push_box","contact_count":2997.0,"contact_point_centroid":[0.50108,-0.04699,-0.00014],"force_p95":117.01246,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.63217,"mean_force":11.04219,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50252,-0.15641,0.03194]},{"body_a":"world","body_b":"push_box","contact_count":1784.0,"contact_point_centroid":[0.45562,-9e-05,-0.00011],"force_p95":126.88951,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.55415,"mean_force":13.09126,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45459,-0.00016,0.10117]},{"body_a":"world","body_b":"push_box","contact_count":1504.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47858,-6e-05,0.23682]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50343,-0.05309,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51928,-0.21083,0.0724]}],"total_contact_groups":6},"final_pose_error":0.13758,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50343,-0.05309,0.02499],"final_tcp_position":[0.51211,-0.15072,0.12844],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":303.55451,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.4571,-0.00012,0.17195],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":446.0,"n_steps_budget":630.0,"object_pos_end":[0.45898,-0.0001,0.02357],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15542,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":278.24812,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1873.0,"raw_peak_contact_force":303.55451,"tcp_end":[0.46582,-0.00018,0.04795],"tcp_start":[0.4571,-0.00012,0.17195],"tcp_to_object_dist_end":0.02531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.50343,-0.05309,0.02499],"object_pos_start":[0.45898,-0.0001,0.02357],"object_to_goal_dist_end":0.09697,"object_to_goal_dist_start":0.15542,"object_z_max":0.03531,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3282.0,"raw_peak_contact_force":194.29495,"subtask_id":"push_to_goal","tcp_end":[0.53049,-0.274,0.0206],"tcp_start":[0.46582,-0.00018,0.04795],"tcp_to_object_dist_end":0.2226,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50343,-0.05309,0.02499],"object_pos_start":[0.50343,-0.05309,0.02499],"object_to_goal_dist_end":0.09697,"object_to_goal_dist_start":0.09697,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51211,-0.15072,0.12844],"tcp_start":[0.53049,-0.274,0.0206],"tcp_to_object_dist_end":0.14251,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```