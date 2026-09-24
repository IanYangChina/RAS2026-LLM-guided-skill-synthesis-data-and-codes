## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.0916 | 0.38 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.6665 | 0.74 | ❌ rejected |
| 9 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3836 | 0.88 | ✅ accepted |
| 8 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3499 | 0.77 | ❌ rejected |
| 7 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | pose_tolerance | 10 | 0.2268 | 0.38 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.885, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.092) — your mutation base

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
      distance: 0.2
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
      - 0.35
      default: 0.2
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
    push1_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
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
      distance: 0.12
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
      - 0.25
      default: 0.12
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
    push2_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push1_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push1_speed: status=consumed; consumers=generator.speed (replace)
    - push1_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_stage2** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push2_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push2_speed: status=consumed; consumers=generator.speed (replace)
    - push2_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.092
- **task_score** (E): 0.384
- **fitness_score**: 0.298  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1652 |
| contact_object | 1.00 | 1.00 | 0.0921 |
| push_stage1 | 1.00 | 1.00 | 0.1207 |
| push_stage2 | 1.00 | 1.00 | 0.1314 |
| retract_after_push | 1.00 | 1.00 | 0.0882 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.025, 0.143) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 1.00 / force_exceeded | (0.509, 0.025, 0.143)→(0.510, 0.040, 0.052) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push_stage1 | push | 1.00 / time_limit | (0.510, 0.040, 0.052)→(0.498, -0.079, 0.048) | (0.513, 0.027, 0.025)→(0.508, -0.028, 0.029) | 0.180→0.125 | 1.00 / 3.333 | 0.948 | 80.571 |
| push_stage2 | push | 1.00 / time_limit | (0.498, -0.079, 0.048)→(0.484, -0.205, 0.038) | (0.508, -0.028, 0.029)→(0.504, -0.037, 0.025) | 0.125→0.115 | 1.00 / 4.000 | 0.245 | 11.987 |
| retract_after_push | retract | 1.00 / step_budget | (0.484, -0.205, 0.038)→(0.480, -0.204, 0.126) | (0.504, -0.037, 0.025)→(0.504, -0.037, 0.025) | 0.115→0.115 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.553
- lateral_force_integral: None
- approach_alignment: 0.874
- goal_progress: 0.552
- terminal_score: 0.552
- phase_score: 0.382
- phase_breakdown.push_goal_score: 0.317
- phase_breakdown.reach_object_score: 0.535

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.450
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.552
- **Median Q (composite search score)**: 0.023
- **K-run variance**: 0.0116
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47134,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.11846,"approach_object.approach_speed":0.04897,"contact_object.contact_force_threshold":9.72409,"push_stage1.push1_distance":0.11354,"push_stage1.push1_speed":0.09531,"push_stage1.push1_time":1.3823,"push_stage2.push2_distance":0.12581,"push_stage2.push2_speed":0.18284,"push_stage2.push2_time":2.87128},"optimized_scores":{"best_composite_score":0.02292,"best_fitness_score":0.22959,"best_task_score":0.31216},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":563.0,"contact_point_centroid":[0.51609,0.02561,0.05057],"force_p95":76.16264,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.73498,"mean_force":50.55639,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.5078,0.01936,0.05192]},{"body_a":"world","body_b":"push_box","contact_count":1504.0,"contact_point_centroid":[0.51414,0.01974,-0.00022],"force_p95":42.69314,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.43657,"mean_force":19.34549,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50693,0.01504,0.05132]},{"body_a":"attachment","body_b":"push_box","contact_count":29.0,"contact_point_centroid":[0.49971,-0.03575,0.04775],"force_p95":5.99987,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.89075,"mean_force":1.45458,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.49814,-0.04764,0.0467]},{"body_a":"world","body_b":"push_box","contact_count":2160.0,"contact_point_centroid":[0.50968,-0.01338,-1e-05],"force_p95":0.24832,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.70713,"mean_force":0.26933,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.49109,-0.10289,0.04242]},{"body_a":"world","body_b":"push_box","contact_count":2208.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50436,0.02123,0.22571]},{"body_a":"world","body_b":"push_box","contact_count":2124.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.50965,0.05212,0.09978]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.50968,-0.01399,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48302,-0.16061,0.08433]}],"total_contact_groups":7},"final_pose_error":0.01204,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50968,-0.01399,0.02499],"final_tcp_position":[0.48309,-0.16056,0.12946],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2208.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51072,0.04352,0.15121],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":531.0,"n_steps_budget":810.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51112,0.0609,0.05249],"tcp_start":[0.51072,0.04352,0.15121],"tcp_to_object_dist_end":0.03077,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.51074,-0.01163,0.02715],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.13881,"object_to_goal_dist_start":0.19823,"object_z_max":0.03533,"peak_contact_force":0.70363,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2067.0,"raw_peak_contact_force":79.73498,"subtask_id":"push_goal","tcp_end":[0.49914,-0.04588,0.04778],"tcp_start":[0.51112,0.0609,0.05249],"tcp_to_object_dist_end":0.04163,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":600.0,"object_pos_end":[0.50968,-0.01399,0.02499],"object_pos_start":[0.51074,-0.01163,0.02715],"object_to_goal_dist_end":0.13635,"object_to_goal_dist_start":0.13881,"object_z_max":0.02715,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2189.0,"raw_peak_contact_force":10.89075,"subtask_id":"push_goal","tcp_end":[0.48626,-0.16146,0.04104],"tcp_start":[0.49914,-0.04588,0.04778],"tcp_to_object_dist_end":0.15018,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50968,-0.01399,0.02499],"object_pos_start":[0.50968,-0.01399,0.02499],"object_to_goal_dist_end":0.13635,"object_to_goal_dist_start":0.13635,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48309,-0.16056,0.12946],"tcp_start":[0.48626,-0.16146,0.04104],"tcp_to_object_dist_end":0.18194,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50538,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.07681,"approach_object.approach_speed":0.05469,"contact_object.contact_force_threshold":4.06119,"push_stage1.push1_distance":0.23462,"push_stage1.push1_speed":0.09977,"push_stage1.push1_time":2.23999,"push_stage2.push2_distance":0.17044,"push_stage2.push2_speed":0.09787,"push_stage2.push2_time":1.78962},"optimized_scores":{"best_composite_score":0.00809,"best_fitness_score":0.21476,"best_task_score":0.28881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":512.0,"contact_point_centroid":[0.48601,0.03622,0.05049],"force_p95":81.50093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.70537,"mean_force":55.70515,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47751,0.03,0.05176]},{"body_a":"world","body_b":"push_box","contact_count":2753.0,"contact_point_centroid":[0.48048,0.01405,-0.00013],"force_p95":55.53197,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.70821,"mean_force":10.71111,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.48031,-0.01969,0.0495]},{"body_a":"world","body_b":"push_box","contact_count":2720.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48795,0.02663,0.20522]},{"body_a":"world","body_b":"push_box","contact_count":1320.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.47436,0.06136,0.08027]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47953,-0.00242,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.49313,-0.16837,0.04283]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.47953,-0.00242,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50077,-0.24677,0.08423]}],"total_contact_groups":6},"final_pose_error":0.01301,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47953,-0.00242,0.02499],"final_tcp_position":[0.50088,-0.24674,0.12931],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2720.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47741,0.05423,0.11061],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47368,0.06891,0.05232],"tcp_start":[0.47741,0.05423,0.11061],"tcp_to_object_dist_end":0.02978,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47953,-0.00242,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.149,"object_to_goal_dist_start":0.2095,"object_z_max":0.03534,"peak_contact_force":0.24525,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3265.0,"raw_peak_contact_force":85.70537,"subtask_id":"push_goal","tcp_end":[0.48589,-0.09083,0.04773],"tcp_start":[0.47368,0.06891,0.05232],"tcp_to_object_dist_end":0.09151,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47953,-0.00242,0.02499],"object_pos_start":[0.47953,-0.00242,0.02499],"object_to_goal_dist_end":0.149,"object_to_goal_dist_start":0.149,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.50407,-0.24813,0.04184],"tcp_start":[0.48589,-0.09083,0.04773],"tcp_to_object_dist_end":0.24751,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.47953,-0.00242,0.02499],"object_pos_start":[0.47953,-0.00242,0.02499],"object_to_goal_dist_end":0.149,"object_to_goal_dist_start":0.149,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50088,-0.24674,0.12931],"tcp_start":[0.50407,-0.24813,0.04184],"tcp_to_object_dist_end":0.26652,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46237,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13554,"approach_object.approach_speed":0.03608,"contact_object.contact_force_threshold":7.2484,"push_stage1.push1_distance":0.10048,"push_stage1.push1_speed":0.19341,"push_stage1.push1_time":1.75207,"push_stage2.push2_distance":0.14474,"push_stage2.push2_speed":0.07092,"push_stage2.push2_time":1.46772},"optimized_scores":{"best_composite_score":0.24368,"best_fitness_score":0.45034,"best_task_score":0.55231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":548.0,"contact_point_centroid":[0.53877,-0.04515,0.05094],"force_p95":73.43283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.272,"mean_force":53.07041,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.52975,-0.05086,0.05244]},{"body_a":"world","body_b":"push_box","contact_count":1160.0,"contact_point_centroid":[0.53717,-0.05191,-0.00026],"force_p95":58.67394,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.88729,"mean_force":25.54586,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.53211,-0.04372,0.05233]},{"body_a":"attachment","body_b":"push_box","contact_count":145.0,"contact_point_centroid":[0.50834,-0.10079,0.04533],"force_p95":10.63283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.82449,"mean_force":2.62521,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.50205,-0.1112,0.04409]},{"body_a":"world","body_b":"push_box","contact_count":3500.0,"contact_point_centroid":[0.5236,-0.0922,-1e-05],"force_p95":0.47888,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.44954,"mean_force":0.37065,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48094,-0.15786,0.03682]},{"body_a":"world","body_b":"push_box","contact_count":2092.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,-0.01136,0.23367]},{"body_a":"world","body_b":"push_box","contact_count":2424.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.53946,-0.01686,0.10694]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.52227,-0.09521,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.45731,-0.20426,0.07402]}],"total_contact_groups":7},"final_pose_error":0.01186,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52227,-0.09521,0.02499],"final_tcp_position":[0.45736,-0.20424,0.11915],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.53754,-0.02329,0.1673],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":606.0,"n_steps_budget":900.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.54389,-0.0106,0.05242],"tcp_start":[0.53754,-0.02329,0.1673],"tcp_to_object_dist_end":0.03126,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.53375,-0.07093,0.03524],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.08658,"object_to_goal_dist_start":0.13211,"object_z_max":0.03523,"peak_contact_force":1.89517,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1708.0,"raw_peak_contact_force":76.272,"subtask_id":"push_goal","tcp_end":[0.51036,-0.09881,0.04931],"tcp_start":[0.54389,-0.0106,0.05242],"tcp_to_object_dist_end":0.03901,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52227,-0.09521,0.02499],"object_pos_start":[0.53375,-0.07093,0.03524],"object_to_goal_dist_end":0.05915,"object_to_goal_dist_start":0.08658,"object_z_max":0.03525,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3645.0,"raw_peak_contact_force":24.82449,"subtask_id":"push_goal","tcp_end":[0.46046,-0.20542,0.03054],"tcp_start":[0.51036,-0.09881,0.04931],"tcp_to_object_dist_end":0.12649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.52227,-0.09521,0.02499],"object_pos_start":[0.52227,-0.09521,0.02499],"object_to_goal_dist_end":0.05915,"object_to_goal_dist_start":0.05915,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45736,-0.20424,0.11915],"tcp_start":[0.46046,-0.20542,0.03054],"tcp_to_object_dist_end":0.15801,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```