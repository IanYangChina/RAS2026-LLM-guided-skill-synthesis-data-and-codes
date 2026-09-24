## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3882 | 0.29 | ❌ rejected |
| 4 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2267 | 0.55 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | -0.2092 | 0.00 | ✅ accepted |
| 2 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.388) — your mutation base

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

- **Composite score**: 0.388
- **task_score** (E): 0.290
- **fitness_score**: 0.285  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_approach | 1.00 | 1.00 | 0.2828 |
| push_task | 1.00 | 1.00 | 0.0565 |
| retract_1 | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.075, 0.033) | (0.513, 0.027, 0.025)→(0.513, 0.026, 0.025) | 0.180→0.179 | 1.00 / 4.333 | 10.856 | 13.840 |
| push_task | push | 1.00 / force_exceeded | (0.514, 0.075, 0.033)→(0.498, 0.021, 0.028) | (0.513, 0.026, 0.025)→(0.507, -0.015, 0.026) | 0.179→0.139 | 1.00 / 3.667 | 20.568 | 19.576 |
| retract_1 | retract | 1.00 / step_budget | (0.498, 0.021, 0.028)→(0.494, 0.021, 0.068) | (0.507, -0.015, 0.026)→(0.506, -0.015, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 12.489 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.782
- lateral_force_integral: None
- approach_alignment: 0.663
- goal_progress: 0.748
- terminal_score: 0.748
- phase_score: 0.597
- phase_breakdown.reach_pre_contact_score: 0.264
- phase_breakdown.push_to_goal_score: 0.740

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.657
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.748
- **Median Q (composite search score)**: 0.228
- **K-run variance**: 0.0698
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.447


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69892,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.06028,"arc_approach.arc_height":0.0337,"push_task.force_limit":17.88773,"push_task.push_distance":0.05349},"optimized_scores":{"best_composite_score":0.22797,"best_fitness_score":0.12464,"best_task_score":0.10035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.51401,0.06274,0.03941],"force_p95":14.47467,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.62124,"mean_force":3.83685,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.50841,0.07453,0.02757]},{"body_a":"world","body_b":"push_box","contact_count":771.0,"contact_point_centroid":[0.51564,0.04231,-2e-05],"force_p95":4.06404,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.50152,"mean_force":0.80204,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.5102,0.09091,0.02895]},{"body_a":"attachment","body_b":"push_box","contact_count":194.0,"contact_point_centroid":[0.5102,0.05145,0.05031],"force_p95":1.01548,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.82186,"mean_force":0.58338,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50423,0.06328,0.03943]},{"body_a":"world","body_b":"push_box","contact_count":1293.0,"contact_point_centroid":[0.51776,0.01739,-2e-05],"force_p95":0.45548,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.10826,"mean_force":0.33259,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50395,0.06328,0.05126]},{"body_a":"world","body_b":"push_box","contact_count":3940.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.50562,0.07061,0.17644]}],"total_contact_groups":5},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51694,0.02754,0.02499],"final_tcp_position":[0.50381,0.06328,0.06809],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":18.62124,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":985.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3940.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.5145,0.10738,0.03349],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.51778,0.0273,0.02496],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.17819,"object_to_goal_dist_start":0.19823,"object_z_max":0.02533,"peak_contact_force":18.62124,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":876.0,"raw_peak_contact_force":18.62124,"subtask_id":"push_to_goal","tcp_end":[0.50772,0.0638,0.02726],"tcp_start":[0.5145,0.10738,0.03349],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.51694,0.02754,0.02499],"object_pos_start":[0.51778,0.0273,0.02496],"object_to_goal_dist_end":0.17834,"object_to_goal_dist_start":0.17819,"object_z_max":0.02535,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1487.0,"raw_peak_contact_force":9.82186,"tcp_end":[0.50381,0.06328,0.06809],"tcp_start":[0.50772,0.0638,0.02726],"tcp_to_object_dist_end":0.05752,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66265,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.03022,"arc_approach.arc_height":0.05539,"push_task.force_limit":7.8456,"push_task.push_distance":0.13792},"optimized_scores":{"best_composite_score":0.17595,"best_fitness_score":0.07261,"best_task_score":0.02047},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.4741,0.08219,0.03709],"force_p95":40.9417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.02801,"mean_force":28.44474,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.47389,0.09407,0.03689]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.47924,0.05846,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.26199,"mean_force":0.39403,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.48734,0.07504,0.18141]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.47381,0.08125,0.03323],"force_p95":11.79774,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.02423,"mean_force":4.67828,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.47355,0.09319,0.03306]},{"body_a":"world","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.47816,0.06958,-4e-05],"force_p95":4.3839,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.51961,"mean_force":1.29869,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.47316,0.09257,0.03256]},{"body_a":"world","body_b":"push_box","contact_count":1620.0,"contact_point_centroid":[0.47802,0.05404,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8372,"mean_force":0.24725,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46933,0.09109,0.05223]}],"total_contact_groups":5},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47802,0.05404,0.02499],"final_tcp_position":[0.46906,0.09111,0.07281],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":41.02801,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47917,0.05655,0.02494],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2076,"object_to_goal_dist_start":0.2095,"object_z_max":0.02508,"peak_contact_force":32.07779,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4007.0,"raw_peak_contact_force":41.02801,"subtask_id":"reach_pre_contact","tcp_end":[0.47366,0.09324,0.03322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.47814,0.05442,0.02481],"object_pos_start":[0.47917,0.05655,0.02494],"object_to_goal_dist_end":0.20558,"object_to_goal_dist_start":0.2076,"object_z_max":0.02533,"peak_contact_force":16.0,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":17.0,"raw_peak_contact_force":13.02423,"subtask_id":"push_to_goal","tcp_end":[0.47276,0.0918,0.03202],"tcp_start":[0.47366,0.09324,0.03322],"tcp_to_object_dist_end":0.03845,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.47802,0.05404,0.02499],"object_pos_start":[0.47814,0.05442,0.02481],"object_to_goal_dist_end":0.20522,"object_to_goal_dist_start":0.20558,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.8372,"tcp_end":[0.46906,0.09111,0.07281],"tcp_start":[0.47276,0.0918,0.03202],"tcp_to_object_dist_end":0.06117,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73585,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.04977,"arc_approach.arc_height":0.02276,"push_task.force_limit":21.45076,"push_task.push_distance":0.03751},"optimized_scores":{"best_composite_score":0.76072,"best_fitness_score":0.65739,"best_task_score":0.74792},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.54982,-0.10391,0.05201],"force_p95":19.40531,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.08231,"mean_force":13.59189,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.51476,-0.08633,0.02308]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54795,-0.11456,0.05239],"force_p95":26.40394,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.80923,"mean_force":9.86414,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.513,-0.09216,0.02334]},{"body_a":"world","body_b":"push_box","contact_count":1417.0,"contact_point_centroid":[0.52591,-0.13379,-1e-05],"force_p95":0.45801,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.29572,"mean_force":0.36515,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5094,-0.09153,0.0471]},{"body_a":"world","body_b":"push_box","contact_count":1314.0,"contact_point_centroid":[0.53686,-0.07211,-4e-05],"force_p95":9.91051,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.98354,"mean_force":2.65953,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.5353,-0.02305,0.02516]},{"body_a":"attachment","body_b":"push_box","contact_count":567.0,"contact_point_centroid":[0.53516,-0.05105,0.03627],"force_p95":15.83578,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.58308,"mean_force":4.3407,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.52965,-0.03921,0.02414]},{"body_a":"attachment","body_b":"push_box","contact_count":153.0,"contact_point_centroid":[0.52205,-0.10302,0.05153],"force_p95":1.11107,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.34367,"mean_force":0.75928,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50998,-0.09164,0.0328]},{"body_a":"world","body_b":"push_box","contact_count":3700.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.52565,0.02513,0.16665]}],"total_contact_groups":7},"final_pose_error":0.01006,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52386,-0.12676,0.02499],"final_tcp_position":[0.50929,-0.09151,0.06402],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":27.08231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3700.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.55411,0.02372,0.03138],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.52609,-0.12766,0.02691],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.0344,"object_to_goal_dist_start":0.13211,"object_z_max":0.02689,"peak_contact_force":27.08231,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1928.0,"raw_peak_contact_force":27.08231,"subtask_id":"push_to_goal","tcp_end":[0.51327,-0.09202,0.02325],"tcp_start":[0.55411,0.02372,0.03138],"tcp_to_object_dist_end":0.03806,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.52386,-0.12676,0.02499],"object_pos_start":[0.52609,-0.12766,0.02691],"object_to_goal_dist_end":0.0333,"object_to_goal_dist_start":0.0344,"object_z_max":0.02699,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1580.0,"raw_peak_contact_force":26.80923,"tcp_end":[0.50929,-0.09151,0.06402],"tcp_start":[0.51327,-0.09202,0.02325],"tcp_to_object_dist_end":0.05458,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```