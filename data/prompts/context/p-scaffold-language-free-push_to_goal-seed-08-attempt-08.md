## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4121 | 0.82 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1877 | 0.00 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3638 | 0.00 | ❌ rejected |
| 5 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2261 | 0.81 | ❌ rejected |
| 4 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3922 | 0.81 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.412) — your mutation base

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

- **Composite score**: 0.412
- **task_score** (E): 0.821
- **fitness_score**: 0.822  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1370 |
| pre_contact_1 | 1.00 | 1.00 | 0.1619 |
| push_1 | 1.00 | 1.00 | 0.1624 |
| retract_1 | 0.33 | 1.00 | 0.1107 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.001, 0.174) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| pre_contact_1 | align | 1.00 / step_budget | (0.521, -0.001, 0.174)→(0.539, 0.059, 0.026) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 66.855 |
| push_1 | push | 1.00 / step_budget | (0.539, 0.059, 0.026)→(0.498, -0.094, 0.022) | (0.526, -0.001, 0.025)→(0.509, -0.118, 0.027) | 0.156→0.035 | 1.00 / 3.000 | 1.981 | 20.853 |
| retract_1 | retract | 0.33 / step_budget | (0.498, -0.094, 0.022)→(0.494, -0.120, 0.128) | (0.509, -0.118, 0.027)→(0.507, -0.119, 0.025) | 0.035→0.035 | 1.00 / 4.000 | 0.245 | 9.728 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.744
- goal_progress: 0.967
- terminal_score: 0.967
- phase_score: 0.914
- phase_breakdown.push_to_goal_score: 0.976
- phase_breakdown.reach_object_score: 0.771

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.936
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.967
- **Median Q (composite search score)**: 0.516
- **K-run variance**: 0.0237
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.232


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48148,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14606,"pre_contact_1.pre_push_offset":0.04394,"push_1.push_distance":0.16391,"push_1.push_speed":0.0562,"push_1.push_tolerance":0.0125,"retract_1.retract_height":0.17389,"retract_1.speed":0.06822},"optimized_scores":{"best_composite_score":0.19434,"best_fitness_score":0.60434,"best_task_score":0.54929},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.48043,0.08442,0.0486],"force_p95":154.9411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.07572,"mean_force":90.56556,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.4737,0.0936,0.04913]},{"body_a":"world","body_b":"push_box","contact_count":3406.0,"contact_point_centroid":[0.47928,0.05894,-3e-05],"force_p95":0.47734,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.01971,"mean_force":1.88041,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.47386,0.07561,0.10238]},{"body_a":"attachment","body_b":"push_box","contact_count":757.0,"contact_point_centroid":[0.48766,0.00982,0.04731],"force_p95":15.72654,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.24482,"mean_force":4.4544,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47574,0.01827,0.02356]},{"body_a":"world","body_b":"push_box","contact_count":1339.0,"contact_point_centroid":[0.51544,-0.01578,-5e-05],"force_p95":11.92416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.519,"mean_force":4.11786,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47583,0.01959,0.0238]},{"body_a":"push_box","body_b":"link7","contact_count":192.0,"contact_point_centroid":[0.51323,-0.01508,0.05726],"force_p95":12.71079,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.62115,"mean_force":8.02165,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48002,-0.02731,0.02347]},{"body_a":"world","body_b":"push_box","contact_count":3470.0,"contact_point_centroid":[0.52039,-0.05729,-1e-05],"force_p95":0.46148,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85997,"mean_force":0.2746,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48238,-0.07316,0.08489]},{"body_a":"attachment","body_b":"push_box","contact_count":154.0,"contact_point_centroid":[0.49565,-0.05936,0.05384],"force_p95":0.67764,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.85036,"mean_force":0.53694,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47986,-0.0586,0.03865]},{"body_a":"world","body_b":"push_box","contact_count":1704.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48874,0.02557,0.23955]}],"total_contact_groups":8},"final_pose_error":0.08869,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51659,-0.05704,0.02499],"final_tcp_position":[0.48652,-0.09423,0.13126],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":200.07572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47847,0.05261,0.1789],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.48028,0.0583,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20923,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24522,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3467.0,"raw_peak_contact_force":200.07572,"tcp_end":[0.47166,0.09951,0.02757],"tcp_start":[0.47847,0.05261,0.1789],"tcp_to_object_dist_end":0.04218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.5221,-0.05726,0.02963],"object_pos_start":[0.48028,0.0583,0.02499],"object_to_goal_dist_end":0.09545,"object_to_goal_dist_start":0.20923,"object_z_max":0.02974,"peak_contact_force":1.53023,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2288.0,"raw_peak_contact_force":23.24482,"subtask_id":"push_to_goal","tcp_end":[0.48258,-0.05587,0.02327],"tcp_start":[0.47166,0.09951,0.02757],"tcp_to_object_dist_end":0.04005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51659,-0.05704,0.02499],"object_pos_start":[0.5221,-0.05726,0.02963],"object_to_goal_dist_end":0.09443,"object_to_goal_dist_start":0.09545,"object_z_max":0.02963,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3624.0,"raw_peak_contact_force":0.85997,"tcp_end":[0.48652,-0.09423,0.13126],"tcp_start":[0.48258,-0.05587,0.02327],"tcp_to_object_dist_end":0.11654,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49724,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14785,"pre_contact_1.pre_push_offset":0.07986,"push_1.push_distance":0.17457,"push_1.push_speed":0.04482,"push_1.push_tolerance":0.02084,"retract_1.retract_height":0.13118,"retract_1.speed":0.07662},"optimized_scores":{"best_composite_score":0.51636,"best_fitness_score":0.92636,"best_task_score":0.94794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":644.0,"contact_point_centroid":[0.52594,-0.06191,0.02241],"force_p95":16.42459,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.13066,"mean_force":4.1555,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52671,-0.05002,0.02161]},{"body_a":"world","body_b":"push_box","contact_count":2053.0,"contact_point_centroid":[0.53086,-0.06686,-5e-05],"force_p95":6.31381,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.93811,"mean_force":1.57379,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53782,-0.01992,0.02189]},{"body_a":"world","body_b":"push_box","contact_count":3970.0,"contact_point_centroid":[0.50672,-0.14872,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.29222,"mean_force":0.24804,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49905,-0.11913,0.0841]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.5117,-0.12254,0.0502],"force_p95":2.85493,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.99865,"mean_force":1.56148,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50507,-0.11055,0.02182]},{"body_a":"world","body_b":"push_box","contact_count":1752.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51755,-0.01132,0.23945]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.54982,0.01101,0.10102]}],"total_contact_groups":6},"final_pose_error":0.01545,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50677,-0.14879,0.02499],"final_tcp_position":[0.49707,-0.14301,0.14272],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":21.13066,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":870.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.53742,-0.02315,0.1793],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.56516,0.04548,0.02681],"tcp_start":[0.53742,-0.02315,0.1793],"tcp_to_object_dist_end":0.07404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.50722,-0.14736,0.0251],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.00769,"object_to_goal_dist_start":0.13211,"object_z_max":0.02545,"peak_contact_force":0.96095,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2697.0,"raw_peak_contact_force":21.13066,"subtask_id":"push_to_goal","tcp_end":[0.5051,-0.11049,0.02184],"tcp_start":[0.56516,0.04548,0.02681],"tcp_to_object_dist_end":0.03708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50677,-0.14879,0.02499],"object_pos_start":[0.50722,-0.14736,0.0251],"object_to_goal_dist_end":0.00688,"object_to_goal_dist_start":0.00769,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3972.0,"raw_peak_contact_force":3.29222,"tcp_end":[0.49707,-0.14301,0.14272],"tcp_start":[0.5051,-0.11049,0.02184],"tcp_to_object_dist_end":0.11827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31818,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13414,"pre_contact_1.pre_push_offset":0.07682,"push_1.push_distance":0.17154,"push_1.push_speed":0.05846,"push_1.push_tolerance":0.02718,"retract_1.retract_height":0.14611,"retract_1.speed":0.04154},"optimized_scores":{"best_composite_score":0.52553,"best_fitness_score":0.93553,"best_task_score":0.96718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50508,-0.12698,0.0199],"force_p95":23.48371,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.03201,"mean_force":12.20579,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50723,-0.1152,0.01943]},{"body_a":"attachment","body_b":"push_box","contact_count":566.0,"contact_point_centroid":[0.53414,-0.06647,0.01947],"force_p95":15.90165,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.18253,"mean_force":3.90321,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53603,-0.0547,0.01902]},{"body_a":"world","body_b":"push_box","contact_count":1897.0,"contact_point_centroid":[0.53435,-0.076,-3e-05],"force_p95":5.66194,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.66913,"mean_force":1.45146,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54737,-0.03175,0.01936]},{"body_a":"world","body_b":"push_box","contact_count":3985.0,"contact_point_centroid":[0.49622,-0.15179,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.84413,"mean_force":0.25507,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50123,-0.11417,0.06521]},{"body_a":"world","body_b":"push_box","contact_count":2036.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52245,-0.0158,0.23203]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"pre_contact_1","phase_type":"align","tcp_position_centroid":[0.56282,-0.00069,0.09258]}],"total_contact_groups":6},"final_pose_error":0.06663,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49621,-0.15176,0.02499],"final_tcp_position":[0.4992,-0.12155,0.11087],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":25.03201,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":990.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54725,-0.03218,0.16477],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":990.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"pre_contact_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.58142,0.03117,0.02443],"tcp_start":[0.54725,-0.03218,0.16477],"tcp_to_object_dist_end":0.07143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":887.0,"n_steps_budget":1000.0,"object_pos_end":[0.49703,-0.15078,0.02485],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.00308,"object_to_goal_dist_start":0.12728,"object_z_max":0.02534,"peak_contact_force":3.45183,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2463.0,"raw_peak_contact_force":18.18253,"subtask_id":"push_to_goal","tcp_end":[0.50728,-0.1151,0.01945],"tcp_start":[0.58142,0.03117,0.02443],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49621,-0.15176,0.02499],"object_pos_start":[0.49703,-0.15078,0.02485],"object_to_goal_dist_end":0.00418,"object_to_goal_dist_start":0.00308,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":25.03201,"tcp_end":[0.4992,-0.12155,0.11087],"tcp_start":[0.50728,-0.1151,0.01945],"tcp_to_object_dist_end":0.09109,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```