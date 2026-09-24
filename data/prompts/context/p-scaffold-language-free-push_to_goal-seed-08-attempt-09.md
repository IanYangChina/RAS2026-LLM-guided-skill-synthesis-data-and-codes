## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.2939 | 0.81 | ❌ rejected |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4121 | 0.82 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1877 | 0.00 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3638 | 0.00 | ❌ rejected |
| 5 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2261 | 0.81 | ❌ rejected |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.838, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.294) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
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
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: reach_object
- id: pre_contact_1
  type: align
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
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    pre_push_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **pre_contact_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - pre_push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.294
- **task_score** (E): 0.806
- **fitness_score**: 0.804  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1421 |
| pre_contact_1 | 0.00 | 1.00 | 0.1552 |
| push_1 | 1.00 | 1.00 | 0.1457 |
| retract_1 | 1.00 | 1.00 | 0.0859 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.001, 0.169) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| pre_contact_1 | contact | 0.00 / step_budget | (0.521, -0.001, 0.169)→(0.535, 0.054, 0.025) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.535, 0.054, 0.025)→(0.499, -0.082, 0.021) | (0.526, -0.001, 0.025)→(0.507, -0.113, 0.027) | 0.156→0.039 | 1.00 / 3.000 | 7.681 | 20.334 |
| retract_1 | retract | 1.00 / time_limit | (0.499, -0.082, 0.021)→(0.495, -0.110, 0.098) | (0.507, -0.113, 0.027)→(0.504, -0.115, 0.025) | 0.039→0.038 | 1.00 / 4.000 | 0.245 | 9.413 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.975
- lateral_force_integral: None
- approach_alignment: 0.726
- goal_progress: 0.948
- terminal_score: 0.948
- phase_score: 0.918
- phase_breakdown.push_to_goal_score: 0.943
- phase_breakdown.reach_object_score: 0.861

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.930
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.948
- **Median Q (composite search score)**: 0.390
- **K-run variance**: 0.0248
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.264


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73723,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1353,"pre_contact_1.contact_force_threshold":4.33728,"pre_contact_1.pre_push_offset":0.05871,"push_1.push_distance":0.21693,"push_1.push_duration":4.4088,"push_1.push_speed":0.08953,"retract_1.retract_duration":5.01831,"retract_1.retract_height":0.10615,"retract_1.speed":0.05985},"optimized_scores":{"best_composite_score":0.07196,"best_fitness_score":0.58196,"best_task_score":0.53336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.51765,-0.02504,0.05594],"force_p95":13.80954,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.4703,"mean_force":3.15519,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48075,-0.03084,0.02292]},{"body_a":"push_box","body_b":"link7","contact_count":256.0,"contact_point_centroid":[0.51495,-0.00911,0.056],"force_p95":18.12215,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.11023,"mean_force":11.71357,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47887,-0.01152,0.02279]},{"body_a":"world","body_b":"push_box","contact_count":1703.0,"contact_point_centroid":[0.50109,0.00776,-3e-05],"force_p95":15.67485,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.70467,"mean_force":4.45008,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47249,0.05289,0.02294]},{"body_a":"attachment","body_b":"push_box","contact_count":755.0,"contact_point_centroid":[0.48469,0.02173,0.04473],"force_p95":14.99571,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.16877,"mean_force":5.52188,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47434,0.03133,0.02259]},{"body_a":"world","body_b":"push_box","contact_count":2812.0,"contact_point_centroid":[0.51751,-0.05442,-4e-05],"force_p95":1.1448,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.07487,"mean_force":0.39354,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48272,-0.06326,0.06572]},{"body_a":"attachment","body_b":"push_box","contact_count":393.0,"contact_point_centroid":[0.49557,-0.04559,0.05812],"force_p95":0.7644,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.67671,"mean_force":0.61696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47956,-0.04277,0.04056]},{"body_a":"world","body_b":"push_box","contact_count":1824.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4886,0.02581,0.2342]},{"body_a":"world","body_b":"push_box","contact_count":3588.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"contact","tcp_position_centroid":[0.47271,0.08339,0.09471]}],"total_contact_groups":8},"final_pose_error":0.07009,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50772,-0.05254,0.02499],"final_tcp_position":[0.48729,-0.09147,0.09475],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":25.4703,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":456.0,"n_steps_budget":960.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47827,0.05296,0.16831],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":897.0,"n_steps_budget":990.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3588.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46977,0.11333,0.02659],"tcp_start":[0.47827,0.05296,0.16831],"tcp_to_object_dist_end":0.05569,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51559,-0.05026,0.02949],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.10105,"object_to_goal_dist_start":0.2095,"object_z_max":0.02958,"peak_contact_force":19.51154,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2714.0,"raw_peak_contact_force":24.11023,"subtask_id":"push_to_goal","tcp_end":[0.48102,-0.03045,0.02297],"tcp_start":[0.46977,0.11333,0.02659],"tcp_to_object_dist_end":0.04038,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50772,-0.05254,0.02499],"object_pos_start":[0.51559,-0.05026,0.02949],"object_to_goal_dist_end":0.09776,"object_to_goal_dist_start":0.10105,"object_z_max":0.02975,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3216.0,"raw_peak_contact_force":25.4703,"tcp_end":[0.48729,-0.09147,0.09475],"tcp_start":[0.48102,-0.03045,0.02297],"tcp_to_object_dist_end":0.08246,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65693,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14465,"pre_contact_1.contact_force_threshold":14.0818,"pre_contact_1.pre_push_offset":0.06666,"push_1.push_distance":0.28201,"push_1.push_duration":5.67882,"push_1.push_speed":0.09536,"retract_1.retract_duration":5.41115,"retract_1.retract_height":0.16172,"retract_1.speed":0.04885},"optimized_scores":{"best_composite_score":0.42031,"best_fitness_score":0.93031,"best_task_score":0.94837},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":726.0,"contact_point_centroid":[0.52668,-0.06074,0.02077],"force_p95":15.04819,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.85159,"mean_force":4.01098,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52706,-0.04881,0.01976]},{"body_a":"world","body_b":"push_box","contact_count":2142.0,"contact_point_centroid":[0.53034,-0.07183,-3e-05],"force_p95":6.08284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.55886,"mean_force":1.62159,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53513,-0.02721,0.02007]},{"body_a":"world","body_b":"push_box","contact_count":3978.0,"contact_point_centroid":[0.50672,-0.14878,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76338,"mean_force":0.24634,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50021,-0.10812,0.0553]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50874,-0.12229,0.03516],"force_p95":0.63979,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67142,"mean_force":0.35506,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50514,-0.11028,0.02007]},{"body_a":"world","body_b":"push_box","contact_count":1788.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51753,-0.01132,0.23802]},{"body_a":"world","body_b":"push_box","contact_count":3920.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"contact","tcp_position_centroid":[0.54798,0.00568,0.09815]}],"total_contact_groups":6},"final_pose_error":0.09876,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50671,-0.14879,0.02499],"final_tcp_position":[0.49907,-0.11144,0.0958],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":20.85159,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":900.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.53746,-0.02318,0.17623],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3920.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.56118,0.03447,0.02496],"tcp_start":[0.53746,-0.02318,0.17623],"tcp_to_object_dist_end":0.06234,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,-0.14718,0.02514],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.00757,"object_to_goal_dist_start":0.13211,"object_z_max":0.0253,"peak_contact_force":1.65111,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2868.0,"raw_peak_contact_force":20.85159,"subtask_id":"push_to_goal","tcp_end":[0.50517,-0.11022,0.02008],"tcp_start":[0.56118,0.03447,0.02496],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,-0.14879,0.02499],"object_pos_start":[0.50702,-0.14718,0.02514],"object_to_goal_dist_end":0.00682,"object_to_goal_dist_start":0.00757,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.76338,"tcp_end":[0.49907,-0.11144,0.0958],"tcp_start":[0.50517,-0.11022,0.02008],"tcp_to_object_dist_end":0.08042,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65441,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13137,"pre_contact_1.contact_force_threshold":7.19681,"pre_contact_1.pre_push_offset":0.0588,"push_1.push_distance":0.19056,"push_1.push_duration":5.32211,"push_1.push_speed":0.08419,"retract_1.retract_duration":4.27301,"retract_1.retract_height":0.11423,"retract_1.speed":0.05613},"optimized_scores":{"best_composite_score":0.38954,"best_fitness_score":0.89954,"best_task_score":0.93584},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":699.0,"contact_point_centroid":[0.53566,-0.06237,0.02003],"force_p95":12.02637,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.04052,"mean_force":3.58258,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5379,-0.05066,0.01946]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.5306,-0.07912,-3e-05],"force_p95":4.44106,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.61901,"mean_force":1.41635,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54384,-0.03889,0.0198]},{"body_a":"world","body_b":"push_box","contact_count":3559.0,"contact_point_centroid":[0.49649,-0.14517,-2e-05],"force_p95":0.41227,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00563,"mean_force":0.26937,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50312,-0.11313,0.06198]},{"body_a":"attachment","body_b":"push_box","contact_count":152.0,"contact_point_centroid":[0.50185,-0.11884,0.04273],"force_p95":0.74229,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.78224,"mean_force":0.56101,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50464,-0.1072,0.0421]},{"body_a":"world","body_b":"push_box","contact_count":2060.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52243,-0.0158,0.2308]},{"body_a":"world","body_b":"push_box","contact_count":3456.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"contact","tcp_position_centroid":[0.55918,-0.00837,0.09126]}],"total_contact_groups":6},"final_pose_error":0.04201,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4968,-0.14249,0.02499],"final_tcp_position":[0.49931,-0.12733,0.10387],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":16.04052,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":990.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54727,-0.0322,0.16213],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":864.0,"n_steps_budget":930.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3456.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.57395,0.01556,0.02487],"tcp_start":[0.54727,-0.0322,0.16213],"tcp_to_object_dist_end":0.05417,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49876,-0.14168,0.02501],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.00841,"object_to_goal_dist_start":0.12728,"object_z_max":0.02528,"peak_contact_force":1.87998,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2899.0,"raw_peak_contact_force":16.04052,"subtask_id":"push_to_goal","tcp_end":[0.51117,-0.10676,0.01981],"tcp_start":[0.57395,0.01556,0.02487],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4968,-0.14249,0.02499],"object_pos_start":[0.49876,-0.14168,0.02501],"object_to_goal_dist_end":0.00817,"object_to_goal_dist_start":0.00841,"object_z_max":0.02602,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3711.0,"raw_peak_contact_force":2.00563,"tcp_end":[0.49931,-0.12733,0.10387],"tcp_start":[0.51117,-0.10676,0.01981],"tcp_to_object_dist_end":0.08036,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```