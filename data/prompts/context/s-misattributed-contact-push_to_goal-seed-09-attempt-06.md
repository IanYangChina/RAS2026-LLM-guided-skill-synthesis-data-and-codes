## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1472 | 0.94 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1506 | 0.95 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1555 | 0.96 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0181 | 0.39 | ❌ rejected |
| 2 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1608 | 0.62 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.964, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.147) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
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
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
  parameters:
    approach_behind:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_contact
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
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
- id: push_forward
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}, tolerance=0.02
  - parameter_bindings:
    - approach_behind: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - parameter_bindings: none
- **push_forward** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.147
- **task_score** (E): 0.943
- **fitness_score**: 0.377  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2045 |
| descend_contact | 1.00 | 1.00 | 0.1437 |
| push_forward | 1.00 | 1.00 | 0.1621 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.540, 0.105, 0.152) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_contact | descend | 1.00 / step_budget | (0.540, 0.105, 0.152)→(0.523, 0.033, 0.031) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 2.667 | 2.738 | 50.981 |
| push_forward | push | 1.00 / step_budget | (0.523, 0.033, 0.031)→(0.502, -0.118, 0.021) | (0.518, -0.020, 0.025)→(0.499, -0.154, 0.026) | 0.139→0.008 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.962
- lateral_force_integral: None
- approach_alignment: 0.655
- goal_progress: 0.961
- terminal_score: 0.961
- phase_score: 0.000
- phase_breakdown.reach_object_score: 0.000
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.385
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.961
- **Median Q (composite search score)**: 0.146
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: push_forward.push_speed
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91736,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.1329,"approach_1.approach_height":0.08958,"push_forward.push_speed":0.07789,"push_forward.push_stroke":0.12397},"optimized_scores":{"best_composite_score":0.14118,"best_fitness_score":0.37118,"best_task_score":0.92796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":275.0,"contact_point_centroid":[0.52925,-0.06527,0.02783],"force_p95":36.29301,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.50023,"mean_force":6.15485,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52785,-0.05352,0.02293]},{"body_a":"world","body_b":"push_box","contact_count":594.0,"contact_point_centroid":[0.52871,-0.07198,-9e-05],"force_p95":16.9404,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.61822,"mean_force":3.20444,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53621,-0.03002,0.02461]},{"body_a":"world","body_b":"push_box","contact_count":1744.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53723,0.04359,0.21391]},{"body_a":"world","body_b":"push_box","contact_count":1380.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.56703,0.06005,0.07796]}],"total_contact_groups":4},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49832,-0.15927,0.02635],"final_tcp_position":[0.50478,-0.12328,0.0204],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":49.50023,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.57741,0.0892,0.12688],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":345.0,"n_steps_budget":780.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.55029,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":869.0,"raw_peak_contact_force":49.50023,"tcp_end":[0.55878,0.02909,0.03091],"tcp_start":[0.57741,0.0892,0.12688],"tcp_to_object_dist_end":0.05683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.49832,-0.15927,0.02635],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.00952,"object_to_goal_dist_start":0.13211,"object_z_max":0.02669,"peak_contact_force":0.24525,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50478,-0.12328,0.0204],"tcp_start":[0.55878,0.02909,0.03091],"tcp_to_object_dist_end":0.03704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08738,"average_solve_count":206.0,"average_success_count":206.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.18142,"approach_1.approach_height":0.13787,"push_forward.push_speed":0.02001,"push_forward.push_stroke":0.10435},"optimized_scores":{"best_composite_score":0.15456,"best_fitness_score":0.38456,"best_task_score":0.9614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":223.0,"contact_point_centroid":[0.53806,-0.06497,0.02286],"force_p95":29.99272,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.70083,"mean_force":4.38338,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53942,-0.05318,0.02224]},{"body_a":"world","body_b":"push_box","contact_count":606.0,"contact_point_centroid":[0.53507,-0.07187,-3e-05],"force_p95":10.43589,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.05977,"mean_force":1.97894,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.5502,-0.03052,0.024]},{"body_a":"world","body_b":"push_box","contact_count":1892.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55781,0.05753,0.23355]},{"body_a":"world","body_b":"push_box","contact_count":2036.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.59584,0.06844,0.09778]}],"total_contact_groups":4},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5029,-0.14604,0.02499],"final_tcp_position":[0.51386,-0.11045,0.0203],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":35.70083,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.61817,0.1166,0.16824],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.21807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.00051,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":829.0,"raw_peak_contact_force":35.70083,"tcp_end":[0.57515,0.01834,0.03015],"tcp_start":[0.61817,0.1166,0.16824],"tcp_to_object_dist_end":0.05743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.5029,-0.14604,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.00491,"object_to_goal_dist_start":0.12728,"object_z_max":0.02546,"peak_contact_force":0.24525,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51386,-0.11045,0.0203],"tcp_start":[0.57515,0.01834,0.03015],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92683,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.12719,"approach_1.approach_height":0.12458,"push_forward.push_speed":0.08872,"push_forward.push_stroke":0.14428},"optimized_scores":{"best_composite_score":0.14594,"best_fitness_score":0.37594,"best_task_score":0.93985},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":297.0,"contact_point_centroid":[0.47339,-0.06143,0.03672],"force_p95":44.39125,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.74158,"mean_force":10.41623,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.46541,-0.04976,0.02425]},{"body_a":"world","body_b":"push_box","contact_count":723.0,"contact_point_centroid":[0.46831,-0.06598,-9e-05],"force_p95":24.48739,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.29392,"mean_force":4.91052,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.45645,-0.02025,0.02604]},{"body_a":"push_box","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.49702,-0.05103,0.05066],"force_p95":23.31868,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.06989,"mean_force":3.86521,"phase_index":2.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.46119,-0.03594,0.02501]},{"body_a":"world","body_b":"push_box","contact_count":1520.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46301,0.05274,0.23117]},{"body_a":"world","body_b":"push_box","contact_count":1992.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.42964,0.08045,0.09661]}],"total_contact_groups":5},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49435,-0.1575,0.02545],"final_tcp_position":[0.4878,-0.12106,0.02081],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":67.74158,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42559,0.10804,0.16204],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":498.0,"n_steps_budget":960.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":7.66367,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1085.0,"raw_peak_contact_force":67.74158,"tcp_end":[0.43614,0.05229,0.03227],"tcp_start":[0.42559,0.10804,0.16204],"tcp_to_object_dist_end":0.05629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49435,-0.1575,0.02545],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00941,"object_to_goal_dist_start":0.1564,"object_z_max":0.02647,"peak_contact_force":0.24525,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4878,-0.12106,0.02081],"tcp_start":[0.43614,0.05229,0.03227],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```