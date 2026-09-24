## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.923, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5531667326686841, 0.0013593063377233885, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.123) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_object
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
- id: approach_behind_object
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
    - 0.025
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_behind:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_object
- id: push_object_to_goal
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    push_overshoot:
      type: scalar
      range:
      - 0.0
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_retry_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_retry_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_behind: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_object_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_overshoot: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - push_retry_y: status=consumed; consumers=retry.offset.y (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.123
- **task_score** (E): 0.895
- **fitness_score**: 0.753  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_object | 1.00 | 1.00 | 0.2207 |
| descend_to_contact | 1.00 | 1.00 | 0.1813 |
| push_object_to_goal | 1.00 | 1.00 | 0.3796 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.558, 0.124, 0.141) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.558, 0.124, 0.141)→(0.554, 0.185, 0.053) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_object_to_goal | push | 1.00 / step_budget | (0.554, 0.185, 0.053)→(0.493, -0.187, 0.048) | (0.531, 0.007, 0.025)→(0.506, -0.140, 0.031) | 0.161→0.017 | 1.00 / 1.333 | 0.707 | 154.560 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.942
- lateral_force_integral: None
- approach_alignment: 0.794
- goal_progress: 0.931
- terminal_score: 0.931
- phase_score: 0.656
- phase_breakdown.approach_object_score: 0.015
- phase_breakdown.push_to_goal_score: 0.931

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.766
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.931
- **Median Q (composite search score)**: 0.131
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.319


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45641,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_behind":0.22495,"approach_behind_object.approach_height":0.09433,"approach_behind_object.approach_speed":0.02008,"approach_behind_object.approach_tolerance":0.02457,"descend_to_contact.descend_behind":0.04067,"descend_to_contact.descend_speed":0.15906,"descend_to_contact.descend_tolerance":0.00949,"push_object_to_goal.push_overshoot":0.07196,"push_object_to_goal.push_retry_x":-0.02157,"push_object_to_goal.push_retry_y":0.02155,"push_object_to_goal.push_speed":0.11819,"push_object_to_goal.push_tolerance":0.07232},"optimized_scores":{"best_composite_score":0.10194,"best_fitness_score":0.73194,"best_task_score":0.82639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":220.0,"contact_point_centroid":[0.54272,-0.04218,0.05299],"force_p95":137.71508,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.71388,"mean_force":105.37979,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.53784,-0.0418,0.05369]},{"body_a":"world","body_b":"push_box","contact_count":597.0,"contact_point_centroid":[0.54589,-0.0499,-0.00042],"force_p95":125.9291,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.2219,"mean_force":39.4328,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.5415,-0.0275,0.05254]},{"body_a":"world","body_b":"push_box","contact_count":2724.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.55675,0.09809,0.21139]},{"body_a":"world","body_b":"push_box","contact_count":1220.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.59214,0.13047,0.08664]}],"total_contact_groups":4},"final_pose_error":0.03954,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50813,-0.12419,0.03159],"final_tcp_position":[0.48758,-0.18017,0.04681],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":140.71388,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2724.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.6161,0.19811,0.12403],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.22909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":720.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.56922,0.05901,0.05294],"tcp_start":[0.6161,0.19811,0.12403],"tcp_to_object_dist_end":0.06605,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50813,-0.12419,0.03159],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02785,"object_to_goal_dist_start":0.16043,"object_z_max":0.04303,"peak_contact_force":0.59775,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":817.0,"raw_peak_contact_force":140.71388,"subtask_id":"push_to_goal","tcp_end":[0.48758,-0.18017,0.04681],"tcp_start":[0.56922,0.05901,0.05294],"tcp_to_object_dist_end":0.06155,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62326,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_behind":0.13866,"approach_behind_object.approach_height":0.0978,"approach_behind_object.approach_speed":0.09334,"approach_behind_object.approach_tolerance":0.02119,"descend_to_contact.descend_behind":0.29219,"descend_to_contact.descend_speed":0.05324,"descend_to_contact.descend_tolerance":0.01973,"push_object_to_goal.push_overshoot":0.0867,"push_object_to_goal.push_retry_x":-0.0028,"push_object_to_goal.push_retry_y":0.01738,"push_object_to_goal.push_speed":0.13079,"push_object_to_goal.push_tolerance":0.0481},"optimized_scores":{"best_composite_score":0.13123,"best_fitness_score":0.76123,"best_task_score":0.92739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1554.0,"contact_point_centroid":[0.53298,-0.00589,-0.00013],"force_p95":109.04824,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.1398,"mean_force":15.23915,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.5481,0.1125,0.04593]},{"body_a":"attachment","body_b":"push_box","contact_count":265.0,"contact_point_centroid":[0.51894,-0.08651,0.04909],"force_p95":148.19845,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.08828,"mean_force":87.21219,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.51411,-0.08213,0.0495]},{"body_a":"world","body_b":"push_box","contact_count":2032.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.52644,0.07757,0.21565]},{"body_a":"world","body_b":"push_box","contact_count":1748.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.56892,0.23077,0.08879]}],"total_contact_groups":4},"final_pose_error":0.03961,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50563,-0.15285,0.03731],"final_tcp_position":[0.49305,-0.19669,0.05038],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":157.1398,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.555,0.15745,0.13189],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.58542,0.30541,0.05005],"tcp_start":[0.555,0.15745,0.13189],"tcp_to_object_dist_end":0.27401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.50563,-0.15285,0.03731],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.01383,"object_to_goal_dist_start":0.1905,"object_z_max":0.03731,"peak_contact_force":0.0,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1819.0,"raw_peak_contact_force":157.1398,"subtask_id":"push_to_goal","tcp_end":[0.49305,-0.19669,0.05038],"tcp_start":[0.58542,0.30541,0.05005],"tcp_to_object_dist_end":0.04745,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94253,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_behind":0.03717,"approach_behind_object.approach_height":0.12252,"approach_behind_object.approach_speed":0.11492,"approach_behind_object.approach_tolerance":0.01719,"descend_to_contact.descend_behind":0.22947,"descend_to_contact.descend_speed":0.13312,"descend_to_contact.descend_tolerance":0.01986,"push_object_to_goal.push_overshoot":0.0729,"push_object_to_goal.push_retry_x":0.02423,"push_object_to_goal.push_retry_y":-0.02684,"push_object_to_goal.push_speed":0.07617,"push_object_to_goal.push_tolerance":0.05033},"optimized_scores":{"best_composite_score":0.13627,"best_fitness_score":0.76627,"best_task_score":0.93123},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":234.0,"contact_point_centroid":[0.50948,-0.06354,0.05217],"force_p95":162.46221,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.82765,"mean_force":110.1478,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50473,-0.06139,0.05273]},{"body_a":"world","body_b":"push_box","contact_count":1395.0,"contact_point_centroid":[0.50547,-0.04453,-0.00017],"force_p95":92.00327,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.27046,"mean_force":18.81671,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50407,0.0395,0.05087]},{"body_a":"world","body_b":"push_box","contact_count":1036.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.50086,0.00735,0.23499]},{"body_a":"world","body_b":"push_box","contact_count":1820.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50439,0.10292,0.1093]}],"total_contact_groups":4},"final_pose_error":0.03937,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50487,-0.14251,0.02367],"final_tcp_position":[0.49847,-0.18357,0.04772],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":165.82765,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":840.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.50256,0.01535,0.16671],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.50834,0.19177,0.05502],"tcp_start":[0.50256,0.01535,0.16671],"tcp_to_object_dist_end":0.21274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.50487,-0.14251,0.02367],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00903,"object_to_goal_dist_start":0.13127,"object_z_max":0.03511,"peak_contact_force":1.52219,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1629.0,"raw_peak_contact_force":165.82765,"subtask_id":"push_to_goal","tcp_end":[0.49847,-0.18357,0.04772],"tcp_start":[0.50834,0.19177,0.05502],"tcp_to_object_dist_end":0.048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```