## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3615 | 0.79 | ✅ accepted |
| 5 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.0456 | 0.39 | ❌ rejected |
| 4 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2807 | 0.72 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6105 | 0.67 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5949 | 0.68 | ✅ accepted |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.785, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.361) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: contact_object
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: reach_object
- id: push_stage1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push1_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push1_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_goal
- id: push_stage2
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push2_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push2_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_goal
- id: retract_after_push
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
    - 0.1
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_object** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=reduce_speed
- **push_stage1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push1_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push1_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_stage2** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push2_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push2_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.361
- **task_score** (E): 0.785
- **fitness_score**: 0.601  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.2733 |
| contact_object | 1.00 | 1.00 | 0.0520 |
| push_stage1 | 1.00 | 1.00 | 0.1231 |
| push_stage2 | 1.00 | 1.00 | 0.0889 |
| retract_after_push | 1.00 | 1.00 | 0.0891 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.109, 0.057) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 1.00 / force_exceeded | (0.517, 0.109, 0.057)→(0.511, 0.064, 0.035) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 36.101 | 0.245 |
| push_stage1 | push | 1.00 / step_budget | (0.511, 0.064, 0.035)→(0.496, -0.057, 0.031) | (0.513, 0.027, 0.025)→(0.521, -0.084, 0.028) | 0.180→0.072 | 1.00 / 3.000 | 13.317 | 38.330 |
| push_stage2 | push | 1.00 / step_budget | (0.496, -0.057, 0.031)→(0.462, -0.134, 0.024) | (0.521, -0.084, 0.028)→(0.505, -0.110, 0.026) | 0.072→0.043 | 1.00 / 3.667 | 28.667 | 43.739 |
| retract_after_push | retract | 1.00 / step_budget | (0.462, -0.134, 0.024)→(0.458, -0.133, 0.113) | (0.505, -0.110, 0.026)→(0.504, -0.111, 0.025) | 0.043→0.043 | 1.00 / 4.000 | 0.245 | 33.916 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.795
- goal_progress: 0.947
- terminal_score: 0.947
- phase_score: 0.719
- phase_breakdown.push_goal_score: 0.824
- phase_breakdown.reach_object_score: 0.473

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.810
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.947
- **Median Q (composite search score)**: 0.271
- **K-run variance**: 0.0218
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.264


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37433,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.11612,"approach_object.approach_speed":0.04448,"contact_object.contact_force_threshold":5.8655,"push_stage1.push1_distance":0.13975,"push_stage1.push1_speed":0.10145,"push_stage2.push2_distance":0.11876,"push_stage2.push2_speed":0.14834},"optimized_scores":{"best_composite_score":0.27075,"best_fitness_score":0.51075,"best_task_score":0.71873},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":446.0,"contact_point_centroid":[0.50824,0.00635,0.04753],"force_p95":25.84064,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.10618,"mean_force":8.67384,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50278,0.01768,0.03643]},{"body_a":"attachment","body_b":"push_box","contact_count":251.0,"contact_point_centroid":[0.4975,-0.09065,0.05565],"force_p95":14.18119,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.1431,"mean_force":4.2165,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48094,-0.08591,0.03051]},{"body_a":"world","body_b":"push_box","contact_count":917.0,"contact_point_centroid":[0.52114,-0.02753,-0.00011],"force_p95":13.50431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.69368,"mean_force":4.71793,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50313,0.02186,0.03647]},{"body_a":"world","body_b":"push_box","contact_count":1142.0,"contact_point_centroid":[0.52385,-0.09326,-4e-05],"force_p95":8.03513,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.74917,"mean_force":1.32953,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47283,-0.1098,0.02935]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50686,0.06596,0.18396]},{"body_a":"world","body_b":"push_box","contact_count":1372.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.5121,0.10861,0.0544]},{"body_a":"world","body_b":"push_box","contact_count":2176.0,"contact_point_centroid":[0.50769,-0.09478,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.45598,-0.14949,0.07136]}],"total_contact_groups":7},"final_pose_error":0.0115,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50769,-0.09478,0.02499],"final_tcp_position":[0.45601,-0.14944,0.11642],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":34.99607,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51567,0.13192,0.07135],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09617,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":343.0,"n_steps_budget":630.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":34.99607,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1372.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51132,0.08455,0.0406],"tcp_start":[0.51567,0.13192,0.07135],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":674.0,"n_steps_budget":870.0,"object_pos_end":[0.52647,-0.06986,0.02815],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.08446,"object_to_goal_dist_start":0.19823,"object_z_max":0.02819,"peak_contact_force":2.39322,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1363.0,"raw_peak_contact_force":34.10618,"subtask_id":"push_goal","tcp_end":[0.49747,-0.04656,0.03598],"tcp_start":[0.51132,0.08455,0.0406],"tcp_to_object_dist_end":0.03801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":600.0,"object_pos_end":[0.50769,-0.09478,0.02499],"object_pos_start":[0.52647,-0.06986,0.02815],"object_to_goal_dist_end":0.05576,"object_to_goal_dist_start":0.08446,"object_z_max":0.02969,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1393.0,"raw_peak_contact_force":21.1431,"subtask_id":"push_goal","tcp_end":[0.45913,-0.15032,0.02746],"tcp_start":[0.49747,-0.04656,0.03598],"tcp_to_object_dist_end":0.07382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.50769,-0.09478,0.02499],"object_pos_start":[0.50769,-0.09478,0.02499],"object_to_goal_dist_end":0.05576,"object_to_goal_dist_start":0.05576,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45601,-0.14944,0.11642],"tcp_start":[0.45913,-0.15032,0.02746],"tcp_to_object_dist_end":0.11841,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35519,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.11384,"approach_object.approach_speed":0.04578,"contact_object.contact_force_threshold":11.14414,"push_stage1.push1_distance":0.13653,"push_stage1.push1_speed":0.13868,"push_stage2.push2_distance":0.09327,"push_stage2.push2_speed":0.08303},"optimized_scores":{"best_composite_score":0.24394,"best_fitness_score":0.48394,"best_task_score":0.68994},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":342.0,"contact_point_centroid":[0.48076,0.01955,0.04621],"force_p95":31.05616,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.07131,"mean_force":7.43095,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.4746,0.03033,0.03735]},{"body_a":"world","body_b":"push_box","contact_count":693.0,"contact_point_centroid":[0.49898,-0.00933,-8e-05],"force_p95":15.8791,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.25473,"mean_force":4.22361,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47404,0.03768,0.03754]},{"body_a":"attachment","body_b":"push_box","contact_count":321.0,"contact_point_centroid":[0.49018,-0.07804,0.05437],"force_p95":12.15802,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.81516,"mean_force":3.59067,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47314,-0.07556,0.03106]},{"body_a":"world","body_b":"push_box","contact_count":714.0,"contact_point_centroid":[0.52939,-0.0742,-5e-05],"force_p95":8.19336,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.87909,"mean_force":2.15402,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47331,-0.0741,0.03117]},{"body_a":"world","body_b":"push_box","contact_count":2055.0,"contact_point_centroid":[0.50012,-0.08455,-1e-05],"force_p95":0.3142,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0912,"mean_force":0.25968,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.46609,-0.1148,0.07508]},{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.48424,-0.11173,0.05259],"force_p95":0.90392,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9339,"mean_force":0.6395,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.46768,-0.1154,0.0325]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48411,0.07016,0.18299]},{"body_a":"world","body_b":"push_box","contact_count":1272.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.46947,0.11822,0.05409]}],"total_contact_groups":8},"final_pose_error":0.01151,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.499,-0.08505,0.02499],"final_tcp_position":[0.46621,-0.11478,0.11778],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":37.07131,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47023,0.14026,0.06951],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09356,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":318.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":29.78937,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.4714,0.09536,0.04113],"tcp_start":[0.47023,0.14026,0.06951],"tcp_to_object_dist_end":0.04101,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":561.0,"n_steps_budget":630.0,"object_pos_end":[0.50794,-0.05447,0.02901],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.09594,"object_to_goal_dist_start":0.2095,"object_z_max":0.02909,"peak_contact_force":2.14146,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1035.0,"raw_peak_contact_force":37.07131,"subtask_id":"push_goal","tcp_end":[0.48029,-0.03111,0.03682],"tcp_start":[0.4714,0.09536,0.04113],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":442.0,"n_steps_budget":720.0,"object_pos_end":[0.5014,-0.08352,0.02769],"object_pos_start":[0.50794,-0.05447,0.02901],"object_to_goal_dist_end":0.06654,"object_to_goal_dist_start":0.09594,"object_z_max":0.02997,"peak_contact_force":1.25303,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1035.0,"raw_peak_contact_force":20.81516,"subtask_id":"push_goal","tcp_end":[0.46938,-0.11544,0.02883],"tcp_start":[0.48029,-0.03111,0.03682],"tcp_to_object_dist_end":0.04522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.499,-0.08505,0.02499],"object_pos_start":[0.5014,-0.08352,0.02769],"object_to_goal_dist_end":0.06496,"object_to_goal_dist_start":0.06654,"object_z_max":0.02769,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2087.0,"raw_peak_contact_force":1.0912,"tcp_end":[0.46621,-0.11478,0.11778],"tcp_start":[0.46938,-0.11544,0.02883],"tcp_to_object_dist_end":0.10281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89744,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.08728,"approach_object.approach_speed":0.07469,"contact_object.contact_force_threshold":5.33031,"push_stage1.push1_distance":0.12101,"push_stage1.push1_speed":0.11062,"push_stage2.push2_distance":0.08257,"push_stage2.push2_speed":0.18424},"optimized_scores":{"best_composite_score":0.56975,"best_fitness_score":0.80975,"best_task_score":0.94656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.49359,-0.13969,0.04924],"force_p95":52.99853,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.4119,"mean_force":10.88756,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.45544,-0.13609,0.01576]},{"body_a":"push_box","body_b":"link7","contact_count":465.0,"contact_point_centroid":[0.51789,-0.12096,0.04961],"force_p95":85.06016,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.25974,"mean_force":61.61398,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.4808,-0.11436,0.01606]},{"body_a":"world","body_b":"push_box","contact_count":1306.0,"contact_point_centroid":[0.5086,-0.14546,-0.00018],"force_p95":60.42433,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.42985,"mean_force":22.28841,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47963,-0.1153,0.01595]},{"body_a":"world","body_b":"push_box","contact_count":2122.0,"contact_point_centroid":[0.50665,-0.15196,-2e-05],"force_p95":0.24761,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.88708,"mean_force":0.32349,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.45284,-0.13531,0.06023]},{"body_a":"push_box","body_b":"link7","contact_count":222.0,"contact_point_centroid":[0.54686,-0.08673,0.05274],"force_p95":39.94835,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.81203,"mean_force":23.77582,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.51651,-0.07307,0.01813]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.5412,-0.09526,-8e-05],"force_p95":28.08384,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.47189,"mean_force":10.59769,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.52692,-0.04407,0.01793]},{"body_a":"attachment","body_b":"push_box","contact_count":462.0,"contact_point_centroid":[0.53465,-0.05797,0.04407],"force_p95":20.35547,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.52709,"mean_force":7.97434,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.52584,-0.04679,0.01782]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.52135,-0.10281,0.05311],"force_p95":20.47592,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.88722,"mean_force":14.88595,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.50448,-0.09487,0.01762]},{"body_a":"world","body_b":"push_box","contact_count":3936.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53214,0.02674,0.16431]},{"body_a":"world","body_b":"push_box","contact_count":1256.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.55677,0.03298,0.02431]}],"total_contact_groups":10},"final_pose_error":0.0113,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50673,-0.15213,0.02499],"final_tcp_position":[0.45289,-0.13529,0.10427],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":100.4119,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3936.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.56632,0.05369,0.03091],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":43.5171,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.55022,0.01128,0.02202],"tcp_start":[0.56632,0.05369,0.03091],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":690.0,"object_pos_end":[0.5288,-0.127,0.02807],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03699,"object_to_goal_dist_start":0.13211,"object_z_max":0.0281,"peak_contact_force":35.41513,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1484.0,"raw_peak_contact_force":43.81203,"subtask_id":"push_goal","tcp_end":[0.51064,-0.09196,0.01933],"tcp_start":[0.55022,0.01128,0.02202],"tcp_to_object_dist_end":0.04042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,-0.15229,0.02488],"object_pos_start":[0.5288,-0.127,0.02807],"object_to_goal_dist_end":0.00652,"object_to_goal_dist_start":0.03699,"object_z_max":0.02807,"peak_contact_force":84.50146,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1846.0,"raw_peak_contact_force":89.25974,"subtask_id":"push_goal","tcp_end":[0.45603,-0.13609,0.0151],"tcp_start":[0.51064,-0.09196,0.01933],"tcp_to_object_dist_end":0.05353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50673,-0.15213,0.02499],"object_pos_start":[0.5061,-0.15229,0.02488],"object_to_goal_dist_end":0.00706,"object_to_goal_dist_start":0.00652,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2136.0,"raw_peak_contact_force":100.4119,"tcp_end":[0.45289,-0.13529,0.10427],"tcp_start":[0.45603,-0.13609,0.0151],"tcp_to_object_dist_end":0.09731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```