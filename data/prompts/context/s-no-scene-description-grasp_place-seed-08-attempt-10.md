## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1491 | 0.13 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 10 | -0.2072 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0140 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0216 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0817 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.149) — your mutation base

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

- **Composite score**: -0.149
- **task_score** (E): 0.128
- **fitness_score**: 0.151  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1418 |
| descend_to_grasp | 1.00 | 1.00 | 0.0003 |
| grasp | 1.00 | 1.00 | 0.0011 |
| lift | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.452, 0.007, 0.170) | (0.522, -0.001, 0.030)→(0.483, -0.001, 0.016) | 0.287→0.310 | 1.00 / 5.000 | 300.458 | 1511.186 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.452, 0.007, 0.170)→(0.452, 0.008, 0.170) | (0.483, -0.001, 0.016)→(0.483, -0.001, 0.016) | 0.310→0.310 | 1.00 / 5.000 | 421.457 | 397.332 |
| grasp | grasp | 1.00 / step_budget | (0.452, 0.008, 0.170)→(0.452, 0.008, 0.169) | (0.483, -0.001, 0.016)→(0.483, -0.001, 0.016) | 0.310→0.310 | 1.00 / 9.333 | 68.004 | 202.386 |
| lift | lift | 0.00 / guard_failure | (0.452, 0.008, 0.169)→(0.452, 0.008, 0.169) | (0.483, -0.001, 0.016)→(0.483, -0.001, 0.016) | 0.310→0.310 | 1.00 / 9.000 | 75.067 | 74.323 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.153
- phase_score: 0.061
- phase_breakdown.lift_object_score: 0.162
- phase_breakdown.grasp_contact_score: 0.043
- phase_breakdown.approach_goal_score: 0.000
- phase_breakdown.approach_object_score: 0.161
- phase_breakdown.final_placement_score: 0.000
- grasp_place_fitness: 0.166

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.166
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.153
- **Median Q (composite search score)**: -0.156
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.78261,"average_solve_count":23.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.22195,"approach_goal.transport_speed":0.08201,"approach_object.approach_speed":0.11974,"descend_to_grasp.contact_force_threshold":7.68006,"descend_to_grasp.descend_speed":0.05825,"descend_to_place.descend_place_speed":0.06338,"lift.lift_height":0.1792,"release.release_time":0.72046},"optimized_scores":{"best_composite_score":-0.15786,"best_fitness_score":0.14214,"best_task_score":0.12518},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63774,0.01385,-0.00045],"force_p95":223.00059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1519.77783,"mean_force":210.64077,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40422,0.01313,0.1338]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53007,0.01102,-0.00361],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.07826,"mean_force":12.83659,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37889,0.00616,0.04648]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62665,0.02662,-0.00024],"force_p95":303.21806,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.21806,"mean_force":303.21806,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42637,0.02525,0.1852]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.627,0.0277,-0.00013],"force_p95":78.77929,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.71897,"mean_force":74.36968,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42667,0.0259,0.18537]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62715,0.02768,-0.00013],"force_p95":83.6766,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.6766,"mean_force":83.6766,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.42672,0.02589,0.18525]},{"body_a":"grasp_target","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.4599,0.0445,0.03899],"force_p95":3.64086,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.98854,"mean_force":1.68796,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38889,0.00622,0.04952]},{"body_a":"world","body_b":"grasp_target","contact_count":3922.0,"contact_point_centroid":[0.44749,0.05038,-0.00214],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42804,"mean_force":0.13835,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41516,0.01229,0.14275]},{"body_a":"grasp_target","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.49038,0.02918,0.00936],"force_p95":0.75146,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.75807,"mean_force":0.34062,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37864,0.00616,0.04762]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44261,0.05061,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42637,0.02525,0.1852]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.44261,0.05061,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42667,0.0259,0.18537]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.44261,0.05061,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.42672,0.02589,0.18525]},{"body_a":"left_finger","body_b":"right_finger","contact_count":333.0,"contact_point_centroid":[0.42843,0.0259,0.18391],"force_p95":0.01423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01134,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42672,0.02589,0.18526]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.43081,0.02589,0.18448],"force_p95":0.00958,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00958,"mean_force":0.00958,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.42672,0.02589,0.18525]}],"total_contact_groups":13},"final_pose_error":0.1792,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44261,0.05061,0.01602],"final_tcp_position":[0.42672,0.02589,0.18525],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1519.77783,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.05061,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.3117,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":216.63219,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4900.0,"raw_peak_contact_force":1519.77783,"subtask_id":"approach_object","tcp_end":[0.42637,0.02525,0.1852],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17184,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.05061,0.01602],"object_pos_start":[0.44261,0.05061,0.01602],"object_to_goal_dist_end":0.3117,"object_to_goal_dist_start":0.3117,"object_z_max":0.01602,"peak_contact_force":375.59301,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":303.21806,"subtask_id":"grasp_contact","tcp_end":[0.42642,0.02527,0.18539],"tcp_start":[0.42637,0.02525,0.1852],"tcp_to_object_dist_end":0.17202,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44261,0.05061,0.01602],"object_pos_start":[0.44261,0.05061,0.01602],"object_to_goal_dist_end":0.3117,"object_to_goal_dist_start":0.3117,"object_z_max":0.01602,"peak_contact_force":71.24986,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2583.0,"raw_peak_contact_force":186.71897,"tcp_end":[0.42672,0.02589,0.18525],"tcp_start":[0.42642,0.02527,0.18539],"tcp_to_object_dist_end":0.17177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.05061,0.01602],"object_pos_start":[0.44261,0.05061,0.01602],"object_to_goal_dist_end":0.3117,"object_to_goal_dist_start":0.3117,"object_z_max":0.01602,"peak_contact_force":85.90736,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10.0,"raw_peak_contact_force":83.6766,"subtask_id":"lift_object","tcp_end":[0.42672,0.02589,0.18525],"tcp_start":[0.42672,0.02589,0.18525],"tcp_to_object_dist_end":0.17177,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.36364,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.1452,"approach_goal.transport_speed":0.0802,"approach_object.approach_speed":0.14452,"descend_to_grasp.contact_force_threshold":15.01142,"descend_to_grasp.descend_speed":0.05649,"descend_to_place.descend_place_speed":0.04611,"lift.lift_height":0.19412,"release.release_time":0.35301},"optimized_scores":{"best_composite_score":-0.15597,"best_fitness_score":0.14403,"best_task_score":0.10661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":862.0,"contact_point_centroid":[0.64958,-0.00584,-0.00043],"force_p95":437.69048,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1513.51257,"mean_force":238.10108,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4291,-0.00646,0.15509]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53782,0.00058,-0.00391],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":399.25874,"mean_force":18.14812,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38536,-0.00284,0.04664]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68192,-0.02533,-0.00023],"force_p95":252.95906,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.95906,"mean_force":252.95906,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4641,-0.00029,0.16237]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.68247,-0.02505,-0.00012],"force_p95":71.11754,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.77368,"mean_force":68.3979,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46417,0.00025,0.16191]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68255,-0.02509,-0.00012],"force_p95":69.95251,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.95251,"mean_force":69.95251,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46415,0.0002,0.16178]},{"body_a":"grasp_target","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.50821,-0.02344,0.03775],"force_p95":3.78292,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.18766,"mean_force":0.9267,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39718,-0.00299,0.08854]},{"body_a":"grasp_target","body_b":"hand","contact_count":135.0,"contact_point_centroid":[0.50009,-0.02833,0.04979],"force_p95":2.30272,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.0391,"mean_force":0.92921,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39629,-0.00296,0.08595]},{"body_a":"world","body_b":"grasp_target","contact_count":3702.0,"contact_point_centroid":[0.5061,-0.02445,-0.00223],"force_p95":0.25599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33997,"mean_force":0.15431,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44121,-0.00626,0.1659]},{"body_a":"grasp_target","body_b":"link6","contact_count":119.0,"contact_point_centroid":[0.54575,-0.02376,0.02518],"force_p95":0.76019,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.82745,"mean_force":0.3838,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39438,-0.00298,0.09006]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49941,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4641,-0.00029,0.16237]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.49941,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46417,0.00025,0.16191]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49941,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46415,0.0002,0.16178]},{"body_a":"left_finger","body_b":"right_finger","contact_count":349.0,"contact_point_centroid":[0.46619,1e-05,0.16059],"force_p95":0.01346,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01089,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46415,0.0002,0.16178]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.46599,2e-05,0.16078],"force_p95":0.01074,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01074,"mean_force":0.01074,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46415,0.0002,0.16178]}],"total_contact_groups":14},"final_pose_error":0.19412,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49941,-0.02488,0.01602],"final_tcp_position":[0.46415,0.0002,0.16177],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1513.51257,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49941,-0.02488,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33579,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":267.02725,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4990.0,"raw_peak_contact_force":1513.51257,"subtask_id":"approach_object","tcp_end":[0.4641,-0.00029,0.16237],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15255,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49941,-0.02488,0.01602],"object_pos_start":[0.49941,-0.02488,0.01602],"object_to_goal_dist_end":0.33579,"object_to_goal_dist_start":0.33579,"object_z_max":0.01602,"peak_contact_force":252.95906,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":252.95906,"subtask_id":"grasp_contact","tcp_end":[0.46411,-0.0001,0.16234],"tcp_start":[0.4641,-0.00029,0.16237],"tcp_to_object_dist_end":0.15255,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49941,-0.02488,0.01602],"object_pos_start":[0.49941,-0.02488,0.01602],"object_to_goal_dist_end":0.33579,"object_to_goal_dist_start":0.33579,"object_z_max":0.01602,"peak_contact_force":66.55926,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2599.0,"raw_peak_contact_force":194.77368,"tcp_end":[0.46415,0.0002,0.16178],"tcp_start":[0.46411,-0.0001,0.16234],"tcp_to_object_dist_end":0.15204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49941,-0.02488,0.01602],"object_pos_start":[0.49941,-0.02488,0.01602],"object_to_goal_dist_end":0.33579,"object_to_goal_dist_start":0.33579,"object_z_max":0.01602,"peak_contact_force":69.95251,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9.0,"raw_peak_contact_force":69.95251,"subtask_id":"lift_object","tcp_end":[0.46415,0.0002,0.16177],"tcp_start":[0.46415,0.0002,0.16178],"tcp_to_object_dist_end":0.15204,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":9.40909,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_arc_height":0.16398,"approach_goal.transport_speed":0.08426,"approach_object.approach_speed":0.138,"descend_to_grasp.contact_force_threshold":8.97109,"descend_to_grasp.descend_speed":0.03895,"descend_to_place.descend_place_speed":0.06048,"lift.lift_height":0.18593,"release.release_time":0.65519},"optimized_scores":{"best_composite_score":-0.13351,"best_fitness_score":0.16649,"best_task_score":0.15273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":860.0,"contact_point_centroid":[0.65048,-0.00799,-0.00042],"force_p95":439.99662,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1500.26811,"mean_force":244.08655,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43012,-0.00873,0.15501]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68887,-0.01954,-9e-05],"force_p95":635.81894,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":635.81894,"mean_force":635.81894,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46416,-0.00276,0.16212]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53876,-0.00041,-0.00373],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.55791,"mean_force":18.07081,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3862,-0.00367,0.04673]},{"body_a":"world","body_b":"link6","contact_count":447.0,"contact_point_centroid":[0.68296,-0.03288,-0.00012],"force_p95":72.30256,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.66587,"mean_force":68.97509,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46428,-0.00129,0.16033]},{"body_a":"link5","body_b":"hand","contact_count":64.0,"contact_point_centroid":[0.54594,0.06766,0.17104],"force_p95":123.13248,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.87287,"mean_force":27.36616,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46453,-0.00107,0.16079]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.683,-0.03299,-0.00012],"force_p95":69.33987,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.33987,"mean_force":69.33987,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46425,-0.00136,0.16019]},{"body_a":"grasp_target","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.51925,-0.0262,0.03735],"force_p95":3.19404,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.60182,"mean_force":0.72463,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40058,-0.00407,0.09682]},{"body_a":"grasp_target","body_b":"link6","contact_count":134.0,"contact_point_centroid":[0.54835,-0.01486,0.0256],"force_p95":0.70898,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.64645,"mean_force":0.41118,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39599,-0.00391,0.09123]},{"body_a":"grasp_target","body_b":"hand","contact_count":131.0,"contact_point_centroid":[0.50171,-0.03481,0.04885],"force_p95":2.38267,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.11503,"mean_force":0.97458,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39687,-0.00385,0.08469]},{"body_a":"world","body_b":"grasp_target","contact_count":3630.0,"contact_point_centroid":[0.5134,-0.02923,-0.00222],"force_p95":0.30571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90289,"mean_force":0.15419,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44313,-0.0086,0.16735]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50724,-0.02945,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46416,-0.00276,0.16212]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50724,-0.02945,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46428,-0.00129,0.16033]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50724,-0.02945,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46425,-0.00136,0.16019]},{"body_a":"left_finger","body_b":"right_finger","contact_count":356.0,"contact_point_centroid":[0.4661,-0.00148,0.15879],"force_p95":0.01338,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.0107,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46425,-0.00135,0.16019]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.46609,-0.00158,0.1592],"force_p95":0.01072,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01072,"mean_force":0.01072,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46425,-0.00136,0.16019]}],"total_contact_groups":15},"final_pose_error":0.18594,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50724,-0.02945,0.01602],"final_tcp_position":[0.46425,-0.00136,0.16019],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1500.26811,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50724,-0.02945,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28187,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":417.71414,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4977.0,"raw_peak_contact_force":1500.26811,"subtask_id":"approach_object","tcp_end":[0.46416,-0.00276,0.16212],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15464,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50724,-0.02945,0.01602],"object_pos_start":[0.50724,-0.02945,0.01602],"object_to_goal_dist_end":0.28187,"object_to_goal_dist_start":0.28187,"object_z_max":0.01602,"peak_contact_force":635.81894,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":635.81894,"subtask_id":"grasp_contact","tcp_end":[0.46418,-0.00249,0.16182],"tcp_start":[0.46416,-0.00276,0.16212],"tcp_to_object_dist_end":0.1544,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50724,-0.02945,0.01602],"object_pos_start":[0.50724,-0.02945,0.01602],"object_to_goal_dist_end":0.28187,"object_to_goal_dist_start":0.28187,"object_z_max":0.01602,"peak_contact_force":66.20212,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2667.0,"raw_peak_contact_force":225.66587,"tcp_end":[0.46425,-0.00136,0.16019],"tcp_start":[0.46418,-0.00249,0.16182],"tcp_to_object_dist_end":0.15304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50724,-0.02945,0.01602],"object_pos_start":[0.50724,-0.02945,0.01602],"object_to_goal_dist_end":0.28187,"object_to_goal_dist_start":0.28187,"object_z_max":0.01602,"peak_contact_force":69.33987,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9.0,"raw_peak_contact_force":69.33987,"subtask_id":"lift_object","tcp_end":[0.46425,-0.00136,0.16019],"tcp_start":[0.46425,-0.00136,0.16019],"tcp_to_object_dist_end":0.15304,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```