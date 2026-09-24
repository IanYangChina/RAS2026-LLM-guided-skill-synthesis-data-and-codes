## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

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

## Current Skill (Q=0.325) — your mutation base

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

- **Composite score**: 0.325
- **task_score** (E): 0.919
- **fitness_score**: 0.794  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_object | 1.00 | 1.00 | 0.2744 |
| descend_to_contact | 0.33 | 1.00 | 0.0483 |
| push_object_to_goal | 1.00 | 1.00 | 0.2579 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.551, 0.121, 0.064) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 0.33 / step_budget | (0.551, 0.121, 0.064)→(0.548, 0.094, 0.045) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.333 | 17.468 | 0.245 |
| push_object_to_goal | push | 1.00 / step_budget | (0.548, 0.094, 0.045)→(0.495, -0.157, 0.044) | (0.531, 0.007, 0.025)→(0.512, -0.152, 0.027) | 0.161→0.014 | 1.00 / 2.667 | 5.810 | 81.180 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.709
- goal_progress: 0.952
- terminal_score: 0.952
- phase_score: 0.809
- phase_breakdown.approach_object_score: 0.475
- phase_breakdown.push_to_goal_score: 0.952

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.952
- **Median Q (composite search score)**: 0.195
- **K-run variance**: 0.0436
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.45652,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_behind":0.18301,"approach_behind_object.approach_speed":0.19272,"approach_behind_object.approach_tolerance":0.02928,"descend_to_contact.approach_behind":0.12478,"descend_to_contact.descend_force_threshold":6.07772,"descend_to_contact.descend_speed":0.09537,"push_object_to_goal.push_overshoot":0.00812,"push_object_to_goal.push_retry_x":0.01708,"push_object_to_goal.push_retry_y":0.02213,"push_object_to_goal.push_speed":0.16367,"push_object_to_goal.push_tolerance":0.05473},"optimized_scores":{"best_composite_score":0.19465,"best_fitness_score":0.77465,"best_task_score":0.92704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":85.0,"contact_point_centroid":[0.5394,-0.03713,0.04303],"force_p95":20.68693,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.60786,"mean_force":5.38707,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.53894,-0.02569,0.04145]},{"body_a":"world","body_b":"push_box","contact_count":556.0,"contact_point_centroid":[0.54607,-0.0219,-5e-05],"force_p95":5.93155,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.48858,"mean_force":1.17939,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.56483,0.05047,0.0412]},{"body_a":"world","body_b":"push_box","contact_count":2344.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.55015,0.07954,0.18027]},{"body_a":"world","body_b":"push_box","contact_count":2052.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.59491,0.14058,0.0492]}],"total_contact_groups":4},"final_pose_error":0.03967,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5096,-0.15669,0.0251],"final_tcp_position":[0.50732,-0.1198,0.04367],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":59.60786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2344.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.60293,0.16119,0.06068],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.59076,0.12148,0.04399],"tcp_start":[0.60293,0.16119,0.06068],"tcp_to_object_dist_end":0.1273,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.5096,-0.15669,0.0251],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.0117,"object_to_goal_dist_start":0.16043,"object_z_max":0.02807,"peak_contact_force":9.75266,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":641.0,"raw_peak_contact_force":59.60786,"subtask_id":"push_to_goal","tcp_end":[0.50732,-0.1198,0.04367],"tcp_start":[0.59076,0.12148,0.04399],"tcp_to_object_dist_end":0.04136,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80921,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_behind":0.09412,"approach_behind_object.approach_speed":0.08365,"approach_behind_object.approach_tolerance":0.02054,"descend_to_contact.approach_behind":0.11148,"descend_to_contact.descend_force_threshold":3.9346,"descend_to_contact.descend_speed":0.09942,"push_object_to_goal.push_overshoot":0.1234,"push_object_to_goal.push_retry_x":-0.04985,"push_object_to_goal.push_retry_y":-0.00952,"push_object_to_goal.push_speed":0.13958,"push_object_to_goal.push_tolerance":0.03453},"optimized_scores":{"best_composite_score":0.16089,"best_fitness_score":0.74089,"best_task_score":0.87792},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":154.0,"contact_point_centroid":[0.52543,-0.04432,0.04944],"force_p95":44.3952,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.71264,"mean_force":6.73516,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.51724,-0.03545,0.0418]},{"body_a":"world","body_b":"push_box","contact_count":829.0,"contact_point_centroid":[0.53449,-0.05656,-0.00014],"force_p95":9.49356,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.92501,"mean_force":1.70015,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.51761,-0.03482,0.04264]},{"body_a":"world","body_b":"push_box","contact_count":2196.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.52232,0.058,0.18279]},{"body_a":"world","body_b":"push_box","contact_count":1936.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54839,0.13109,0.05166]}],"total_contact_groups":4},"final_pose_error":0.03939,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52311,-0.14739,0.02493],"final_tcp_position":[0.48069,-0.23243,0.04393],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":61.71264,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54683,0.11823,0.06421],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.55283,0.14303,0.04494],"tcp_start":[0.54683,0.11823,0.06421],"tcp_to_object_dist_end":0.10915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.52311,-0.14739,0.02493],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.02326,"object_to_goal_dist_start":0.1905,"object_z_max":0.03258,"peak_contact_force":0.24364,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":983.0,"raw_peak_contact_force":61.71264,"subtask_id":"push_to_goal","tcp_end":[0.48069,-0.23243,0.04393],"tcp_start":[0.55283,0.14303,0.04494],"tcp_to_object_dist_end":0.09692,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09615,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_object.approach_behind":0.11059,"approach_behind_object.approach_speed":0.08748,"approach_behind_object.approach_tolerance":0.03183,"descend_to_contact.approach_behind":0.02909,"descend_to_contact.descend_force_threshold":4.85716,"descend_to_contact.descend_speed":0.1092,"push_object_to_goal.push_overshoot":0.00654,"push_object_to_goal.push_retry_x":-0.00084,"push_object_to_goal.push_retry_y":0.01491,"push_object_to_goal.push_speed":0.18294,"push_object_to_goal.push_tolerance":0.0315},"optimized_scores":{"best_composite_score":0.61992,"best_fitness_score":0.86659,"best_task_score":0.95249},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.50154,-0.06427,0.04455],"force_p95":63.57344,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.2196,"mean_force":10.16678,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49898,-0.05275,0.04451]},{"body_a":"world","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.50643,-0.09955,-4e-05],"force_p95":40.17944,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.50934,"mean_force":9.66457,"phase_index":2.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49913,-0.04434,0.04459]},{"body_a":"world","body_b":"push_box","contact_count":1964.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind_object","phase_type":"approach","tcp_position_centroid":[0.50147,0.04056,0.18474]},{"body_a":"world","body_b":"push_box","contact_count":2072.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5011,0.05095,0.05503]}],"total_contact_groups":4},"final_pose_error":0.03922,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50337,-0.1516,0.03],"final_tcp_position":[0.49804,-0.11775,0.04446],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":122.2196,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.50435,0.08301,0.06723],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":518.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":51.91348,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.50136,0.01812,0.04693],"tcp_start":[0.50435,0.08301,0.06723],"tcp_to_object_dist_end":0.04308,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":166.0,"n_steps_budget":630.0,"object_pos_end":[0.50337,-0.1516,0.03],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00624,"object_to_goal_dist_start":0.13127,"object_z_max":0.03118,"peak_contact_force":7.43231,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":179.0,"raw_peak_contact_force":122.2196,"subtask_id":"push_to_goal","tcp_end":[0.49804,-0.11775,0.04446],"tcp_start":[0.50136,0.01812,0.04693],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```