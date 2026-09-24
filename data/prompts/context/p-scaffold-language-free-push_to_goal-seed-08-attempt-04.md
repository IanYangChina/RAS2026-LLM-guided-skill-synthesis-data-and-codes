## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3922 | 0.81 | ❌ rejected |
| 3 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4294 | 0.84 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2385 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4400 | 0.75 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4443 | 0.76 | ✅ accepted |

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

## Current Skill (Q=0.392) — your mutation base

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

- **Composite score**: 0.392
- **task_score** (E): 0.808
- **fitness_score**: 0.802  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1361 |
| pre_contact_1 | 1.00 | 1.00 | 0.1730 |
| push_1 | 0.67 | 1.00 | 0.1801 |
| retract_1 | 0.67 | 1.00 | 0.1349 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.001, 0.175) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| pre_contact_1 | align | 1.00 / step_budget | (0.521, -0.001, 0.175)→(0.541, 0.081, 0.026) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.541, 0.081, 0.026)→(0.499, -0.089, 0.021) | (0.526, -0.001, 0.025)→(0.498, -0.120, 0.026) | 0.156→0.039 | 1.00 / 3.667 | 11.513 | 20.960 |
| retract_1 | retract | 0.67 / step_budget | (0.499, -0.089, 0.021)→(0.497, -0.134, 0.135) | (0.498, -0.120, 0.026)→(0.493, -0.125, 0.025) | 0.039→0.036 | 1.00 / 4.000 | 0.245 | 18.718 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.767
- goal_progress: 0.922
- terminal_score: 0.922
- phase_score: 0.890
- phase_breakdown.push_to_goal_score: 0.937
- phase_breakdown.reach_object_score: 0.781

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.903
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.922
- **Median Q (composite search score)**: 0.484
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.430


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53704,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14933,"pre_contact_1.align_speed":0.12954,"pre_contact_1.pre_push_offset":0.08815,"push_1.push_speed":0.0572,"push_1.push_tolerance":0.02009,"retract_1.retract_height":0.07783,"retract_1.speed":0.07801},"optimized_scores":{"best_composite_score":0.19942,"best_fitness_score":0.60942,"best_task_score":0.59544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52068,-0.02851,0.05537],"force_p95":20.15424,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.90173,"mean_force":5.19111,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48278,-0.02739,0.02254]},{"body_a":"attachment","body_b":"push_box","contact_count":634.0,"contact_point_centroid":[0.48454,0.02124,0.04232],"force_p95":17.61264,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.854,"mean_force":5.34599,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47575,0.03165,0.02263]},{"body_a":"world","body_b":"push_box","contact_count":1922.0,"contact_point_centroid":[0.49329,0.02132,-3e-05],"force_p95":13.28361,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.5405,"mean_force":2.85853,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4711,0.07505,0.02335]},{"body_a":"push_box","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.51844,-0.01583,0.05526],"force_p95":18.14972,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.1547,"mean_force":10.72669,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48118,-0.01429,0.02234]},{"body_a":"world","body_b":"push_box","contact_count":2719.0,"contact_point_centroid":[0.51016,-0.06577,-4e-05],"force_p95":1.25578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.5886,"mean_force":0.41347,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48818,-0.08952,0.07192]},{"body_a":"attachment","body_b":"push_box","contact_count":331.0,"contact_point_centroid":[0.49497,-0.05398,0.0469],"force_p95":1.14469,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.41209,"mean_force":0.772,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48294,-0.05089,0.04564]},{"body_a":"world","body_b":"push_box","contact_count":1668.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4888,0.02546,0.24123]},{"body_a":"world","body_b":"push_box","contact_count":3392.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.47171,0.09571,0.10447]}],"total_contact_groups":8},"final_pose_error":0.01576,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50017,-0.06524,0.02499],"final_tcp_position":[0.49487,-0.13725,0.09512],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":25.90173,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47857,0.05243,0.18224],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3392.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46707,0.14079,0.02779],"tcp_start":[0.47857,0.05243,0.18224],"tcp_to_object_dist_end":0.08325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51286,-0.0523,0.02924],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.09864,"object_to_goal_dist_start":0.2095,"object_z_max":0.02922,"peak_contact_force":20.09856,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2711.0,"raw_peak_contact_force":23.854,"subtask_id":"push_to_goal","tcp_end":[0.48299,-0.02707,0.0225],"tcp_start":[0.46707,0.14079,0.02779],"tcp_to_object_dist_end":0.03967,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50017,-0.06524,0.02499],"object_pos_start":[0.51286,-0.0523,0.02924],"object_to_goal_dist_end":0.08476,"object_to_goal_dist_start":0.09864,"object_z_max":0.03259,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3058.0,"raw_peak_contact_force":25.90173,"tcp_end":[0.49487,-0.13725,0.09512],"tcp_start":[0.48299,-0.02707,0.0225],"tcp_to_object_dist_end":0.10065,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79487,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13308,"pre_contact_1.align_speed":0.13589,"pre_contact_1.pre_push_offset":0.0988,"push_1.push_speed":0.07085,"push_1.push_tolerance":0.02493,"retract_1.retract_height":0.1743,"retract_1.speed":0.06363},"optimized_scores":{"best_composite_score":0.49273,"best_fitness_score":0.90273,"best_task_score":0.92166},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50359,-0.13003,0.02081],"force_p95":28.31754,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.35178,"mean_force":19.00931,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5063,-0.11841,0.0202]},{"body_a":"attachment","body_b":"push_box","contact_count":571.0,"contact_point_centroid":[0.52836,-0.06016,0.02057],"force_p95":18.95172,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.09276,"mean_force":4.87344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52971,-0.04832,0.02021]},{"body_a":"world","body_b":"push_box","contact_count":2375.0,"contact_point_centroid":[0.53014,-0.06526,-4e-05],"force_p95":6.08743,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.75494,"mean_force":1.45054,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54087,-0.01598,0.02056]},{"body_a":"world","body_b":"push_box","contact_count":3973.0,"contact_point_centroid":[0.49064,-0.15448,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.5609,"mean_force":0.25621,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5007,-0.11429,0.07376]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51761,-0.0114,0.23239]},{"body_a":"world","body_b":"push_box","contact_count":3044.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.55261,0.01846,0.09476]}],"total_contact_groups":6},"final_pose_error":0.07882,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49067,-0.15448,0.02499],"final_tcp_position":[0.49901,-0.11981,0.1265],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":29.35178,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":479.0,"n_steps_budget":960.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5376,-0.02331,0.16499],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":761.0,"n_steps_budget":810.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3044.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.57109,0.06225,0.02598],"tcp_start":[0.5376,-0.02331,0.16499],"tcp_to_object_dist_end":0.0918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49214,-0.15284,0.02461],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.00837,"object_to_goal_dist_start":0.13211,"object_z_max":0.0255,"peak_contact_force":13.69254,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2946.0,"raw_peak_contact_force":22.09276,"subtask_id":"push_to_goal","tcp_end":[0.50632,-0.11835,0.02021],"tcp_start":[0.57109,0.06225,0.02598],"tcp_to_object_dist_end":0.03755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49067,-0.15448,0.02499],"object_pos_start":[0.49214,-0.15284,0.02461],"object_to_goal_dist_end":0.01035,"object_to_goal_dist_start":0.00837,"object_z_max":0.02516,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3975.0,"raw_peak_contact_force":29.35178,"tcp_end":[0.49901,-0.11981,0.1265],"tcp_start":[0.50632,-0.11835,0.02021],"tcp_to_object_dist_end":0.10759,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47826,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14875,"pre_contact_1.align_speed":0.12637,"pre_contact_1.pre_push_offset":0.08787,"push_1.push_speed":0.03945,"push_1.push_tolerance":0.0193,"retract_1.retract_height":0.17192,"retract_1.speed":0.14074},"optimized_scores":{"best_composite_score":0.48446,"best_fitness_score":0.89446,"best_task_score":0.9065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":558.0,"contact_point_centroid":[0.53551,-0.06723,0.02043],"force_p95":14.85271,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.9322,"mean_force":4.32489,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53804,-0.05562,0.01985]},{"body_a":"world","body_b":"push_box","contact_count":2321.0,"contact_point_centroid":[0.53323,-0.07448,-4e-05],"force_p95":5.04702,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.64541,"mean_force":1.33392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54992,-0.03003,0.02016]},{"body_a":"world","body_b":"push_box","contact_count":2997.0,"contact_point_centroid":[0.48909,-0.15475,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90182,"mean_force":0.24674,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50111,-0.1225,0.10064]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52233,-0.01567,0.23916]},{"body_a":"world","body_b":"push_box","contact_count":3392.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.56471,0.00359,0.10132]}],"total_contact_groups":5},"final_pose_error":0.01421,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4891,-0.15477,0.02499],"final_tcp_position":[0.49766,-0.14497,0.18384],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":16.9322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":900.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54696,-0.03191,0.1792],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":900.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3392.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.58577,0.04035,0.0256],"tcp_start":[0.54696,-0.03191,0.1792],"tcp_to_object_dist_end":0.08157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48941,-0.15401,0.02507],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.01132,"object_to_goal_dist_start":0.12728,"object_z_max":0.02538,"peak_contact_force":0.74906,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2879.0,"raw_peak_contact_force":16.9322,"subtask_id":"push_to_goal","tcp_end":[0.50834,-0.12164,0.02006],"tcp_start":[0.58577,0.04035,0.0256],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.4891,-0.15477,0.02499],"object_pos_start":[0.48941,-0.15401,0.02507],"object_to_goal_dist_end":0.0119,"object_to_goal_dist_start":0.01132,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2997.0,"raw_peak_contact_force":0.90182,"tcp_end":[0.49766,-0.14497,0.18384],"tcp_start":[0.50834,-0.12164,0.02006],"tcp_to_object_dist_end":0.15938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```