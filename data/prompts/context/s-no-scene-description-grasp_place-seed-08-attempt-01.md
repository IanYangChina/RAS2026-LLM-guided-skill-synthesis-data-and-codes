## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0732 | 0.20 | ✅ accepted |
| 0 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.073) — your mutation base

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
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: position_control
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
    approach_arc_height:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
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
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
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

- **Composite score**: 0.073
- **task_score** (E): 0.197
- **fitness_score**: 0.573  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1586 |
| descend_to_grasp | 1.00 | 1.00 | 0.1097 |
| grasp | 1.00 | 1.00 | 0.0123 |
| lift | 1.00 | 1.00 | 0.1043 |
| approach_goal | 1.00 | 1.00 | 0.2720 |
| descend_to_place | 1.00 | 1.00 | 0.0797 |
| release | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.000, 0.038) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.000, 0.038)→(0.508, -0.000, 0.029) | (0.522, -0.001, 0.026)→(0.522, -0.000, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.149 | 0.232 |
| lift | lift | 1.00 / step_budget | (0.508, -0.000, 0.029)→(0.504, -0.001, 0.133) | (0.522, -0.000, 0.026)→(0.522, -0.001, 0.125) | 0.289→0.241 | 1.00 / 22.667 | 0.112 | 0.655 |
| approach_goal | approach | 1.00 / step_budget | (0.504, -0.001, 0.133)→(0.600, 0.195, 0.292) | (0.522, -0.001, 0.125)→(0.539, 0.071, 0.016) | 0.241→0.245 | 1.00 / 8.667 | 91004.502 | 1.784 |
| descend_to_place | descend | 1.00 / step_budget | (0.600, 0.195, 0.292)→(0.604, 0.204, 0.213) | (0.539, 0.071, 0.016)→(0.539, 0.071, 0.016) | 0.245→0.245 | 1.00 / 8.333 | 91002.236 | 0.123 |
| release | release | 1.00 / step_budget | (0.604, 0.204, 0.213)→(0.599, 0.202, 0.232) | (0.539, 0.071, 0.016)→(0.539, 0.071, 0.016) | 0.245→0.245 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.230
- phase_score: 0.727
- phase_breakdown.lift_object_score: 0.587
- phase_breakdown.grasp_contact_score: 0.747
- phase_breakdown.approach_goal_score: 0.671
- phase_breakdown.approach_object_score: 0.674
- phase_breakdown.final_placement_score: 0.823
- grasp_place_fitness: 0.588

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.588
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.230
- **Median Q (composite search score)**: 0.070
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59204,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_arc_height":0.02389,"approach_object.approach_speed":0.16531,"descend_to_grasp.descend_speed":0.04773,"descend_to_grasp.force_limit":16.39354,"descend_to_place.descend_place_speed":0.04795,"lift.lift_height":0.11425,"release.release_time":0.6701},"optimized_scores":{"best_composite_score":0.07041,"best_fitness_score":0.57041,"best_task_score":0.18462},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2158.0,"contact_point_centroid":[0.50269,0.11992,-0.00247],"force_p95":0.16934,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81684,"mean_force":0.15134,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53671,0.1609,0.26943]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.47944,0.04635,-0.00147],"force_p95":0.80049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8425,"mean_force":0.20308,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46892,0.04697,0.02103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3449.0,"contact_point_centroid":[0.48237,0.04883,0.15135],"force_p95":0.17439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35291,"mean_force":0.09909,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4767,0.06722,0.15118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5412.0,"contact_point_centroid":[0.46805,0.06579,0.06393],"force_p95":0.09865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31673,"mean_force":0.05834,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46664,0.04674,0.06204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3144.0,"contact_point_centroid":[0.48239,0.0863,0.1522],"force_p95":0.18083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31567,"mean_force":0.10698,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47697,0.06765,0.15187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.46803,0.02767,0.06563],"force_p95":0.10257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29651,"mean_force":0.06172,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46665,0.04674,0.06308]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04833,-0.00215],"force_p95":0.16552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2688,"mean_force":0.13472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47132,0.04723,0.02073]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49077,0.02001,0.22567]},{"body_a":"world","body_b":"grasp_target","contact_count":3092.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47832,0.04472,0.08398]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.50178,0.12018,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57495,0.22118,0.27817]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50178,0.12018,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57433,0.22408,0.23898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.47004,0.02788,0.0227],"force_p95":0.07124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10791,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47018,0.04711,0.01959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5527.0,"contact_point_centroid":[0.46984,0.06647,0.02199],"force_p95":0.07005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08548,"mean_force":0.04139,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47018,0.04711,0.0196]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2099.0,"contact_point_centroid":[0.54017,0.16553,0.27638],"force_p95":0.01161,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53969,0.16551,0.27414]},{"body_a":"left_finger","body_b":"right_finger","contact_count":983.0,"contact_point_centroid":[0.57555,0.22119,0.28042],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57494,0.22116,0.2783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57701,0.22506,0.23713],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57626,0.22502,0.23501]}],"total_contact_groups":16},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50178,0.12018,0.01602],"final_tcp_position":[0.57762,0.22552,0.23861],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.81684,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48202,0.04156,0.14864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3092.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47797,0.04789,0.02739],"tcp_start":[0.48202,0.04156,0.14864],"tcp_to_object_dist_end":0.00499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48255,0.04711,0.0255],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2914,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15729,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12306.0,"raw_peak_contact_force":0.2688,"tcp_end":[0.47015,0.0471,0.01956],"tcp_start":[0.47797,0.04789,0.02739],"tcp_to_object_dist_end":0.01375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":291.0,"n_steps_budget":720.0,"object_pos_end":[0.48553,0.04676,0.11686],"object_pos_start":[0.48255,0.04711,0.0255],"object_to_goal_dist_end":0.23527,"object_to_goal_dist_start":0.2914,"object_z_max":0.11658,"peak_contact_force":0.10927,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10475.0,"raw_peak_contact_force":0.8425,"subtask_id":"lift_object","tcp_end":[0.46638,0.04671,0.11425],"tcp_start":[0.47015,0.0471,0.01956],"tcp_to_object_dist_end":0.01933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.50178,0.12018,0.01602],"object_pos_start":[0.48553,0.04676,0.11686],"object_to_goal_dist_end":0.25342,"object_to_goal_dist_start":0.23527,"object_z_max":0.17336,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10850.0,"raw_peak_contact_force":1.81684,"subtask_id":"approach_goal","tcp_end":[0.57368,0.21773,0.31626],"tcp_start":[0.46638,0.04671,0.11425],"tcp_to_object_dist_end":0.32378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.50178,0.12018,0.01602],"object_pos_start":[0.50178,0.12018,0.01602],"object_to_goal_dist_end":0.25342,"object_to_goal_dist_start":0.25342,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1899.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.57762,0.22552,0.23861],"tcp_start":[0.57368,0.21773,0.31626],"tcp_to_object_dist_end":0.25767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50178,0.12018,0.01602],"object_pos_start":[0.50178,0.12018,0.01602],"object_to_goal_dist_end":0.25342,"object_to_goal_dist_start":0.25342,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57324,0.22352,0.2587],"tcp_start":[0.57762,0.22552,0.23861],"tcp_to_object_dist_end":0.27328,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52885,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_arc_height":0.02159,"approach_object.approach_speed":0.13753,"descend_to_grasp.descend_speed":0.07579,"descend_to_grasp.force_limit":16.05074,"descend_to_place.descend_place_speed":0.02931,"lift.lift_height":0.12186,"release.release_time":0.33468},"optimized_scores":{"best_composite_score":0.061,"best_fitness_score":0.561,"best_task_score":0.1762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2657.0,"contact_point_centroid":[0.55383,0.06045,-0.00235],"force_p95":0.12975,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70064,"mean_force":0.14054,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57001,0.12633,0.25089]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.53419,-0.02,-0.00137],"force_p95":0.51552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54846,"mean_force":0.11594,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52083,-0.02044,0.03592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4684.0,"contact_point_centroid":[0.52151,-0.00149,0.08193],"force_p95":0.11156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32732,"mean_force":0.07619,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51833,-0.02038,0.07952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5113.0,"contact_point_centroid":[0.52162,-0.03915,0.08026],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30461,"mean_force":0.07151,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51836,-0.02038,0.07857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2094.0,"contact_point_centroid":[0.529,-0.01837,0.15563],"force_p95":0.17952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26518,"mean_force":0.09954,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52307,0.00012,0.15549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.52943,0.01969,0.15649],"force_p95":0.17127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26223,"mean_force":0.09639,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52336,0.00121,0.15647]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02113,-0.00208],"force_p95":0.14563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20423,"mean_force":0.12881,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5234,-0.02049,0.03598]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51325,-0.00883,0.22481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.52331,-0.00126,0.03727],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1331,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52217,-0.02046,0.03457]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52831,-0.01971,0.08123]},{"body_a":"world","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.55374,0.06045,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.604,0.21862,0.25555]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55374,0.06045,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60235,0.22242,0.21495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4938.0,"contact_point_centroid":[0.52326,-0.03957,0.03636],"force_p95":0.07065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08168,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52217,-0.02046,0.03458]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2559.0,"contact_point_centroid":[0.57335,0.13399,0.25808],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.01061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57293,0.13398,0.25582]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.60533,0.22343,0.21345],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6045,0.22341,0.21142]},{"body_a":"left_finger","body_b":"right_finger","contact_count":992.0,"contact_point_centroid":[0.60449,0.21866,0.25761],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60401,0.21864,0.25537]}],"total_contact_groups":16},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55374,0.06045,0.01602],"final_tcp_position":[0.60602,0.2239,0.21536],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.46228,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52853,-0.01826,0.14783],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53042,-0.02062,0.0441],"tcp_start":[0.52853,-0.01826,0.14783],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02047,0.02573],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31624,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14112,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10829.0,"raw_peak_contact_force":0.20423,"tcp_end":[0.52214,-0.02046,0.03454],"tcp_start":[0.53042,-0.02062,0.0441],"tcp_to_object_dist_end":0.01721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":341.0,"n_steps_budget":780.0,"object_pos_end":[0.53584,-0.02037,0.12286],"object_pos_start":[0.53693,-0.02047,0.02573],"object_to_goal_dist_end":0.27251,"object_to_goal_dist_start":0.31624,"object_z_max":0.12261,"peak_contact_force":0.11495,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9876.0,"raw_peak_contact_force":0.54846,"subtask_id":"lift_object","tcp_end":[0.51817,-0.02037,0.13703],"tcp_start":[0.52214,-0.02046,0.03454],"tcp_to_object_dist_end":0.02265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.55374,0.06045,0.01602],"object_pos_start":[0.53584,-0.02037,0.12286],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.27251,"object_z_max":0.15697,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9462.0,"raw_peak_contact_force":1.70064,"subtask_id":"approach_goal","tcp_end":[0.60353,0.21436,0.2943],"tcp_start":[0.51817,-0.02037,0.13703],"tcp_to_object_dist_end":0.32188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.55374,0.06045,0.01602],"object_pos_start":[0.55374,0.06045,0.01602],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.26042,"object_z_max":0.01602,"peak_contact_force":273006.46228,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.60602,0.2239,0.21536],"tcp_start":[0.60353,0.21436,0.2943],"tcp_to_object_dist_end":0.26303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55374,0.06045,0.01602],"object_pos_start":[0.55374,0.06045,0.01602],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.26042,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60112,0.22184,0.23433],"tcp_start":[0.60602,0.2239,0.21536],"tcp_to_object_dist_end":0.27559,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_arc_height":0.02275,"approach_object.approach_speed":0.15049,"descend_to_grasp.descend_speed":0.08964,"descend_to_grasp.force_limit":13.58417,"descend_to_place.descend_place_speed":0.04229,"lift.lift_height":0.13491,"release.release_time":0.35515},"optimized_scores":{"best_composite_score":0.08828,"best_fitness_score":0.58828,"best_task_score":0.22953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2126.0,"contact_point_centroid":[0.5625,0.0312,-0.00244],"force_p95":0.1827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83546,"mean_force":0.14476,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5854,0.08398,0.2366]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.5425,-0.0275,-0.00144],"force_p95":0.54299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57541,"mean_force":0.12244,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52908,-0.028,0.03436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5129.0,"contact_point_centroid":[0.53009,-0.00906,0.08659],"force_p95":0.11399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32923,"mean_force":0.07833,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52653,-0.02791,0.08424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5556.0,"contact_point_centroid":[0.53018,-0.04666,0.08497],"force_p95":0.10922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31319,"mean_force":0.07409,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52656,-0.02791,0.08325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.53853,0.00554,0.16249],"force_p95":0.19002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30739,"mean_force":0.09871,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53235,-0.01284,0.16312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1531.0,"contact_point_centroid":[0.53795,-0.03227,0.16181],"force_p95":0.19591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26524,"mean_force":0.10565,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53193,-0.01377,0.1622]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.029,-0.00211],"force_p95":0.15417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22279,"mean_force":0.13099,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53169,-0.02808,0.0345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.5317,-0.00884,0.03574],"force_p95":0.07981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14254,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53044,-0.02805,0.03304]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51694,-0.01218,0.22428]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53622,-0.02702,0.08236]},{"body_a":"world","body_b":"grasp_target","contact_count":936.0,"contact_point_centroid":[0.56235,0.03123,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62457,0.15621,0.22522]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56235,0.03123,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62329,0.16028,0.18389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4973.0,"contact_point_centroid":[0.53162,-0.04718,0.03481],"force_p95":0.07212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08204,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53045,-0.02805,0.03305]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2022.0,"contact_point_centroid":[0.58961,0.09104,0.24329],"force_p95":0.01155,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01528,"mean_force":0.01052,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58936,0.09103,0.24092]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1003.0,"contact_point_centroid":[0.62503,0.15624,0.2273],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62458,0.15623,0.22506]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.62671,0.1611,0.18272],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62584,0.16108,0.18039]}],"total_contact_groups":16},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56235,0.03123,0.01602],"final_tcp_position":[0.62758,0.16146,0.18437],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273013.26005,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53612,-0.02518,0.14679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53886,-0.0283,0.04293],"tcp_start":[0.53612,-0.02518,0.14679],"tcp_to_object_dist_end":0.01822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02811,0.02564],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26034,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14795,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10851.0,"raw_peak_contact_force":0.22279,"tcp_end":[0.53041,-0.02804,0.03301],"tcp_start":[0.53886,-0.0283,0.04293],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":386.0,"n_steps_budget":840.0,"object_pos_end":[0.5446,-0.02792,0.13458],"object_pos_start":[0.54551,-0.02811,0.02564],"object_to_goal_dist_end":0.21627,"object_to_goal_dist_start":0.26034,"object_z_max":0.13433,"peak_contact_force":0.11264,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10763.0,"raw_peak_contact_force":0.57541,"subtask_id":"lift_object","tcp_end":[0.52651,-0.0279,0.14854],"tcp_start":[0.53041,-0.02804,0.03301],"tcp_to_object_dist_end":0.02285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":775.0,"n_steps_budget":1000.0,"object_pos_end":[0.56235,0.03123,0.01602],"object_pos_start":[0.5446,-0.02792,0.13458],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.21627,"object_z_max":0.15854,"peak_contact_force":273013.26005,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7327.0,"raw_peak_contact_force":1.83546,"subtask_id":"approach_goal","tcp_end":[0.62344,0.1518,0.26516],"tcp_start":[0.52651,-0.0279,0.14854],"tcp_to_object_dist_end":0.28345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.56235,0.03123,0.01602],"object_pos_start":[0.56235,0.03123,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1939.0,"raw_peak_contact_force":0.12263,"subtask_id":"final_placement","tcp_end":[0.62758,0.16146,0.18437],"tcp_start":[0.62344,0.1518,0.26516],"tcp_to_object_dist_end":0.22262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56235,0.03123,0.01602],"object_pos_start":[0.56235,0.03123,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62179,0.15979,0.20324],"tcp_start":[0.62758,0.16146,0.18437],"tcp_to_object_dist_end":0.23476,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```