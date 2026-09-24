## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0632 | 0.27 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1491 | 0.13 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2072 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0140 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0216 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.063) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  target_entity: object
  weight: 0.1
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.15
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.15
- id: final_placement
  target_entity: object
  weight: 0.4
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    force_limit:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 15.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
  subtask_id: grasp_contact
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: final_placement
- id: release
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
    release_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_guard, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.0
  - retries: max_attempts=1, strategy=repeat
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.063
- **task_score** (E): 0.270
- **fitness_score**: 0.613  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0672 |
| descend_to_grasp | 1.00 | 1.00 | 0.2127 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1507 |
| approach_goal | 0.00 | 1.00 | 0.0769 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.000, 0.247) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.000, 0.247)→(0.517, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.517, -0.001, 0.034)→(0.508, -0.001, 0.025) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.144 | 0.211 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.025)→(0.505, -0.001, 0.176) | (0.522, -0.001, 0.026)→(0.526, -0.001, 0.167) | 0.289→0.228 | 1.00 / 23.333 | 524.431 | 0.731 |
| approach_goal | approach | 0.00 / guard_failure | (0.505, -0.001, 0.176)→(0.517, 0.027, 0.245) | (0.526, -0.001, 0.167)→(0.530, 0.026, 0.220) | 0.228→0.201 | 1.00 / 6.667 | 0.003 | 0.278 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.349
- phase_score: 0.300
- phase_breakdown.lift_object_score: 0.475
- phase_breakdown.descend_to_grasp_score: 0.870
- phase_breakdown.approach_goal_score: 0.047
- phase_breakdown.approach_object_score: 0.674
- phase_breakdown.final_placement_score: 0.000
- grasp_place_fitness: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.652
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.349
- **Median Q (composite search score)**: 0.065
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31606,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.24307,"approach_goal.transport_speed":0.09806,"approach_object.approach_arc_height":0.15434,"approach_object.approach_speed":0.16333,"descend_to_grasp.descend_speed":0.03118,"descend_to_place.descend_place_speed":0.09856,"lift.lift_height":0.19382,"release.release_time":0.61876},"optimized_scores":{"best_composite_score":0.06537,"best_fitness_score":0.61537,"best_task_score":0.27007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.47942,0.04624,-0.00146],"force_p95":0.66639,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70285,"mean_force":0.16516,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46913,0.04686,0.02821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1254.0,"contact_point_centroid":[0.47346,0.03154,0.21565],"force_p95":0.19393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34814,"mean_force":0.11316,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46755,0.04983,0.21768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1185.0,"contact_point_centroid":[0.47334,0.06861,0.21648],"force_p95":0.19903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3209,"mean_force":0.11985,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46767,0.0501,0.21885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8200.0,"contact_point_centroid":[0.46946,0.06558,0.1017],"force_p95":0.11195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31865,"mean_force":0.06881,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46688,0.04664,0.09976]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8003.0,"contact_point_centroid":[0.46969,0.02777,0.1061],"force_p95":0.10864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29903,"mean_force":0.06998,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46688,0.04664,0.10395]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04842,-0.00216],"force_p95":0.16752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25432,"mean_force":0.1348,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47152,0.04711,0.02785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5001.0,"contact_point_centroid":[0.47018,0.02776,0.0296],"force_p95":0.07018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15203,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47039,0.047,0.02672]},{"body_a":"world","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.4827,0.04873,-0.00177],"force_p95":0.13794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12351,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49092,0.02148,0.27738]},{"body_a":"world","body_b":"grasp_target","contact_count":2920.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47963,0.04404,0.1397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5531.0,"contact_point_centroid":[0.46998,0.06635,0.02897],"force_p95":0.07051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08962,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4704,0.04701,0.02673]}],"total_contact_groups":10},"final_pose_error":0.22296,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48823,0.05679,0.21703],"final_tcp_position":[0.47093,0.05648,0.2428],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.70285,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":552.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48361,0.0405,0.24779],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":730.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2920.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_to_grasp","tcp_end":[0.47828,0.04778,0.03473],"tcp_start":[0.48361,0.0405,0.24779],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04716,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29138,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15997,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12332.0,"raw_peak_contact_force":0.25432,"tcp_end":[0.47036,0.047,0.02669],"tcp_start":[0.47828,0.04778,0.03473],"tcp_to_object_dist_end":0.01229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.48786,0.04702,0.19074],"object_pos_start":[0.48259,0.04716,0.02546],"object_to_goal_dist_end":0.20852,"object_to_goal_dist_start":0.29138,"object_z_max":0.19047,"peak_contact_force":0.08711,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16279.0,"raw_peak_contact_force":0.70285,"subtask_id":"lift_object","tcp_end":[0.4672,0.04667,0.20093],"tcp_start":[0.47036,0.047,0.02669],"tcp_to_object_dist_end":0.02304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.48823,0.05679,0.21703],"object_pos_start":[0.48786,0.04702,0.19074],"object_to_goal_dist_end":0.19636,"object_to_goal_dist_start":0.20852,"object_z_max":0.21918,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2439.0,"raw_peak_contact_force":0.34814,"subtask_id":"approach_goal","tcp_end":[0.47093,0.05648,0.2428],"tcp_start":[0.4672,0.04667,0.20093],"tcp_to_object_dist_end":0.03105,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57895,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.23192,"approach_goal.transport_speed":0.03031,"approach_object.approach_arc_height":0.28977,"approach_object.approach_speed":0.16548,"descend_to_grasp.descend_speed":0.06551,"descend_to_place.descend_place_speed":0.05432,"lift.lift_height":0.17382,"release.release_time":0.51572},"optimized_scores":{"best_composite_score":0.0223,"best_fitness_score":0.5723,"best_task_score":0.18946},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.53382,-0.02052,-0.00135],"force_p95":0.6966,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74064,"mean_force":0.1603,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52155,-0.02074,0.02557]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6794.0,"contact_point_centroid":[0.52245,-0.00183,0.09481],"force_p95":0.11502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.342,"mean_force":0.07762,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51896,-0.02068,0.09258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7353.0,"contact_point_centroid":[0.52248,-0.03942,0.09217],"force_p95":0.11237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31844,"mean_force":0.07289,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51897,-0.02068,0.09052]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1990.0,"contact_point_centroid":[0.52314,-0.03517,0.20126],"force_p95":0.17961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25599,"mean_force":0.11593,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51818,-0.01688,0.20391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1889.0,"contact_point_centroid":[0.523,0.00158,0.20231],"force_p95":0.1888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24655,"mean_force":0.11723,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51819,-0.01672,0.20485]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02111,-0.00205],"force_p95":0.1383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18223,"mean_force":0.12703,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52413,-0.02079,0.02567]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.53702,-0.02132,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12355,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51353,-0.00837,0.27519]},{"body_a":"world","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52779,-0.0187,0.13824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.52378,-0.00157,0.027],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1192,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02077,0.02428]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.52376,-0.03986,0.02607],"force_p95":0.06929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08733,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02077,0.02428]}],"total_contact_groups":10},"final_pose_error":0.26303,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5341,-0.00983,0.21111],"final_tcp_position":[0.52055,-0.00887,0.23575],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.74064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":528.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52668,-0.01653,0.24615],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2692.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_to_grasp","tcp_end":[0.53151,-0.02092,0.0341],"tcp_start":[0.52668,-0.01653,0.24615],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.02065,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31635,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1347,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.18223,"tcp_end":[0.52286,-0.02077,0.02424],"tcp_start":[0.53151,-0.02092,0.0341],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.54071,-0.02072,0.16958],"object_pos_start":[0.53687,-0.02065,0.02582],"object_to_goal_dist_end":0.2608,"object_to_goal_dist_start":0.31635,"object_z_max":0.16934,"peak_contact_force":0.11233,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14224.0,"raw_peak_contact_force":0.74064,"subtask_id":"lift_object","tcp_end":[0.51925,-0.02068,0.17839],"tcp_start":[0.52286,-0.02077,0.02424],"tcp_to_object_dist_end":0.02319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.5341,-0.00983,0.21111],"object_pos_start":[0.54071,-0.02072,0.16958],"object_to_goal_dist_end":0.24953,"object_to_goal_dist_start":0.2608,"object_z_max":0.21128,"peak_contact_force":0.01017,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3879.0,"raw_peak_contact_force":0.25599,"subtask_id":"approach_goal","tcp_end":[0.52055,-0.00887,0.23575],"tcp_start":[0.51925,-0.02068,0.17839],"tcp_to_object_dist_end":0.02814,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18957,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.24958,"approach_goal.transport_speed":0.03021,"approach_object.approach_arc_height":0.14857,"approach_object.approach_speed":0.19501,"descend_to_grasp.descend_speed":0.04594,"descend_to_place.descend_place_speed":0.02564,"lift.lift_height":0.14289,"release.release_time":0.24337},"optimized_scores":{"best_composite_score":0.10187,"best_fitness_score":0.65187,"best_task_score":0.34915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54218,-0.02858,-0.00138],"force_p95":0.69617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74839,"mean_force":0.16347,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53,-0.02847,0.02529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5752.0,"contact_point_centroid":[0.53042,-0.00949,0.08087],"force_p95":0.11228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34127,"mean_force":0.07501,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52731,-0.02838,0.07854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6250.0,"contact_point_centroid":[0.5305,-0.04717,0.07893],"force_p95":0.10783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32182,"mean_force":0.07037,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52734,-0.02838,0.07725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.54068,0.01173,0.2017],"force_p95":0.15581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23135,"mean_force":0.09958,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5363,-0.00665,0.20299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5082.0,"contact_point_centroid":[0.54081,-0.02514,0.20082],"force_p95":0.14207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20559,"mean_force":0.09692,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53625,-0.00681,0.20221]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02898,-0.00206],"force_p95":0.14173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19733,"mean_force":0.12802,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53257,-0.02855,0.02544]},{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.5456,-0.02923,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12343,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51939,-0.01312,0.27725]},{"body_a":"world","body_b":"grasp_target","contact_count":2752.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53683,-0.02666,0.13851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.53227,-0.00932,0.02673],"force_p95":0.07793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12239,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53132,-0.02852,0.02399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.53223,-0.04762,0.02578],"force_p95":0.06992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08744,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53132,-0.02852,0.024]}],"total_contact_groups":10},"final_pose_error":0.15307,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56891,0.03133,0.23149],"final_tcp_position":[0.55817,0.03286,0.2566],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":604.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53629,-0.02463,0.24673],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2752.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_to_grasp","tcp_end":[0.54005,-0.02877,0.03414],"tcp_start":[0.53629,-0.02463,0.24673],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54545,-0.02841,0.02578],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2605,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1373,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.19733,"tcp_end":[0.53129,-0.02851,0.02396],"tcp_start":[0.54005,-0.02877,0.03414],"tcp_to_object_dist_end":0.01428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":413.0,"n_steps_budget":900.0,"object_pos_end":[0.54816,-0.02828,0.14162],"object_pos_start":[0.54545,-0.02841,0.02578],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.2605,"object_z_max":0.14138,"peak_contact_force":1573.09317,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12080.0,"raw_peak_contact_force":0.74839,"subtask_id":"lift_object","tcp_end":[0.52737,-0.02837,0.1475],"tcp_start":[0.53129,-0.02851,0.02396],"tcp_to_object_dist_end":0.0216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.56891,0.03133,0.23149],"object_pos_start":[0.54816,-0.02828,0.14162],"object_to_goal_dist_end":0.15784,"object_to_goal_dist_start":0.21388,"object_z_max":0.23242,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9957.0,"raw_peak_contact_force":0.23135,"subtask_id":"approach_goal","tcp_end":[0.55817,0.03286,0.2566],"tcp_start":[0.52737,-0.02837,0.1475],"tcp_to_object_dist_end":0.02736,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```