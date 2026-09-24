## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 10  | 0.2514 | 0.87 | ✅ accepted |
| 6 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10  | -0.4666 | 0.00 | ❌ rejected |
| 5 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.5165 | 0.00 | ❌ rejected |
| 4 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12  | -0.5164 | 0.00 | ❌ rejected |
| 3 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 12  | 0.0504 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.869, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.050) — your mutation base

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
  control: position_control
  termination: pose_tolerance
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
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
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
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - side_offset_x: status=consumed; consumers=target.offset.x (add)
    - side_offset_y: status=consumed; consumers=target.offset.y (add)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.050
- **task_score** (E): 0.210
- **fitness_score**: 0.247  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_object | 1.00 | 1.00 | 0.1658 |
| approach_contact | 0.33 | 1.00 | 0.0995 |
| push_to_goal | 1.00 | 1.00 | 0.0556 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_object | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.023, 0.142) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_contact | approach | 0.33 / step_budget | (0.508, 0.023, 0.142)→(0.509, 0.061, 0.050) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.333 | 25298.009 | 0.245 |
| push_to_goal | push | 1.00 / force_exceeded | (0.509, 0.061, 0.050)→(0.498, 0.007, 0.042) | (0.513, 0.027, 0.025)→(0.518, -0.011, 0.029) | 0.180→0.145 | 1.00 / 4.333 | 23.323 | 25.837 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.000
- lateral_force_integral: None
- approach_alignment: 0.355
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.152
- phase_breakdown.approach_object_score: 0.507
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.357
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.348
- **Median Q (composite search score)**: 0.096
- **K-run variance**: 0.0279
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95732,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.03498,"approach_contact.contact_force_threshold":5.7725,"approach_contact.side_offset_x":-0.00143,"approach_contact.side_offset_y":0.02987,"descend_to_object.descend_speed":0.05517,"descend_to_object.descend_tolerance":0.01724,"push_to_goal.push_force_threshold":19.03361,"push_to_goal.push_speed":0.05453,"push_to_goal.retry_offset_x":-0.00116,"push_to_goal.retry_offset_y":-0.00832},"optimized_scores":{"best_composite_score":-0.1731,"best_fitness_score":0.3569,"best_task_score":0.34787},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":870.0,"contact_point_centroid":[0.51192,0.02906,0.04895],"force_p95":13.18834,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.93908,"mean_force":5.40552,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50248,0.03947,0.04]},{"body_a":"world","body_b":"push_box","contact_count":1628.0,"contact_point_centroid":[0.52874,-0.00243,-4e-05],"force_p95":8.24754,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.56224,"mean_force":3.5066,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50293,0.0442,0.04068]},{"body_a":"push_box","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.54288,-0.00098,0.06046],"force_p95":9.93954,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.24141,"mean_force":7.50876,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50036,-0.0014,0.03615]},{"body_a":"world","body_b":"push_box","contact_count":1548.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.5043,0.02022,0.22138]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50809,0.06816,0.0844]}],"total_contact_groups":5},"final_pose_error":0.17421,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53106,-0.0247,0.03195],"final_tcp_position":[0.50042,-0.00282,0.03615],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":17.93908,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1548.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51033,0.04191,0.14016],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.50865,0.0865,0.04893],"tcp_start":[0.51033,0.04191,0.14016],"tcp_to_object_dist_end":0.04606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53106,-0.0247,0.03195],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.12927,"object_to_goal_dist_start":0.19823,"object_z_max":0.03194,"peak_contact_force":15.56224,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2538.0,"raw_peak_contact_force":17.93908,"subtask_id":"push_to_goal","tcp_end":[0.50042,-0.00282,0.03615],"tcp_start":[0.50865,0.0865,0.04893],"tcp_to_object_dist_end":0.03788,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76712,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.02331,"approach_contact.contact_force_threshold":2.31652,"approach_contact.side_offset_x":0.01096,"approach_contact.side_offset_y":0.0002,"descend_to_object.descend_speed":0.06175,"descend_to_object.descend_tolerance":0.02005,"push_to_goal.push_force_threshold":15.15145,"push_to_goal.push_speed":0.07083,"push_to_goal.retry_offset_x":0.00431,"push_to_goal.retry_offset_y":0.0119},"optimized_scores":{"best_composite_score":0.22803,"best_fitness_score":0.09136,"best_task_score":2e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49368,0.07366,0.04991],"force_p95":40.49796,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.01447,"mean_force":30.54786,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48296,0.07329,0.0552]},{"body_a":"world","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.47422,0.05847,-1e-05],"force_p95":20.45514,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.39537,"mean_force":9.35107,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48296,0.07329,0.0552]},{"body_a":"world","body_b":"push_box","contact_count":1344.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48936,0.02436,0.22305]},{"body_a":"world","body_b":"push_box","contact_count":2788.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.47975,0.06214,0.09601]}],"total_contact_groups":4},"final_pose_error":0.24138,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47918,0.05846,0.02497],"final_tcp_position":[0.48291,0.07327,0.05506],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1344.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4792,0.05061,0.14311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2788.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.48299,0.07328,0.05528],"tcp_start":[0.4792,0.05061,0.14311],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47918,0.05846,0.02497],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":35.84936,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":41.01447,"subtask_id":"push_to_goal","tcp_end":[0.48291,0.07327,0.05506],"tcp_start":[0.48299,0.07328,0.05528],"tcp_to_object_dist_end":0.03375,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96154,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.03363,"approach_contact.contact_force_threshold":4.00443,"approach_contact.side_offset_x":-0.00404,"approach_contact.side_offset_y":0.03698,"descend_to_object.descend_speed":0.04532,"descend_to_object.descend_tolerance":0.01919,"push_to_goal.push_force_threshold":16.9031,"push_to_goal.push_speed":0.03199,"push_to_goal.retry_offset_x":-0.00609,"push_to_goal.retry_offset_y":0.01236},"optimized_scores":{"best_composite_score":0.09622,"best_fitness_score":0.29289,"best_task_score":0.28198},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.55345,-0.03442,0.06154],"force_p95":15.58849,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.55642,"mean_force":11.02225,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5119,-0.04367,0.03577]},{"body_a":"world","body_b":"push_box","contact_count":1977.0,"contact_point_centroid":[0.55153,-0.05408,-3e-05],"force_p95":9.89559,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.27112,"mean_force":2.98545,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52198,-0.00927,0.03854]},{"body_a":"attachment","body_b":"push_box","contact_count":809.0,"contact_point_centroid":[0.53005,-0.03,0.05221],"force_p95":8.89422,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.79513,"mean_force":4.44499,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51868,-0.01936,0.03732]},{"body_a":"world","body_b":"push_box","contact_count":1436.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51666,-0.01072,0.22257]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.53419,0.00479,0.08221]}],"total_contact_groups":5},"final_pose_error":0.19471,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54514,-0.06678,0.03097],"final_tcp_position":[0.5109,-0.0483,0.03582],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":18.55642,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53596,-0.02232,0.14172],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.53508,0.02289,0.04576],"tcp_start":[0.53596,-0.02232,0.14172],"tcp_to_object_dist_end":0.05356,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.54514,-0.06678,0.03097],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.09486,"object_to_goal_dist_start":0.13211,"object_z_max":0.03097,"peak_contact_force":18.55642,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2931.0,"raw_peak_contact_force":18.55642,"subtask_id":"push_to_goal","tcp_end":[0.5109,-0.0483,0.03582],"tcp_start":[0.53508,0.02289,0.04576],"tcp_to_object_dist_end":0.03922,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```