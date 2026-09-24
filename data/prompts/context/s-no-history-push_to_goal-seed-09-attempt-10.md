## Search State

- **Seed**: 9
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.848, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.442) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_to_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_box
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
    - 0.1
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    pre_push_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: pre_push
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_box** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - pre_push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.442
- **task_score** (E): 0.848
- **fitness_score**: 0.672  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_box | 1.00 | 1.00 | 0.1346 |
| descend_to_contact | 1.00 | 1.00 | 0.1507 |
| push_to_goal | 1.00 | 0.67 | 0.1644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_box | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.014, 0.172) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.514, -0.014, 0.172)→(0.522, 0.022, 0.028) | (0.518, -0.020, 0.025)→(0.519, -0.021, 0.025) | 0.139→0.138 | 1.00 / 4.000 | 0.245 | 131.447 |
| push_to_goal | push | 1.00 / step_budget | (0.522, 0.022, 0.028)→(0.499, -0.132, 0.020) | (0.519, -0.021, 0.025)→(0.502, -0.165, 0.025) | 0.138→0.021 | 0.67 / 1.333 | 0.569 | 41.339 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.689
- goal_progress: 0.859
- terminal_score: 0.859
- phase_score: 0.557
- phase_breakdown.pre_push_score: 0.281
- phase_breakdown.push_to_goal_score: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.678
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.859
- **Median Q (composite search score)**: 0.440
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11765,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_box.approach_speed":0.32458,"descend_to_contact.descend_speed":0.13199,"descend_to_contact.pre_push_offset":0.05288,"push_to_goal.push_speed":0.09314},"optimized_scores":{"best_composite_score":0.44027,"best_fitness_score":0.67027,"best_task_score":0.8557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":263.0,"contact_point_centroid":[0.52512,-0.06954,0.02505],"force_p95":29.5813,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.56807,"mean_force":3.99129,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52637,-0.05795,0.02141]},{"body_a":"world","body_b":"push_box","contact_count":549.0,"contact_point_centroid":[0.52139,-0.07973,-7e-05],"force_p95":11.32461,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.06965,"mean_force":2.29439,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53211,-0.04197,0.02237]},{"body_a":"world","body_b":"push_box","contact_count":488.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_box","phase_type":"approach","tcp_position_centroid":[0.5156,-0.00836,0.24001]},{"body_a":"world","body_b":"push_box","contact_count":2768.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54238,0.00149,0.09777]}],"total_contact_groups":4},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48831,-0.16505,0.0248],"final_tcp_position":[0.50228,-0.13078,0.0202],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":41.56807,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_box","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":488.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.53195,-0.01803,0.17193],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_push","tcp_end":[0.55611,0.02161,0.02735],"tcp_start":[0.53195,-0.01803,0.17193],"tcp_to_object_dist_end":0.04868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.48831,-0.16505,0.0248],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01906,"object_to_goal_dist_start":0.13211,"object_z_max":0.02646,"peak_contact_force":4e-05,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":812.0,"raw_peak_contact_force":41.56807,"subtask_id":"push_to_goal","tcp_end":[0.50228,-0.13078,0.0202],"tcp_start":[0.55611,0.02161,0.02735],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21739,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_box.approach_speed":0.34415,"descend_to_contact.descend_speed":0.12044,"descend_to_contact.pre_push_offset":0.04541,"push_to_goal.push_speed":0.03002},"optimized_scores":{"best_composite_score":0.44762,"best_fitness_score":0.67762,"best_task_score":0.85869},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":53.0,"contact_point_centroid":[0.57127,-0.00953,0.04865],"force_p95":122.40756,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.78813,"mean_force":80.20085,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.56528,0.00032,0.04911]},{"body_a":"world","body_b":"push_box","contact_count":2879.0,"contact_point_centroid":[0.55546,-0.03534,-3e-05],"force_p95":0.48018,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.22665,"mean_force":1.73871,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.55179,-0.01102,0.0993]},{"body_a":"attachment","body_b":"push_box","contact_count":253.0,"contact_point_centroid":[0.53333,-0.07413,0.0231],"force_p95":27.28154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.33896,"mean_force":3.95207,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53506,-0.06249,0.02136]},{"body_a":"world","body_b":"push_box","contact_count":527.0,"contact_point_centroid":[0.52782,-0.09331,-9e-05],"force_p95":9.58067,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.68902,"mean_force":2.28935,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5391,-0.05439,0.02206]},{"body_a":"world","body_b":"push_box","contact_count":504.0,"contact_point_centroid":[0.55472,-0.03508,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_box","phase_type":"approach","tcp_position_centroid":[0.51926,-0.01161,0.23939]}],"total_contact_groups":5},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49534,-0.16737,0.02523],"final_tcp_position":[0.50409,-0.1314,0.02018],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":175.78813,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_box","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.5396,-0.02493,0.17086],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.55711,-0.03673,0.02498],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12685,"object_to_goal_dist_start":0.12728,"object_z_max":0.02548,"peak_contact_force":0.24518,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2932.0,"raw_peak_contact_force":175.78813,"subtask_id":"pre_push","tcp_end":[0.56861,0.00434,0.02725],"tcp_start":[0.5396,-0.02493,0.17086],"tcp_to_object_dist_end":0.04271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.49534,-0.16737,0.02523],"object_pos_start":[0.55711,-0.03673,0.02498],"object_to_goal_dist_end":0.01799,"object_to_goal_dist_start":0.12685,"object_z_max":0.02625,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":780.0,"raw_peak_contact_force":34.33896,"subtask_id":"push_to_goal","tcp_end":[0.50409,-0.1314,0.02018],"tcp_start":[0.56861,0.00434,0.02725],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10753,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_box.approach_speed":0.23618,"descend_to_contact.descend_speed":0.13209,"descend_to_contact.pre_push_offset":0.04534,"push_to_goal.push_speed":0.08666},"optimized_scores":{"best_composite_score":0.4369,"best_fitness_score":0.6669,"best_task_score":0.83069},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.45,0.02505,0.04905],"force_p95":181.92676,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.30817,"mean_force":82.64794,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.44501,0.0353,0.0493]},{"body_a":"world","body_b":"push_box","contact_count":2666.0,"contact_point_centroid":[0.45517,-0.00043,-1e-05],"force_p95":0.48975,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.37059,"mean_force":1.24545,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.45382,0.02019,0.09927]},{"body_a":"attachment","body_b":"push_box","contact_count":276.0,"contact_point_centroid":[0.47182,-0.06007,0.04373],"force_p95":35.12199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.11004,"mean_force":6.70477,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46571,-0.0484,0.02381]},{"body_a":"world","body_b":"push_box","contact_count":493.0,"contact_point_centroid":[0.4844,-0.08224,-7e-05],"force_p95":21.95457,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.74283,"mean_force":4.3632,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46114,-0.03261,0.02469]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52565,-0.12193,0.05385],"force_p95":0.53958,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.5502,"mean_force":0.44399,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48738,-0.11935,0.02112]},{"body_a":"world","body_b":"push_box","contact_count":464.0,"contact_point_centroid":[0.45543,-9e-05,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_box","phase_type":"approach","tcp_position_centroid":[0.48606,-3e-05,0.23982]}],"total_contact_groups":6},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52359,-0.162,0.02592],"final_tcp_position":[0.49157,-0.13271,0.02068],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":218.30817,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_box","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":464.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.46943,-7e-05,0.1723],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":750.0,"object_pos_end":[0.45558,-0.00069,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.15578,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24532,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2698.0,"raw_peak_contact_force":218.30817,"subtask_id":"pre_push","tcp_end":[0.44085,0.04077,0.02988],"tcp_start":[0.46943,-7e-05,0.1723],"tcp_to_object_dist_end":0.04428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":480.0,"n_steps_budget":1000.0,"object_pos_end":[0.52359,-0.162,0.02592],"object_pos_start":[0.45558,-0.00069,0.02499],"object_to_goal_dist_end":0.02648,"object_to_goal_dist_start":0.15578,"object_z_max":0.02713,"peak_contact_force":1.70604,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":771.0,"raw_peak_contact_force":48.11004,"subtask_id":"push_to_goal","tcp_end":[0.49157,-0.13271,0.02068],"tcp_start":[0.44085,0.04077,0.02988],"tcp_to_object_dist_end":0.04371,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```