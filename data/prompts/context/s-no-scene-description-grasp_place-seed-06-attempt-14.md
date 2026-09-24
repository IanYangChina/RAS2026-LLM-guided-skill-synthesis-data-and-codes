## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2398 | 0.32 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 15 | -0.1797 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0007 | 0.28 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2044 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0518 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.240) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.01
  weight: 0.1
- id: reach_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: reach_place
  offset:
  - 0.0
  - 0.0
  - 0.01
  weight: 0.4
- id: reach_retract
  offset:
  - 0.0
  - 0.0
  - 0.3
  weight: 0.2
phases:
- id: approach_pre_grasp
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.arc_height
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
  subtask_id: reach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.03
      - 0.0
      default: -0.01
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_object
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
    orientation:
      mode: keep_current
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_success_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_grasp
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_lift
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
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
  guards:
  - id: object_grasped_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.02
    on_failure: abort
  subtask_id: reach_place
- id: place_object
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: place_force_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_retract

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_success_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_grasped_guard, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.02
- **place_object** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=place_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=tcp, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.240
- **task_score** (E): 0.323
- **fitness_score**: 0.640  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_grasp | 1.00 | 1.00 | 0.1227 |
| descend_to_grasp | 1.00 | 1.00 | 0.1543 |
| grasp_object | 1.00 | 1.00 | 0.0116 |
| lift_object | 1.00 | 1.00 | 0.1713 |
| transport_to_goal | 0.00 | 1.00 | 0.1020 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_grasp | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.031, 0.186) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 8.437 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.031, 0.186)→(0.495, 0.024, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.495, 0.024, 0.032)→(0.487, 0.024, 0.023) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.136 | 0.203 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.024, 0.023)→(0.495, 0.024, 0.195) | (0.500, 0.024, 0.026)→(0.510, 0.024, 0.191) | 0.272→0.202 | 1.00 / 34.333 | 0.087 | 0.695 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.495, 0.024, 0.195)→(0.513, 0.063, 0.286) | (0.510, 0.024, 0.191)→(0.529, 0.061, 0.264) | 0.202→0.170 | 1.00 / 10.000 | 0.004 | 0.276 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.345
- phase_score: 0.156
- phase_breakdown.reach_retract_score: 0.000
- phase_breakdown.reach_lift_score: 0.203
- phase_breakdown.reach_pre_grasp_score: 0.310
- phase_breakdown.reach_place_score: 0.032
- phase_breakdown.reach_grasp_score: 0.710
- grasp_place_fitness: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.652
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.345
- **Median Q (composite search score)**: -0.239
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.303


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21887,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.17809,"approach_pre_grasp.speed":0.04759,"descend_to_grasp.descend_z":-0.01861,"descend_to_grasp.speed":0.06918,"grasp_object.grasp_duration":0.39496,"lift_object.lift_height":0.26691,"lift_object.speed":0.0403,"place_object.place_z_offset":0.0289,"place_object.speed":0.02804,"release_object.release_duration":0.13424,"retract_after_place.retract_z":0.36058,"retract_after_place.speed":0.08194,"transport_to_goal.arc_height":0.0521,"transport_to_goal.speed":0.07372},"optimized_scores":{"best_composite_score":-0.25263,"best_fitness_score":0.62737,"best_task_score":0.30053},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.49975,-0.01491,-0.00141],"force_p95":0.70489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73626,"mean_force":0.27071,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48981,-0.01522,0.02057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6749.0,"contact_point_centroid":[0.51168,-0.00989,0.32654],"force_p95":0.16661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34413,"mean_force":0.0787,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5088,0.00872,0.32688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18012.0,"contact_point_centroid":[0.49345,0.00407,0.14838],"force_p95":0.07377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2887,"mean_force":0.05114,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49353,-0.0151,0.14648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5956.0,"contact_point_centroid":[0.51144,0.02685,0.32626],"force_p95":0.17005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28297,"mean_force":0.0827,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5085,0.00802,0.326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18655.0,"contact_point_centroid":[0.49338,-0.03424,0.148],"force_p95":0.0724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27534,"mean_force":0.04975,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49353,-0.0151,0.14633]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01546,-0.00204],"force_p95":0.13448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17902,"mean_force":0.12615,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49197,-0.01524,0.02074]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49905,0.00649,0.24109]},{"body_a":"world","body_b":"grasp_target","contact_count":3852.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49783,-0.01185,0.09896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4096.0,"contact_point_centroid":[0.49127,0.00397,0.02226],"force_p95":0.07648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11157,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49077,-0.01523,0.0195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.49132,-0.03432,0.02135],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09369,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49077,-0.01523,0.0195]}],"total_contact_groups":10},"final_pose_error":0.14848,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54432,0.05362,0.36123],"final_tcp_position":[0.5313,0.05956,0.39715],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":25.0659,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49991,-0.00788,0.18449],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49886,-0.01532,0.02793],"tcp_start":[0.49991,-0.00788,0.18449],"tcp_to_object_dist_end":0.00532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50366,-0.01508,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13133,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.17902,"subtask_id":"reach_grasp","tcp_end":[0.49074,-0.01523,0.01947],"tcp_start":[0.49886,-0.01532,0.02793],"tcp_to_object_dist_end":0.01441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.51363,-0.01498,0.27094],"object_pos_start":[0.50366,-0.01508,0.02586],"object_to_goal_dist_end":0.21649,"object_to_goal_dist_start":0.31201,"object_z_max":0.27068,"peak_contact_force":0.07129,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36752.0,"raw_peak_contact_force":0.73626,"subtask_id":"reach_lift","tcp_end":[0.50039,-0.01505,0.27304],"tcp_start":[0.49074,-0.01523,0.01947],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.54432,0.05362,0.36123],"object_pos_start":[0.51363,-0.01498,0.27094],"object_to_goal_dist_end":0.18033,"object_to_goal_dist_start":0.21649,"object_z_max":0.36857,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12705.0,"raw_peak_contact_force":0.34413,"subtask_id":"reach_place","tcp_end":[0.5313,0.05956,0.39715],"tcp_start":[0.50039,-0.01505,0.27304],"tcp_to_object_dist_end":0.03866,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11905,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.10413,"approach_pre_grasp.speed":0.04824,"descend_to_grasp.descend_z":-0.01484,"descend_to_grasp.speed":0.05384,"grasp_object.grasp_duration":0.50336,"lift_object.lift_height":0.15355,"lift_object.speed":0.06678,"place_object.place_z_offset":-0.00308,"place_object.speed":0.03374,"release_object.release_duration":0.27492,"retract_after_place.retract_z":0.22084,"retract_after_place.speed":0.05402,"transport_to_goal.arc_height":0.15611,"transport_to_goal.speed":0.0542},"optimized_scores":{"best_composite_score":-0.23904,"best_fitness_score":0.64096,"best_task_score":0.32481},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.50973,0.03848,-0.00141],"force_p95":0.63341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73583,"mean_force":0.17795,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49832,0.03878,0.02371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8316.0,"contact_point_centroid":[0.50259,0.05751,0.08517],"force_p95":0.10514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30829,"mean_force":0.06116,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50094,0.03851,0.08347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7988.0,"contact_point_centroid":[0.50319,0.01959,0.0888],"force_p95":0.10119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30623,"mean_force":0.06282,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50122,0.03851,0.08702]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51252,0.03944,-0.00207],"force_p95":0.14442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22253,"mean_force":0.12869,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03899,0.02382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.51258,0.01993,0.16234],"force_p95":0.13013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16835,"mean_force":0.09671,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50747,0.03844,0.16044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.51237,0.05712,0.16176],"force_p95":0.13899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15961,"mean_force":0.09952,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50747,0.03844,0.16046]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.50167,0.04039,0.25294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.49991,0.0197,0.02533],"force_p95":0.07847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12506,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49934,0.03889,0.02253]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50617,0.04272,0.09951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4940.0,"contact_point_centroid":[0.4999,0.05801,0.02435],"force_p95":0.07071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09256,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49935,0.03889,0.02254]}],"total_contact_groups":10},"final_pose_error":0.25786,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52592,0.03843,0.15688],"final_tcp_position":[0.50702,0.03826,0.16081],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.73583,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50782,0.04678,0.18508],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50739,0.03956,0.03121],"tcp_start":[0.50782,0.04678,0.18508],"tcp_to_object_dist_end":0.00729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51236,0.03878,0.02576],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21304,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13882,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.22253,"subtask_id":"reach_grasp","tcp_end":[0.49931,0.03888,0.0225],"tcp_start":[0.50739,0.03956,0.03121],"tcp_to_object_dist_end":0.01345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,0.03863,0.15642],"object_pos_start":[0.51236,0.03878,0.02576],"object_to_goal_dist_end":0.16805,"object_to_goal_dist_start":0.21304,"object_z_max":0.15617,"peak_contact_force":0.10879,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16386.0,"raw_peak_contact_force":0.73583,"subtask_id":"reach_lift","tcp_end":[0.50748,0.03847,0.16017],"tcp_start":[0.49931,0.03888,0.0225],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.52592,0.03843,0.15688],"object_pos_start":[0.52665,0.03863,0.15642],"object_to_goal_dist_end":0.16868,"object_to_goal_dist_start":0.16805,"object_z_max":0.15679,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":140.0,"raw_peak_contact_force":0.16835,"subtask_id":"reach_place","tcp_end":[0.50702,0.03826,0.16081],"tcp_start":[0.50748,0.03847,0.16017],"tcp_to_object_dist_end":0.01931,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93377,"average_solve_count":302.0,"average_success_count":302.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_grasp.arc_height":0.12508,"approach_pre_grasp.speed":0.03381,"descend_to_grasp.descend_z":-0.01848,"descend_to_grasp.speed":0.02517,"grasp_object.grasp_duration":0.63009,"lift_object.lift_height":0.14386,"lift_object.speed":0.04814,"place_object.place_z_offset":0.00105,"place_object.speed":0.04253,"release_object.release_duration":0.08544,"retract_after_place.retract_z":0.30264,"retract_after_place.speed":0.08038,"transport_to_goal.arc_height":0.05408,"transport_to_goal.speed":0.0722},"optimized_scores":{"best_composite_score":-0.22766,"best_fitness_score":0.65234,"best_task_score":0.34495},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47946,0.04771,-0.00143],"force_p95":0.561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61409,"mean_force":0.18122,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46934,0.04782,0.02941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7517.0,"contact_point_centroid":[0.48544,0.04105,0.21512],"force_p95":0.12775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31546,"mean_force":0.0716,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48212,0.05971,0.21423]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6700.0,"contact_point_centroid":[0.48549,0.07896,0.21667],"force_p95":0.13553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29446,"mean_force":0.07904,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48229,0.06002,0.21542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8671.0,"contact_point_centroid":[0.47206,0.06675,0.08843],"force_p95":0.075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2934,"mean_force":0.05135,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47216,0.0476,0.08647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8259.0,"contact_point_centroid":[0.4722,0.02844,0.08908],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26416,"mean_force":0.05301,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47218,0.0476,0.0866]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04855,-0.00206],"force_p95":0.14133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20745,"mean_force":0.12777,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47139,0.04805,0.02947]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_pre_grasp","phase_type":"approach","tcp_position_centroid":[0.49142,0.04033,0.25491]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47795,0.05121,0.10778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5051.0,"contact_point_centroid":[0.47008,0.02871,0.03128],"force_p95":0.0671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09964,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04794,0.02832]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5425.0,"contact_point_centroid":[0.4699,0.06722,0.03068],"force_p95":0.06643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08252,"mean_force":0.04124,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04794,0.02833]}],"total_contact_groups":10},"final_pose_error":0.20718,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51709,0.08978,0.27466],"final_tcp_position":[0.50009,0.09036,0.29989],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.61409,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_pre_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48121,0.05422,0.18822],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47797,0.04872,0.03615],"tcp_start":[0.48121,0.05422,0.18822],"tcp_to_object_dist_end":0.01118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04801,0.02578],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29064,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13828,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12276.0,"raw_peak_contact_force":0.20745,"subtask_id":"reach_grasp","tcp_end":[0.47023,0.04794,0.02829],"tcp_start":[0.47797,0.04872,0.03615],"tcp_to_object_dist_end":0.0126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.48911,0.0477,0.14453],"object_pos_start":[0.48258,0.04801,0.02578],"object_to_goal_dist_end":0.22093,"object_to_goal_dist_start":0.29064,"object_z_max":0.14426,"peak_contact_force":0.0797,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17014.0,"raw_peak_contact_force":0.61409,"subtask_id":"reach_lift","tcp_end":[0.47776,0.04763,0.1504],"tcp_start":[0.47023,0.04794,0.02829],"tcp_to_object_dist_end":0.01278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.51709,0.08978,0.27466],"object_pos_start":[0.48911,0.0477,0.14453],"object_to_goal_dist_end":0.15965,"object_to_goal_dist_start":0.22093,"object_z_max":0.27663,"peak_contact_force":0.01185,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14217.0,"raw_peak_contact_force":0.31546,"subtask_id":"reach_place","tcp_end":[0.50009,0.09036,0.29989],"tcp_start":[0.47776,0.04763,0.1504],"tcp_to_object_dist_end":0.03043,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```