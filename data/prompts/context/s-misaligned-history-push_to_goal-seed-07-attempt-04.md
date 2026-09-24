## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12  | -0.5164 | 0.00 | ❌ rejected |
| 3 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12  | 0.3180 | 0.85 | ✅ accepted |
| 2 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8  | 0.0028 | 0.00 | ✅ accepted |
| 1 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8  | -0.3400 | 0.00 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5  | -0.5165 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.517) — your mutation base

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

- **Composite score**: -0.517
- **task_score** (E): 0.000
- **fitness_score**: 0.113  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_object | 1.00 | 1.00 | 0.1711 |
| approach_contact | 1.00 | 1.00 | 0.0892 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_object | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.024, 0.137) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_contact | approach | 1.00 / step_budget | (0.509, 0.024, 0.137)→(0.515, 0.026, 0.048) | (0.513, 0.027, 0.025)→(0.516, 0.027, 0.024) | 0.180→0.180 | 1.00 / 5.000 | 253.001 | 294.918 |
| push_to_goal | push | 0.00 / guard_failure | (0.515, 0.026, 0.048)→(0.515, 0.026, 0.048) | (0.516, 0.027, 0.024)→(0.516, 0.027, 0.024) | 0.180→0.180 | 1.00 / 5.000 | 135.344 | 135.344 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.015
- lateral_force_integral: None
- approach_alignment: 0.410
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.190
- phase_breakdown.approach_object_score: 0.634
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.114
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.516
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08397,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.02966,"approach_contact.approach_tolerance":0.02204,"approach_contact.side_offset_x":-0.00723,"approach_contact.side_offset_y":-0.03232,"descend_to_object.descend_speed":0.07639,"descend_to_object.descend_tolerance":0.01689,"push_to_goal.force_guard_threshold":25.75784,"push_to_goal.push_overshoot":0.17581,"push_to_goal.push_speed":0.0825,"push_to_goal.push_tolerance":0.0249,"push_to_goal.retry_offset_x":-0.0039,"push_to_goal.retry_offset_y":0.00342},"optimized_scores":{"best_composite_score":-0.51579,"best_fitness_score":0.11421,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.52122,0.04479,0.04659],"force_p95":302.05309,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":307.65139,"mean_force":268.48718,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.51017,0.04457,0.04916]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.52713,0.04541,0.04565],"force_p95":127.92298,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.41167,"mean_force":117.48101,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51598,0.04517,0.04764]},{"body_a":"world","body_b":"push_box","contact_count":896.0,"contact_point_centroid":[0.51522,0.0477,-0.00013],"force_p95":114.15832,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.6368,"mean_force":17.14142,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50799,0.04335,0.08677]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.51678,0.04793,-0.00069],"force_p95":48.80416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.0302,"mean_force":29.68196,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51598,0.04517,0.04764]},{"body_a":"world","body_b":"push_box","contact_count":1512.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.50436,0.02031,0.22107]}],"total_contact_groups":5},"final_pose_error":0.14498,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51755,0.04786,0.02365],"final_tcp_position":[0.51619,0.0452,0.04776],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":307.65139,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51038,0.04201,0.13979],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.5176,0.04786,0.0236],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19865,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":263.74018,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":307.65139,"subtask_id":"approach_object","tcp_end":[0.51586,0.04516,0.04759],"tcp_start":[0.51038,0.04201,0.13979],"tcp_to_object_dist_end":0.02421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51759,0.04786,0.02361],"object_pos_start":[0.5176,0.04786,0.0236],"object_to_goal_dist_end":0.19865,"object_to_goal_dist_start":0.19865,"object_z_max":0.02363,"peak_contact_force":129.41167,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":129.41167,"subtask_id":"push_to_goal","tcp_end":[0.51619,0.0452,0.04776],"tcp_start":[0.5161,0.04519,0.04769],"tcp_to_object_dist_end":0.02434,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92308,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.05891,"approach_contact.approach_tolerance":0.01786,"approach_contact.side_offset_x":-0.00943,"approach_contact.side_offset_y":-0.02835,"descend_to_object.descend_speed":0.04327,"descend_to_object.descend_tolerance":0.01246,"push_to_goal.force_guard_threshold":23.09988,"push_to_goal.push_overshoot":0.1991,"push_to_goal.push_speed":0.04619,"push_to_goal.push_tolerance":0.00515,"push_to_goal.retry_offset_x":0.00043,"push_to_goal.retry_offset_y":-0.00134},"optimized_scores":{"best_composite_score":-0.5179,"best_fitness_score":0.1121,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":104.0,"contact_point_centroid":[0.48688,0.05942,0.0462],"force_p95":298.68815,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":304.60552,"mean_force":269.18652,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.47621,0.05912,0.04937]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49402,0.06077,0.04555],"force_p95":149.58306,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.45863,"mean_force":135.17563,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48323,0.06053,0.0483]},{"body_a":"world","body_b":"push_box","contact_count":1148.0,"contact_point_centroid":[0.47967,0.05857,-0.00022],"force_p95":113.99171,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.76167,"mean_force":24.72168,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.47416,0.05653,0.07956]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.48153,0.05899,-0.0007],"force_p95":62.59604,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.2035,"mean_force":34.09286,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48323,0.06053,0.0483]},{"body_a":"world","body_b":"push_box","contact_count":2052.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48845,0.02573,0.21864]}],"total_contact_groups":5},"final_pose_error":0.17217,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48232,0.05911,0.02362],"final_tcp_position":[0.48336,0.06056,0.04841],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":304.60552,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47798,0.05295,0.13597],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.48233,0.05911,0.02358],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20986,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":262.24675,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":304.60552,"subtask_id":"approach_object","tcp_end":[0.48317,0.06052,0.04826],"tcp_start":[0.47798,0.05295,0.13597],"tcp_to_object_dist_end":0.02473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48233,0.05911,0.02359],"object_pos_start":[0.48233,0.05911,0.02358],"object_to_goal_dist_end":0.20986,"object_to_goal_dist_start":0.20986,"object_z_max":0.02361,"peak_contact_force":150.45863,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":150.45863,"subtask_id":"push_to_goal","tcp_end":[0.48336,0.06056,0.04841],"tcp_start":[0.4833,0.06054,0.04834],"tcp_to_object_dist_end":0.02488,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91736,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.04167,"approach_contact.approach_tolerance":0.01685,"approach_contact.side_offset_x":-0.01216,"approach_contact.side_offset_y":-0.03113,"descend_to_object.descend_speed":0.05887,"descend_to_object.descend_tolerance":0.01177,"push_to_goal.force_guard_threshold":29.1821,"push_to_goal.push_overshoot":0.19393,"push_to_goal.push_speed":0.06709,"push_to_goal.push_tolerance":0.02148,"push_to_goal.retry_offset_x":0.00276,"push_to_goal.retry_offset_y":0.00225},"optimized_scores":{"best_composite_score":-0.51582,"best_fitness_score":0.11418,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":137.0,"contact_point_centroid":[0.55064,-0.02635,0.04653],"force_p95":263.91637,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":272.49599,"mean_force":240.7245,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.53932,-0.02648,0.04836]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.55788,-0.02689,0.04616],"force_p95":125.3156,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.1631,"mean_force":116.79935,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54647,-0.02711,0.04766]},{"body_a":"world","body_b":"push_box","contact_count":1284.0,"contact_point_centroid":[0.54511,-0.02565,-0.00024],"force_p95":94.18856,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.34742,"mean_force":25.98691,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.53584,-0.02531,0.07526]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.54719,-0.02585,-0.00062],"force_p95":49.21023,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.09512,"mean_force":29.47772,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54647,-0.02711,0.04766]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51743,-0.01142,0.21748]}],"total_contact_groups":5},"final_pose_error":0.16616,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54776,-0.0259,0.02378],"final_tcp_position":[0.54659,-0.02712,0.04776],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":272.49599,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53744,-0.02339,0.13416],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.54777,-0.0259,0.02374],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13298,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":233.01508,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1421.0,"raw_peak_contact_force":272.49599,"subtask_id":"approach_object","tcp_end":[0.54641,-0.0271,0.04762],"tcp_start":[0.53744,-0.02339,0.13416],"tcp_to_object_dist_end":0.02395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54777,-0.0259,0.02375],"object_pos_start":[0.54777,-0.0259,0.02374],"object_to_goal_dist_end":0.13298,"object_to_goal_dist_start":0.13298,"object_z_max":0.02376,"peak_contact_force":126.1631,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":126.1631,"subtask_id":"push_to_goal","tcp_end":[0.54659,-0.02712,0.04776],"tcp_start":[0.54653,-0.02711,0.0477],"tcp_to_object_dist_end":0.02407,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```