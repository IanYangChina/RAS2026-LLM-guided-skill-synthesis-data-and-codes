## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | -0.1966 | 0.21 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.1495 | 0.42 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.0702 | 0.43 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | -0.0416 | 0.21 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.1391 | 0.41 | ❌ rejected |

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

- Task name: grasp_place
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=-0.197) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_to_object
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_object_held
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_object_held, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.05]

## Design Metrics

- **Composite score**: -0.197
- **task_score** (E): 0.208
- **fitness_score**: 0.277  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2035 |
| descend_to_grasp | 0.33 | 1.00 | 0.0164 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.2081 |
| transport_to_goal | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.101) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 0.33 / step_budget | (0.506, 0.002, 0.101)→(0.517, 0.008, 0.091) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 141.316 | 0.041 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.009, 0.058)→(0.506, 0.009, 0.058) | (0.511, 0.002, 0.026)→(0.510, 0.003, 0.026) | 0.246→0.246 | 1.00 / 19.333 | 3250.364 | 4.330 |
| lift | lift | 1.00 / step_budget | (0.506, 0.009, 0.058)→(0.504, 0.008, 0.266) | (0.510, 0.003, 0.026)→(0.498, 0.019, 0.023) | 0.246→0.243 | 1.00 / 8.333 | 3249.805 | 1.395 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.504, 0.008, 0.266)→(0.504, 0.008, 0.266) | (0.498, 0.019, 0.023)→(0.498, 0.019, 0.023) | 0.243→0.243 | 1.00 / 8.000 | 3249.730 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.140
- phase_score: 0.195
- phase_breakdown.reach_object_score: 0.641
- phase_breakdown.reach_goal_score: 0.003
- grasp_place_fitness: 0.261

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.311
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.295
- **Median Q (composite search score)**: -0.229
- **K-run variance**: 0.0074
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.375


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47143,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05856,"approach_to_object.approach_speed":0.13036,"descend_to_grasp.descend_force_threshold":5.16872,"descend_to_grasp.descend_speed":0.04305,"descend_to_grasp.descend_target_z":0.01061,"grasp.grasp_duration":0.59052,"lift.lift_height":0.24042,"lift.lift_speed":0.18956,"transport_to_goal.transport_speed":0.2532},"optimized_scores":{"best_composite_score":-0.07886,"best_fitness_score":0.26114,"best_task_score":0.13988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":7093.0,"contact_point_centroid":[0.48241,-0.04286,-0.00351],"force_p95":2.25327,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12.74481,"mean_force":1.55664,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47548,-0.00207,-0.00125]},{"body_a":"world","body_b":"right_finger","contact_count":6906.0,"contact_point_centroid":[0.46727,0.03862,-0.00296],"force_p95":1.99586,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11.95197,"mean_force":1.31568,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47547,-0.00208,-0.00126]},{"body_a":"world","body_b":"left_finger","contact_count":317.0,"contact_point_centroid":[0.48192,-0.0414,-0.00239],"force_p95":3.31864,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.93879,"mean_force":1.01576,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47465,-0.00221,0.00212]},{"body_a":"world","body_b":"right_finger","contact_count":270.0,"contact_point_centroid":[0.4678,0.03723,-0.00212],"force_p95":2.75382,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.26072,"mean_force":0.79408,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47472,-0.0022,0.00168]},{"body_a":"world","body_b":"grasp_target","contact_count":2094.0,"contact_point_centroid":[0.42241,0.02152,-0.00217],"force_p95":0.3354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13763,"mean_force":0.14182,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47174,-0.0022,0.12082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.45971,0.00529,0.03639],"force_p95":0.5812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58746,"mean_force":0.4315,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47131,-0.0022,0.0393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":566.0,"contact_point_centroid":[0.47295,-0.03576,0.00973],"force_p95":0.18566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35546,"mean_force":0.06943,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47347,-0.00225,0.01095]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45648,-0.0235,-0.0022],"force_p95":0.2052,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34034,"mean_force":0.14576,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47787,-0.0022,0.00174]},{"body_a":"grasp_target","body_b":"hand","contact_count":505.0,"contact_point_centroid":[0.474,-0.00486,0.04327],"force_p95":0.13592,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33093,"mean_force":0.06054,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47542,-0.00207,-0.00128]},{"body_a":"grasp_target","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.47285,-0.00247,0.04356],"force_p95":0.25643,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25647,"mean_force":0.18829,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47516,-0.00212,-0.00104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4588.0,"contact_point_centroid":[0.47586,-0.04212,3e-05],"force_p95":0.08439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21728,"mean_force":0.02935,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47542,-0.00207,-0.00128]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.47991,-0.01125,0.20514]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.42029,0.02548,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47245,-0.0022,0.21936]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46989,-0.01469,0.0961]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1623.0,"contact_point_centroid":[0.47242,-0.00211,0.15214],"force_p95":0.01184,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01053,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47168,-0.0022,0.15004]},{"body_a":"left_finger","body_b":"right_finger","contact_count":13.0,"contact_point_centroid":[0.47354,-0.00203,0.22051],"force_p95":0.01067,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01067,"mean_force":0.01017,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47245,-0.0022,0.21937]}],"total_contact_groups":16},"final_pose_error":0.28321,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.42029,0.02548,0.01602],"final_tcp_position":[0.47257,-0.00219,0.21953],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":272985.52157,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46003,-0.02314,0.10802],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":423.70219,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":96.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.49307,-0.00377,0.07716],"tcp_start":[0.46003,-0.02314,0.10802],"tcp_to_object_dist_end":0.06568,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45518,-0.0238,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30371,"object_to_goal_dist_start":0.30365,"object_z_max":0.02607,"peak_contact_force":2.25323,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21292.0,"raw_peak_contact_force":12.74481,"tcp_end":[0.47523,-0.00209,-0.0015],"tcp_start":[0.47524,-0.00209,-0.0015],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":600.0,"n_steps_budget":810.0,"object_pos_end":[0.42029,0.02548,0.01602],"object_pos_start":[0.455,-0.02319,0.02585],"object_to_goal_dist_end":0.29504,"object_to_goal_dist_start":0.30333,"object_z_max":0.03091,"peak_contact_force":9749.16954,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4882.0,"raw_peak_contact_force":3.93879,"tcp_end":[0.47237,-0.00221,0.21922],"tcp_start":[0.47523,-0.00209,-0.0015],"tcp_to_object_dist_end":0.21159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.42029,0.02548,0.01602],"object_pos_start":[0.42029,0.02548,0.01602],"object_to_goal_dist_end":0.29504,"object_to_goal_dist_start":0.29504,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.47257,-0.00219,0.21953],"tcp_start":[0.47255,-0.0022,0.21948],"tcp_to_object_dist_end":0.21194,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":43.0,"average_failure_rate":0.34127,"average_mean_iterations":70.93651,"average_solve_count":126.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05022,"approach_to_object.approach_speed":0.21715,"descend_to_grasp.descend_force_threshold":6.1153,"descend_to_grasp.descend_speed":0.02591,"descend_to_grasp.descend_target_z":0.01903,"grasp.grasp_duration":0.68663,"lift.lift_height":0.27958,"lift.lift_speed":0.09841,"transport_to_goal.transport_speed":0.27008},"optimized_scores":{"best_composite_score":-0.28163,"best_fitness_score":0.25837,"best_task_score":0.18872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51681,0.00047,0.19965]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52854,0.00083,0.08819]},{"body_a":"world","body_b":"grasp_target","contact_count":3428.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52457,0.00076,0.21614]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52575,0.00076,0.34679]},{"body_a":"left_finger","body_b":"right_finger","contact_count":758.0,"contact_point_centroid":[0.52773,0.00081,0.08917],"force_p95":0.01316,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01086,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52761,0.00081,0.08701]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3660.0,"contact_point_centroid":[0.52483,0.00076,0.21855],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01299,"mean_force":0.01044,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52457,0.00076,0.21625]},{"body_a":"left_finger","body_b":"right_finger","contact_count":14.0,"contact_point_centroid":[0.52611,0.00076,0.35008],"force_p95":0.01075,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01075,"mean_force":0.00981,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52575,0.00076,0.34679]}],"total_contact_groups":7},"final_pose_error":0.25273,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54431,0.00113,0.02602],"final_tcp_position":[0.52573,0.00076,0.34688],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273017.19681,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53571,0.00095,0.09776],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.53571,0.00095,0.09776],"tcp_start":[0.53571,0.00095,0.09776],"tcp_to_object_dist_end":0.07226,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":9748.71605,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2958.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52761,0.00081,0.08701],"tcp_start":[0.52761,0.00081,0.08701],"tcp_to_object_dist_end":0.06323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7088.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52576,0.00076,0.34669],"tcp_start":[0.52761,0.00081,0.08701],"tcp_to_object_dist_end":0.32121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":9748.94392,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.52573,0.00076,0.34688],"tcp_start":[0.52572,0.00076,0.34686],"tcp_to_object_dist_end":0.3214,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":50.0,"average_failure_rate":0.49505,"average_mean_iterations":101.33663,"average_solve_count":101.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05006,"approach_to_object.approach_speed":0.16899,"descend_to_grasp.descend_force_threshold":3.58707,"descend_to_grasp.descend_speed":0.02293,"descend_to_grasp.descend_target_z":0.01762,"grasp.grasp_duration":0.627,"lift.lift_height":0.16345,"lift.lift_speed":0.17521,"transport_to_goal.transport_speed":0.20226},"optimized_scores":{"best_composite_score":-0.22925,"best_fitness_score":0.31075,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51078,0.01325,0.19995]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51637,0.02688,0.08893]},{"body_a":"world","body_b":"grasp_target","contact_count":1672.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51232,0.02661,0.15898]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51267,0.02663,0.23185]},{"body_a":"left_finger","body_b":"right_finger","contact_count":764.0,"contact_point_centroid":[0.51566,0.02682,0.09013],"force_p95":0.01263,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.017,"mean_force":0.01079,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51546,0.02682,0.0878]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1783.0,"contact_point_centroid":[0.51256,0.02662,0.16123],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01045,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51232,0.02661,0.15902]},{"body_a":"left_finger","body_b":"right_finger","contact_count":13.0,"contact_point_centroid":[0.51348,0.02664,0.23322],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51267,0.02663,0.23185]}],"total_contact_groups":7},"final_pose_error":0.21521,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.5128,0.02664,0.23202],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273010.78989,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52346,0.02721,0.09813],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52346,0.02721,0.09813],"tcp_start":[0.52346,0.02721,0.09813],"tcp_to_object_dist_end":0.07254,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2964.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51546,0.02682,0.0878],"tcp_start":[0.51546,0.02682,0.0878],"tcp_to_object_dist_end":0.06371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3455.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51259,0.02663,0.2317],"tcp_start":[0.51546,0.02682,0.0878],"tcp_to_object_dist_end":0.2065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5128,0.02664,0.23202],"tcp_start":[0.51277,0.02664,0.23197],"tcp_to_object_dist_end":0.2068,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```