## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8  | 0.0028 | 0.00 | ✅ accepted |
| 1 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8  | -0.3400 | 0.00 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5  | 0.3180 | 0.85 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.845, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.318) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: descend_to_object
  type: descend
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
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: approach_contact
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    side_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    side_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: approach_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    retry_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.y
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **approach_contact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - side_offset_x: status=consumed; consumers=target.offset.x (add)
    - side_offset_y: status=consumed; consumers=target.offset.y (add)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.318
- **task_score** (E): 0.845
- **fitness_score**: 0.748  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_object | 1.00 | 1.00 | 0.1689 |
| approach_contact | 0.00 | 1.00 | 0.1306 |
| push_to_goal | 0.00 | 1.00 | 0.1826 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_object | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.024, 0.139) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_contact | approach | 0.00 / step_budget | (0.509, 0.024, 0.139)→(0.515, 0.087, 0.025) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.00 / step_budget | (0.515, 0.087, 0.025)→(0.495, -0.093, 0.022) | (0.513, 0.027, 0.025)→(0.503, -0.129, 0.027) | 0.180→0.029 | 1.00 / 3.667 | 28.478 | 49.005 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.698
- goal_progress: 0.893
- terminal_score: 0.893
- phase_score: 0.700
- phase_breakdown.approach_object_score: 0.248
- phase_breakdown.push_to_goal_score: 0.893

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.777
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.893
- **Median Q (composite search score)**: 0.336
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.341


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
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39869,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.09573,"approach_contact.contact_force_threshold":2.85001,"approach_contact.side_offset_x":0.01017,"approach_contact.side_offset_y":0.02831,"descend_to_object.descend_speed":0.0441,"descend_to_object.descend_tolerance":0.00953,"push_to_goal.retry_offset_x":-0.0085,"push_to_goal.retry_offset_y":0.00961},"optimized_scores":{"best_composite_score":0.33596,"best_fitness_score":0.76596,"best_task_score":0.86052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":763.0,"contact_point_centroid":[0.51576,-0.01359,0.03845],"force_p95":20.34044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.76542,"mean_force":5.27453,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50688,-0.0018,0.02006]},{"body_a":"world","body_b":"push_box","contact_count":1535.0,"contact_point_centroid":[0.51188,-0.03302,-5e-05],"force_p95":11.71419,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.25407,"mean_force":3.22978,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50893,0.01736,0.02049]},{"body_a":"push_box","body_b":"link7","contact_count":137.0,"contact_point_centroid":[0.53493,-0.03983,0.05066],"force_p95":11.33465,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.5045,"mean_force":3.26187,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50509,-0.02206,0.02011]},{"body_a":"world","body_b":"push_box","contact_count":2548.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50429,0.02147,0.21644]},{"body_a":"world","body_b":"push_box","contact_count":3092.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.51388,0.0728,0.07661]}],"total_contact_groups":5},"final_pose_error":0.08583,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50464,-0.12274,0.02521],"final_tcp_position":[0.49944,-0.08599,0.02006],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":28.76542,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2548.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51064,0.04394,0.13248],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":773.0,"n_steps_budget":840.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3092.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.52008,0.10208,0.02486],"tcp_start":[0.51064,0.04394,0.13248],"tcp_to_object_dist_end":0.05465,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50464,-0.12274,0.02521],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.02765,"object_to_goal_dist_start":0.19823,"object_z_max":0.02626,"peak_contact_force":1.73724,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2435.0,"raw_peak_contact_force":28.76542,"subtask_id":"push_to_goal","tcp_end":[0.49944,-0.08599,0.02006],"tcp_start":[0.52008,0.10208,0.02486],"tcp_to_object_dist_end":0.03747,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91406,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.08072,"approach_contact.contact_force_threshold":8.1449,"approach_contact.side_offset_x":0.00513,"approach_contact.side_offset_y":0.02924,"descend_to_object.descend_speed":0.0742,"descend_to_object.descend_tolerance":0.02283,"push_to_goal.retry_offset_x":-0.00243,"push_to_goal.retry_offset_y":-0.00148},"optimized_scores":{"best_composite_score":0.27097,"best_fitness_score":0.70097,"best_task_score":0.78284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":822.0,"contact_point_centroid":[0.49069,0.00144,0.03117],"force_p95":17.74787,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.18865,"mean_force":4.46095,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48483,0.01324,0.02034]},{"body_a":"world","body_b":"push_box","contact_count":1791.0,"contact_point_centroid":[0.48642,-0.01584,-4e-05],"force_p95":8.31921,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.24208,"mean_force":2.4004,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48386,0.02811,0.02071]},{"body_a":"push_box","body_b":"link7","contact_count":110.0,"contact_point_centroid":[0.51636,-0.02096,0.05028],"force_p95":10.2848,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.86281,"mean_force":2.40284,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48659,-0.00681,0.02033]},{"body_a":"world","body_b":"push_box","contact_count":1172.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48974,0.02387,0.22467]},{"body_a":"world","body_b":"push_box","contact_count":3888.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.47844,0.08273,0.0816]}],"total_contact_groups":5},"final_pose_error":0.09363,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49683,-0.10461,0.02492],"final_tcp_position":[0.49188,-0.06758,0.02018],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":31.18865,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47971,0.04973,0.14582],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3888.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.48,0.1142,0.0248],"tcp_start":[0.47971,0.04973,0.14582],"tcp_to_object_dist_end":0.05573,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49683,-0.10461,0.02492],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.0455,"object_to_goal_dist_start":0.2095,"object_z_max":0.02547,"peak_contact_force":0.82267,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2723.0,"raw_peak_contact_force":31.18865,"subtask_id":"push_to_goal","tcp_end":[0.49188,-0.06758,0.02018],"tcp_start":[0.48,0.1142,0.0248],"tcp_to_object_dist_end":0.03766,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92105,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.08761,"approach_contact.contact_force_threshold":1.8781,"approach_contact.side_offset_x":0.00499,"approach_contact.side_offset_y":0.04309,"descend_to_object.descend_speed":0.09079,"descend_to_object.descend_tolerance":0.01513,"push_to_goal.retry_offset_x":-0.00604,"push_to_goal.retry_offset_y":-0.00062},"optimized_scores":{"best_composite_score":0.34699,"best_fitness_score":0.77699,"best_task_score":0.89306},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.53965,-0.07722,0.05338],"force_p95":78.6158,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.06029,"mean_force":38.8119,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51032,-0.0601,0.02187]},{"body_a":"attachment","body_b":"push_box","contact_count":705.0,"contact_point_centroid":[0.52133,-0.08125,0.04561],"force_p95":73.79997,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.89782,"mean_force":30.5275,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50713,-0.07041,0.02189]},{"body_a":"world","body_b":"push_box","contact_count":2114.0,"contact_point_centroid":[0.53008,-0.08707,-0.00012],"force_p95":51.45069,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.77485,"mean_force":18.4153,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51755,-0.03556,0.02142]},{"body_a":"world","body_b":"push_box","contact_count":1672.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51717,-0.01112,0.2197]},{"body_a":"world","body_b":"push_box","contact_count":3536.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.53906,0.0108,0.07802]}],"total_contact_groups":5},"final_pose_error":0.11137,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50754,-0.16084,0.03002],"final_tcp_position":[0.49404,-0.12486,0.02547],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":87.06029,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53679,-0.02291,0.13757],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":884.0,"n_steps_budget":960.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3536.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.54434,0.04408,0.02407],"tcp_start":[0.53679,-0.02291,0.13757],"tcp_to_object_dist_end":0.06967,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50754,-0.16084,0.03002],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01413,"object_to_goal_dist_start":0.13211,"object_z_max":0.03001,"peak_contact_force":82.87555,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3562.0,"raw_peak_contact_force":87.06029,"subtask_id":"push_to_goal","tcp_end":[0.49404,-0.12486,0.02547],"tcp_start":[0.54434,0.04408,0.02407],"tcp_to_object_dist_end":0.03869,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```