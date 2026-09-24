## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2171 | 0.54 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | -0.2185 | 0.00 | ❌ rejected |
| 5 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3882 | 0.29 | ❌ rejected |
| 4 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2267 | 0.55 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | -0.2092 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.51501145599256, 0.047665656116349056, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.51501145599256, 0.047665656116349056, 0.025]
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.217) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
phases:
- id: arc_approach
  type: approach
  generator: arc_cartesian
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
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_pre_contact
- id: push_task
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    force_limit:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
  subtask_id: push_to_goal
- id: retract_1
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **arc_approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **push_task** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.217
- **task_score** (E): 0.540
- **fitness_score**: 0.497  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_approach | 1.00 | 1.00 | 0.2861 |
| push_task | 0.00 | 1.00 | 0.1218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.087, 0.033) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_task | push | 0.00 / guard_failure | (0.517, 0.087, 0.033)→(0.499, -0.031, 0.026) | (0.513, 0.027, 0.025)→(0.513, -0.067, 0.026) | 0.180→0.088 | 1.00 / 3.000 | 17.757 | 29.837 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.798
- lateral_force_integral: None
- approach_alignment: 0.645
- goal_progress: 0.748
- terminal_score: 0.748
- phase_score: 0.616
- phase_breakdown.reach_pre_contact_score: 0.177
- phase_breakdown.push_to_goal_score: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.748
- **Median Q (composite search score)**: 0.173
- **K-run variance**: 0.0158
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.443


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93258,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.07394,"arc_approach.arc_height":0.02694,"push_task.force_limit":24.94201,"push_task.push_distance":0.12772,"push_task.push_time":3.01696},"optimized_scores":{"best_composite_score":0.0903,"best_fitness_score":0.3703,"best_task_score":0.39916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":396.0,"contact_point_centroid":[0.51621,0.03531,0.04382],"force_p95":19.20131,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.06393,"mean_force":5.11576,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.5068,0.04689,0.02677]},{"body_a":"world","body_b":"push_box","contact_count":1482.0,"contact_point_centroid":[0.51826,0.02263,-3e-05],"force_p95":8.89108,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.35873,"mean_force":1.76494,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.50922,0.07819,0.02784]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54365,0.00714,0.05295],"force_p95":13.37868,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.46217,"mean_force":9.77082,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.50519,0.02114,0.02635]},{"body_a":"world","body_b":"push_box","contact_count":3992.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.50619,0.07279,0.17466]}],"total_contact_groups":4},"final_pose_error":0.27972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52232,-0.03301,0.02583],"final_tcp_position":[0.50397,0.00203,0.02597],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":25.06393,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3992.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.51553,0.1192,0.03322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.52232,-0.03301,0.02583],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.11911,"object_to_goal_dist_start":0.19823,"object_z_max":0.0277,"peak_contact_force":25.06393,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1886.0,"raw_peak_contact_force":25.06393,"subtask_id":"push_to_goal","tcp_end":[0.50397,0.00203,0.02597],"tcp_start":[0.51553,0.1192,0.03322],"tcp_to_object_dist_end":0.03955,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92771,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.0351,"arc_approach.arc_height":0.04564,"push_task.force_limit":24.70196,"push_task.push_distance":0.12406,"push_task.push_time":3.41428},"optimized_scores":{"best_composite_score":0.17256,"best_fitness_score":0.45256,"best_task_score":0.4725},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":476.0,"contact_point_centroid":[0.48382,0.03893,0.0434],"force_p95":20.36572,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.87439,"mean_force":6.27921,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.47424,0.05046,0.02898]},{"body_a":"world","body_b":"push_box","contact_count":780.0,"contact_point_centroid":[0.4904,-0.00247,-8e-05],"force_p95":11.78801,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.77435,"mean_force":4.71246,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.47416,0.05256,0.0292]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.5156,0.00098,0.05321],"force_p95":14.91274,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.45928,"mean_force":6.94398,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.47782,0.01469,0.02779]},{"body_a":"world","body_b":"push_box","contact_count":3876.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.48694,0.07133,0.17932]}],"total_contact_groups":4},"final_pose_error":0.27457,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48957,-0.03998,0.02527],"final_tcp_position":[0.47945,-0.00086,0.02737],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":37.87439,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3876.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.47304,0.09572,0.03411],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.48957,-0.03998,0.02527],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.11051,"object_to_goal_dist_start":0.2095,"object_z_max":0.02849,"peak_contact_force":1.63287,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1310.0,"raw_peak_contact_force":37.87439,"subtask_id":"push_to_goal","tcp_end":[0.47945,-0.00086,0.02737],"tcp_start":[0.47304,0.09572,0.03411],"tcp_to_object_dist_end":0.04046,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93478,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.0763,"arc_approach.arc_height":0.02018,"push_task.force_limit":24.99547,"push_task.push_distance":0.10761,"push_task.push_time":3.78415},"optimized_scores":{"best_composite_score":0.38855,"best_fitness_score":0.66855,"best_task_score":0.74756},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.54944,-0.10501,0.05213],"force_p95":24.91559,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.57327,"mean_force":15.17302,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.51345,-0.08876,0.02362]},{"body_a":"attachment","body_b":"push_box","contact_count":584.0,"contact_point_centroid":[0.53438,-0.05299,0.03565],"force_p95":16.69966,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.45124,"mean_force":4.70357,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.52897,-0.04115,0.02413]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.5391,-0.05945,-3e-05],"force_p95":9.35417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.42446,"mean_force":2.13099,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.54107,-0.0058,0.02515]},{"body_a":"world","body_b":"push_box","contact_count":3816.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.52955,0.03502,0.16762]}],"total_contact_groups":4},"final_pose_error":0.164,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52611,-0.12936,0.02709],"final_tcp_position":[0.51209,-0.09462,0.02414],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":26.57327,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3816.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.56256,0.047,0.03137],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.52611,-0.12936,0.02709],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03335,"object_to_goal_dist_start":0.13211,"object_z_max":0.02706,"peak_contact_force":26.57327,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2562.0,"raw_peak_contact_force":26.57327,"subtask_id":"push_to_goal","tcp_end":[0.51209,-0.09462,0.02414],"tcp_start":[0.56256,0.047,0.03137],"tcp_to_object_dist_end":0.03758,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```