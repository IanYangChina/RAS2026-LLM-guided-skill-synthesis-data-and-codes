## Search State

- **Seed**: 9
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.861, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.524) — your mutation base

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

- **Composite score**: 0.524
- **task_score** (E): 0.844
- **fitness_score**: 0.704  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1790 |
| descend_behind | 1.00 | 1.00 | 0.1214 |
| push_to_goal | 1.00 | 1.00 | 0.2173 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.527, 0.061, 0.148) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_behind | descend | 1.00 / step_budget | (0.527, 0.061, 0.148)→(0.530, 0.072, 0.028) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.530, 0.072, 0.028)→(0.499, -0.132, 0.020) | (0.518, -0.020, 0.025)→(0.509, -0.163, 0.026) | 0.139→0.022 | 1.00 / 1.333 | 0.961 | 41.625 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.698
- goal_progress: 0.869
- terminal_score: 0.869
- phase_score: 0.627
- phase_breakdown.approach_behind_score: 0.064
- phase_breakdown.push_to_goal_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.724
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.869
- **Median Q (composite search score)**: 0.539
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.235


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76106,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.37954,"descend_behind.descend_speed":0.14263,"push_to_goal.push_speed":0.06368},"optimized_scores":{"best_composite_score":0.54371,"best_fitness_score":0.72371,"best_task_score":0.86856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":288.0,"contact_point_centroid":[0.52592,-0.06973,0.02353],"force_p95":28.88773,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.35612,"mean_force":4.88167,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52674,-0.05796,0.02075]},{"body_a":"world","body_b":"push_box","contact_count":1005.0,"contact_point_centroid":[0.53267,-0.05768,-5e-05],"force_p95":12.41188,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.14408,"mean_force":1.71781,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5455,-0.00356,0.022]},{"body_a":"world","body_b":"push_box","contact_count":948.0,"contact_point_centroid":[0.54443,-0.02558,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53077,0.02757,0.22556]},{"body_a":"world","body_b":"push_box","contact_count":2156.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.56666,0.06196,0.08599]}],"total_contact_groups":4},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49613,-0.16692,0.02546],"final_tcp_position":[0.50245,-0.13078,0.02028],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":41.35612,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":948.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.56372,0.05707,0.14839],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_behind","tcp_end":[0.57252,0.06718,0.02738],"tcp_start":[0.56372,0.05707,0.14839],"tcp_to_object_dist_end":0.09695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.49613,-0.16692,0.02546],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01737,"object_to_goal_dist_start":0.13211,"object_z_max":0.02643,"peak_contact_force":0.3058,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1293.0,"raw_peak_contact_force":41.35612,"subtask_id":"push_to_goal","tcp_end":[0.50245,-0.13078,0.02028],"tcp_start":[0.57252,0.06718,0.02738],"tcp_to_object_dist_end":0.03705,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78378,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.33572,"descend_behind.descend_speed":0.1196,"push_to_goal.push_speed":0.06664},"optimized_scores":{"best_composite_score":0.53942,"best_fitness_score":0.71942,"best_task_score":0.86352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":264.0,"contact_point_centroid":[0.53232,-0.07842,0.02249],"force_p95":26.70848,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.59543,"mean_force":3.91477,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53344,-0.06669,0.02002]},{"body_a":"world","body_b":"push_box","contact_count":971.0,"contact_point_centroid":[0.54109,-0.06302,-4e-05],"force_p95":9.38892,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.97769,"mean_force":1.38326,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55941,-0.01048,0.02098]},{"body_a":"world","body_b":"push_box","contact_count":976.0,"contact_point_centroid":[0.55472,-0.03508,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53909,0.02229,0.22536]},{"body_a":"world","body_b":"push_box","contact_count":2360.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.58498,0.05002,0.08423]}],"total_contact_groups":4},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4987,-0.16732,0.02545],"final_tcp_position":[0.50431,-0.13119,0.02001],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":34.59543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.58087,0.04612,0.14796],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":590.0,"n_steps_budget":660.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_behind","tcp_end":[0.59198,0.05411,0.02613],"tcp_start":[0.58087,0.04612,0.14796],"tcp_to_object_dist_end":0.09667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.4987,-0.16732,0.02545],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.01737,"object_to_goal_dist_start":0.12728,"object_z_max":0.02648,"peak_contact_force":0.47526,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1235.0,"raw_peak_contact_force":34.59543,"subtask_id":"push_to_goal","tcp_end":[0.50431,-0.13119,0.02001],"tcp_start":[0.59198,0.05411,0.02613],"tcp_to_object_dist_end":0.03696,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29825,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.11288,"descend_behind.descend_speed":0.14968,"push_to_goal.push_speed":0.04614},"optimized_scores":{"best_composite_score":0.48766,"best_fitness_score":0.66766,"best_task_score":0.80009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":297.0,"contact_point_centroid":[0.47128,-0.05377,0.0445],"force_p95":31.17411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.92199,"mean_force":6.50059,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46348,-0.04249,0.02324]},{"body_a":"world","body_b":"push_box","contact_count":1100.0,"contact_point_centroid":[0.47378,-0.04167,-4e-05],"force_p95":13.92713,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.3748,"mean_force":2.20237,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44544,0.01698,0.0253]},{"body_a":"world","body_b":"push_box","contact_count":1028.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46931,0.03871,0.22589]},{"body_a":"world","body_b":"push_box","contact_count":2176.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.42944,0.08692,0.08888]}],"total_contact_groups":4},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53074,-0.15564,0.02567],"final_tcp_position":[0.49155,-0.13271,0.02064],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":48.92199,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.43682,0.08041,0.14854],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_behind","tcp_end":[0.42421,0.09397,0.03015],"tcp_start":[0.43682,0.08041,0.14854],"tcp_to_object_dist_end":0.09924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.53074,-0.15564,0.02567],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.03127,"object_to_goal_dist_start":0.1564,"object_z_max":0.0273,"peak_contact_force":2.10224,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1397.0,"raw_peak_contact_force":48.92199,"subtask_id":"push_to_goal","tcp_end":[0.49155,-0.13271,0.02064],"tcp_start":[0.42421,0.09397,0.03015],"tcp_to_object_dist_end":0.04569,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```