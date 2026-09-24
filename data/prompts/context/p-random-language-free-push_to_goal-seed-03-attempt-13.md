## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.1420 | 0.58 | ❌ rejected |
| 12 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.0560 | 0.42 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.2113 | 0.00 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 12 | 0.2406 | 0.55 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.2991 | 0.42 | ❌ rejected |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.824, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.142) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
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
    - 0.05
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_lateral_distance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_lateral_distance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.05], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_lateral_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_lateral_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.142
- **task_score** (E): 0.581
- **fitness_score**: 0.418  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2237 |
| descend_1 | 1.00 | 1.00 | 0.0449 |
| push_1 | 0.00 | 1.00 | 0.0004 |
| retract_1 | 1.00 | 1.00 | 0.1612 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.033, 0.088) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.512, 0.033, 0.088)→(0.511, 0.039, 0.044) | (0.513, 0.002, 0.025)→(0.513, 0.001, 0.025) | 0.160→0.158 | 1.00 / 2.000 | 1.041 | 149.899 |
| push_1 | push | 0.00 / guard_failure | (0.498, -0.004, 0.034)→(0.498, -0.004, 0.034) | (0.513, 0.001, 0.025)→(0.509, -0.039, 0.025) | 0.158→0.120 | 1.00 / 2.000 | 0.128 | 49.752 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.004, 0.034)→(0.497, -0.137, 0.112) | (0.509, -0.040, 0.025)→(0.514, -0.093, 0.025) | 0.119→0.067 | 1.00 / 4.000 | 0.245 | 15.356 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.650
- lateral_force_integral: None
- approach_alignment: 0.776
- goal_progress: 0.618
- terminal_score: 0.618
- phase_score: 0.509
- phase_breakdown.push_to_goal_score: 0.527
- phase_breakdown.approach_object_score: 0.466

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.553
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.618
- **Median Q (composite search score)**: -0.159
- **K-run variance**: 0.0108
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.284


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73214,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06866,"approach_1.approach_lateral_distance":0.03084,"approach_1.approach_speed":0.11034,"descend_1.descend_lateral_distance":0.04867,"descend_1.descend_speed":0.06833,"descend_1.descend_tolerance":0.02892,"push_1.push_distance":0.20855,"push_1.push_speed":0.09795,"push_1.push_tolerance":0.03419,"retract_1.retract_speed":0.11043},"optimized_scores":{"best_composite_score":-0.2599,"best_fitness_score":0.3001,"best_task_score":0.55422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.43142,-0.00706,0.04163],"force_p95":41.31772,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.8198,"mean_force":15.53962,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43141,0.00459,0.04163]},{"body_a":"world","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":2.00977,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.03509,"mean_force":1.05189,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43057,0.00749,0.04258]},{"body_a":"attachment","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.44228,-0.03224,0.0526],"force_p95":16.50612,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.53595,"mean_force":4.65574,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4402,-0.02064,0.05232]},{"body_a":"world","body_b":"push_box","contact_count":1019.0,"contact_point_centroid":[0.46723,-0.08685,-0.00013],"force_p95":4.04236,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.3141,"mean_force":0.87667,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46729,-0.08282,0.08469]},{"body_a":"world","body_b":"push_box","contact_count":2496.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46941,-0.00146,0.20175]},{"body_a":"world","body_b":"push_box","contact_count":516.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43503,0.00236,0.07496]}],"total_contact_groups":6},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46955,-0.10152,0.02498],"final_tcp_position":[0.49121,-0.13653,0.11316],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":45.8198,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2496.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.43939,-0.00296,0.10337],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":129.0,"n_steps_budget":750.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":516.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.43103,0.00852,0.04419],"tcp_start":[0.43939,-0.00296,0.10337],"tcp_to_object_dist_end":0.04845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.45031,-0.03167,0.02505],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12834,"object_to_goal_dist_start":0.12843,"object_z_max":0.02507,"peak_contact_force":0.3816,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":59.0,"raw_peak_contact_force":45.8198,"subtask_id":"push_to_goal","tcp_end":[0.43143,0.00389,0.04154],"tcp_start":[0.43148,0.00417,0.04159],"tcp_to_object_dist_end":0.04351,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.46955,-0.10152,0.02498],"object_pos_start":[0.45034,-0.03188,0.02506],"object_to_goal_dist_end":0.05725,"object_to_goal_dist_start":0.12813,"object_z_max":0.03534,"peak_contact_force":0.24515,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1118.0,"raw_peak_contact_force":17.53595,"tcp_end":[0.49121,-0.13653,0.11316],"tcp_start":[0.43143,0.00389,0.04154],"tcp_to_object_dist_end":0.09732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95146,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04144,"approach_1.approach_lateral_distance":0.04231,"approach_1.approach_speed":0.15366,"descend_1.descend_lateral_distance":0.03076,"descend_1.descend_speed":0.06958,"descend_1.descend_tolerance":0.025,"push_1.push_distance":0.09798,"push_1.push_speed":0.11808,"push_1.push_tolerance":0.03711,"retract_1.retract_speed":0.13068},"optimized_scores":{"best_composite_score":-0.00743,"best_fitness_score":0.55257,"best_task_score":0.61848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.56555,0.0259,0.04802],"force_p95":201.34884,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.2665,"mean_force":135.88883,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56034,0.03564,0.04817]},{"body_a":"world","body_b":"push_box","contact_count":255.0,"contact_point_centroid":[0.5545,0.00197,-7e-05],"force_p95":78.52662,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.31466,"mean_force":11.54416,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55966,0.03713,0.05923]},{"body_a":"attachment","body_b":"push_box","contact_count":65.0,"contact_point_centroid":[0.54775,-0.02278,0.04464],"force_p95":11.79928,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.96074,"mean_force":4.96643,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54373,-0.0112,0.03241]},{"body_a":"world","body_b":"push_box","contact_count":126.0,"contact_point_centroid":[0.54786,-0.05539,-0.0001],"force_p95":11.09907,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.46012,"mean_force":3.28429,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54611,-0.00451,0.03373]},{"body_a":"world","body_b":"push_box","contact_count":840.0,"contact_point_centroid":[0.54336,-0.10809,-0.00013],"force_p95":1.51509,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.01856,"mean_force":0.53378,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51016,-0.10595,0.0744]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.52536,-0.088,0.04771],"force_p95":6.49735,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.85848,"mean_force":1.79896,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51917,-0.07753,0.0448]},{"body_a":"world","body_b":"push_box","contact_count":2952.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52893,0.01926,0.18559]}],"total_contact_groups":7},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53767,-0.10176,0.02499],"final_tcp_position":[0.50001,-0.13879,0.1088],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":203.2665,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2952.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.55986,0.03884,0.07251],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":71.0,"n_steps_budget":600.0,"object_pos_end":[0.55263,-0.00124,0.02531],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1578,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":1.07772,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":276.0,"raw_peak_contact_force":203.2665,"tcp_end":[0.56188,0.03591,0.04375],"tcp_start":[0.55986,0.03884,0.07251],"tcp_to_object_dist_end":0.04249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":154.0,"n_steps_budget":750.0,"object_pos_end":[0.54438,-0.08995,0.02497],"object_pos_start":[0.55263,-0.00124,0.02531],"object_to_goal_dist_end":0.07467,"object_to_goal_dist_start":0.1578,"object_z_max":0.02642,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":191.0,"raw_peak_contact_force":46.96074,"subtask_id":"push_to_goal","tcp_end":[0.52896,-0.05543,0.02525],"tcp_start":[0.52908,-0.05505,0.02534],"tcp_to_object_dist_end":0.03782,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":690.0,"object_pos_end":[0.53767,-0.10176,0.02499],"object_pos_start":[0.54469,-0.09081,0.02518],"object_to_goal_dist_end":0.06121,"object_to_goal_dist_start":0.07416,"object_z_max":0.03149,"peak_contact_force":0.24524,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":918.0,"raw_peak_contact_force":7.01856,"tcp_end":[0.50001,-0.13879,0.1088],"tcp_start":[0.52896,-0.05543,0.02525],"tcp_to_object_dist_end":0.09906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05553,"approach_1.approach_lateral_distance":0.03074,"approach_1.approach_speed":0.13067,"descend_1.descend_lateral_distance":0.04172,"descend_1.descend_speed":0.08636,"descend_1.descend_tolerance":0.018,"push_1.push_distance":0.08573,"push_1.push_speed":0.10738,"push_1.push_tolerance":0.03587,"retract_1.retract_speed":0.07597},"optimized_scores":{"best_composite_score":-0.15854,"best_fitness_score":0.40146,"best_task_score":0.57149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.54558,0.06224,0.04844],"force_p95":199.03056,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":246.18432,"mean_force":130.81769,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53955,0.07153,0.04843]},{"body_a":"world","body_b":"push_box","contact_count":374.0,"contact_point_centroid":[0.53758,0.03801,-4e-05],"force_p95":26.65716,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":231.62391,"mean_force":7.66481,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53746,0.06719,0.06636]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.53723,0.04932,0.04104],"force_p95":37.17062,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.4743,"mean_force":8.09274,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53666,0.06084,0.03855]},{"body_a":"world","body_b":"push_box","contact_count":62.0,"contact_point_centroid":[0.526,0.00788,-0.0003],"force_p95":15.36859,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.82225,"mean_force":3.59187,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53552,0.05412,0.03737]},{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.52791,0.00267,0.04208],"force_p95":18.39881,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.51451,"mean_force":5.51749,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52563,0.01429,0.04256]},{"body_a":"world","body_b":"push_box","contact_count":1292.0,"contact_point_centroid":[0.53378,-0.06722,-9e-05],"force_p95":4.09363,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.12631,"mean_force":0.82569,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51015,-0.07149,0.08262]},{"body_a":"world","body_b":"push_box","contact_count":2912.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51727,0.03117,0.193]}],"total_contact_groups":7},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53521,-0.07635,0.02499],"final_tcp_position":[0.49941,-0.13453,0.11282],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":246.18432,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.53653,0.06297,0.08718],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":100.0,"n_steps_budget":600.0,"object_pos_end":[0.53584,0.03547,0.02521],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1889,"object_to_goal_dist_start":0.1905,"object_z_max":0.02508,"peak_contact_force":1.80004,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":395.0,"raw_peak_contact_force":246.18432,"tcp_end":[0.54148,0.07358,0.04385],"tcp_start":[0.53653,0.06297,0.08718],"tcp_to_object_dist_end":0.0428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":62.0,"n_steps_budget":750.0,"object_pos_end":[0.53278,0.00326,0.02468],"object_pos_start":[0.53584,0.03547,0.02521],"object_to_goal_dist_end":0.15672,"object_to_goal_dist_start":0.1889,"object_z_max":0.02679,"peak_contact_force":0.00172,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":85.0,"raw_peak_contact_force":56.4743,"subtask_id":"push_to_goal","tcp_end":[0.53239,0.03909,0.03411],"tcp_start":[0.53246,0.03947,0.03421],"tcp_to_object_dist_end":0.03706,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.53521,-0.07635,0.02499],"object_pos_start":[0.5329,0.00267,0.02483],"object_to_goal_dist_end":0.08163,"object_to_goal_dist_start":0.15618,"object_z_max":0.03534,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1402.0,"raw_peak_contact_force":21.51451,"tcp_end":[0.49941,-0.13453,0.11282],"tcp_start":[0.53239,0.03909,0.03411],"tcp_to_object_dist_end":0.11127,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```